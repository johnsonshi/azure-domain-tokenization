"""Resumable pipeline orchestration (plan.md §20-22).

Stages: acquire -> audit -> train -> evaluate -> benchmark -> analyze -> report,
each idempotent and content-hashed. Corpus/audit build the byte-matched
General/Azure/Mixed corpora with leakage controls; train builds the controlled
byte-level BPE tokenizers; evaluate/analyze produce the raw + processed results.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import yaml

from . import config, corpus, evaluate, sampling, splitting, train
from .acquire import write_sources_lock
from .corpus import RawDoc
from .provenance import atomic_write_json, atomic_write_text, sha256_text
from .schemas import SourceLock
from .sources import acquire_source, load_sources_config
from .staging import stage

# --------------------------------------------------------------------------- #
# Profiles + experiment config
# --------------------------------------------------------------------------- #
PROFILE_BYTES = {"pilot": config.PILOT_CORPUS_BYTES, "full": config.FULL_CORPUS_BYTES}
PROFILE_VOCABS = {"pilot": (config.VOCAB_SIZE_PILOT,), "full": config.VOCAB_SIZES_REQUIRED}


def load_experiment(path: str | Path | None = None) -> dict:
    path = Path(path) if path else (config.CONFIGS / "experiment.yaml")
    if path.exists():
        return yaml.safe_load(path.read_text())
    return {}


def _profile_bytes(profile: str) -> int:
    p = (load_experiment().get("profiles") or {}).get(profile) or {}
    return int(p.get("corpus_bytes", PROFILE_BYTES.get(profile, config.PILOT_CORPUS_BYTES)))


def _profile_vocabs(profile: str) -> tuple[int, ...]:
    p = (load_experiment().get("profiles") or {}).get(profile) or {}
    return tuple(p.get("vocab_sizes", PROFILE_VOCABS.get(profile, (config.VOCAB_SIZE_PILOT,))))


def _log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} {msg}"
    print(line, file=__import__("sys").stderr, flush=True)
    config.LOGS.mkdir(parents=True, exist_ok=True)
    with open(config.LOGS / "pipeline.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


# --------------------------------------------------------------------------- #
# ACQUIRE
# --------------------------------------------------------------------------- #
def _raw_parquet(name: str) -> Path:
    return config.RAW / f"{name}.raw.parquet"


def _lock_json(name: str) -> Path:
    return config.MANIFESTS / "locks" / f"{name}.json"


def run_acquire(profile: str, sources_cfg: str | Path, force: bool = False) -> dict:
    specs = load_sources_config(sources_cfg)
    results = {}
    for spec in specs:
        out_parquet = _raw_parquet(spec.name)
        lock_path = _lock_json(spec.name)

        def work(spec=spec, out_parquet=out_parquet, lock_path=lock_path):
            _log(f"acquire: {spec.name} (role={spec.role})")
            raw_docs, lock = acquire_source(spec)
            rows = [{
                "source_repo": rd.source_repo,
                "source_commit": rd.source_commit,
                "source_path": rd.source_path,
                "license_id": rd.license_id,
                "role": spec.role,
                "source_name": spec.name,
                "eval_category": spec.eval_category,
                "raw_text": rd.raw_bytes.decode("utf-8", errors="replace"),
            } for rd in raw_docs]
            out_parquet.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_parquet(out_parquet)
            atomic_write_json(lock_path, lock.model_dump())
            _log(f"acquire: {spec.name} -> {len(rows)} docs, {lock.source_bytes} src bytes")

        res = stage(
            name=f"acquire-{profile}:{spec.name}",
            input_files=[sources_cfg],
            output_files=[out_parquet, lock_path],
            params={"role": spec.role, "paths": spec.paths, "max_docs": spec.max_docs,
                    "hf_files": spec.hf_files, "method": spec.method},
            fn=work, force=force,
        )
        results[spec.name] = {"skipped": res.skipped}

    # Aggregate sources.lock.json from per-source locks
    locks = [SourceLock(**json.loads(_lock_json(s.name).read_text())) for s in specs
             if _lock_json(s.name).exists()]
    write_sources_lock(locks)
    return {"sources": results, "n_sources": len(specs)}


# --------------------------------------------------------------------------- #
# AUDIT (process, dedupe, split, build byte-matched corpora)
# --------------------------------------------------------------------------- #
def _load_raw(role: str | None = None) -> list[RawDoc]:
    docs: list[RawDoc] = []
    for pq in sorted(config.RAW.glob("*.raw.parquet")):
        df = pd.read_parquet(pq)
        if role is not None:
            df = df[df["role"] == role]
        for _, r in df.iterrows():
            docs.append(RawDoc(
                source_repo=r["source_repo"], source_commit=r["source_commit"],
                source_path=r["source_path"], license_id=r["license_id"],
                raw_bytes=str(r["raw_text"]).encode("utf-8"),
            ))
    return docs


def _role_of(pq_name: str) -> str:
    return pq_name


def run_audit(profile: str, exp: dict, force: bool = False) -> dict:
    target_bytes = _profile_bytes(profile)
    seed = config.GLOBAL_SEED
    near_thr = float(exp.get("near_dup_threshold", 0.8))

    out_corpora = [config.SPLITS / f"{c}.corpus.txt" for c in ("general", "azure", "mixed")]
    out_audit = config.AUDIT / "audit_summary.json"
    out_splits = config.SPLITS / "azure_splits.parquet"
    out_segments = config.SEGMENTS / "segments.sample.parquet"
    out_eval = config.EVALUATION / "eval_docs.parquet"
    out_dedup = config.AUDIT / "cross_repo_overlap.parquet"

    def work():
        _log(f"audit: profile={profile} target_bytes={target_bytes}")
        # Load by role; also build source_repo -> friendly eval category map
        raw_by_role: dict[str, list[RawDoc]] = {}
        repo_to_category: dict[str, str] = {}
        for pq in sorted(config.RAW.glob("*.raw.parquet")):
            df = pd.read_parquet(pq)
            if "eval_category" in df.columns:
                for repo, cat in df[["source_repo", "eval_category"]].dropna().itertuples(index=False):
                    if cat:
                        repo_to_category[repo] = cat
            for role, g in df.groupby("role"):
                lst = raw_by_role.setdefault(role, [])
                for _, r in g.iterrows():
                    lst.append(RawDoc(r["source_repo"], r["source_commit"], r["source_path"],
                                      r["license_id"], str(r["raw_text"]).encode("utf-8")))

        # Process each role
        processed: dict[str, list] = {}
        norm_reports = {}
        for role, rds in raw_by_role.items():
            rep = corpus.nz.NormalizationReport()
            processed[role] = corpus.process_documents(rds, rep)
            norm_reports[role] = {"total": rep.total, "changed_by_nfc": rep.changed_by_nfc,
                                  "malformed": rep.malformed, "empty": rep.empty}
            _log(f"audit: processed role={role}: {len(processed[role])} docs")

        # Segments sample (schema demo + provenance) from anchor
        anchor_raw = raw_by_role.get("anchor", [])[:400]
        if anchor_raw:
            seg_df = corpus.segments_dataframe(anchor_raw)
            out_segments.parent.mkdir(parents=True, exist_ok=True)
            seg_df.to_parquet(out_segments)

        # Exact + near-dup within anchor (azure). Near-duplicates are REMOVED
        # (one representative kept) so genuine cross-service duplicates cannot
        # bridge services in the split (plan.md §11).
        azure_docs = processed.get("anchor", [])
        azure_docs, exact_stats = corpus.exact_dedup(azure_docs)
        near = None
        near_stats = {"removed_near": 0, "input": len(azure_docs), "kept": len(azure_docs), "threshold": near_thr}
        if azure_docs:
            azure_docs, near, near_stats = corpus.near_dedup(azure_docs, threshold=near_thr)
        cluster_of = near.clusters if near else {}

        # Azure group-aware splits (near-dups already removed -> service-granular)
        refs = [splitting.DocumentRef(d.document_id, d.source_repo, d.source_path,
                                      cluster_of.get(d.document_id, -1)) for d in azure_docs]
        asg = splitting.assign_azure_splits(refs, seed=seed)
        violations = splitting.verify_no_cross_split_leakage(refs, asg)
        if violations:
            raise RuntimeError(f"LEAKAGE: {violations[:5]}")

        split_rows = [{"document_id": d.document_id, "source_path": d.source_path,
                       "service": splitting.top_level_service(d.source_path),
                       "cluster_id": cluster_of.get(d.document_id, -1),
                       "split": asg.doc_to_split[d.document_id]} for d in azure_docs]
        out_splits.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(split_rows).to_parquet(out_splits)

        # Build training pools
        azure_train_docs = [d for d in azure_docs if asg.doc_to_split[d.document_id] == "azure_train"]

        # General: exact dedup BEFORE the train/eval split so no identical
        # WikiText content lands on both sides (red-team blocker 1). Near-dup
        # bridging within general is handled by the cross-corpus eval filter below.
        general_all = processed.get("general_english", [])
        general_all, gen_exact_stats = corpus.exact_dedup(general_all)
        gen_near_stats = {"removed_near": 0, "note": "general near-dup handled by cross-corpus eval filter"}
        general_train, _general_eval = _hash_split(general_all, seed, eval_frac=0.15)
        # Guard: no exact content hash shared across general train/eval
        _assert_no_content_leak(general_train, _general_eval, "general")

        azure_pairs = [(d.document_id, d.semantic_full) for d in azure_train_docs]
        general_pairs = [(d.document_id, d.semantic_full) for d in general_train]

        # Cross-corpus exact-leakage guard: no shared semantic hash train<->eval
        _assert_no_train_eval_leak(azure_train_docs, azure_docs, asg)

        azure_sample = sampling.deterministic_sample(azure_pairs, target_bytes, seed, "azure")
        general_sample = sampling.deterministic_sample(general_pairs, target_bytes, seed, "general")
        mix_a, mix_b = sampling.interleave_mixed(azure_pairs, general_pairs, target_bytes,
                                                 seed, "azure", "general")

        config.SPLITS.mkdir(parents=True, exist_ok=True)
        info = {}
        info["azure"] = corpus.build_corpus_file(list(azure_sample.texts.values()),
                                                 config.SPLITS / "azure.corpus.txt")
        info["general"] = corpus.build_corpus_file(list(general_sample.texts.values()),
                                                   config.SPLITS / "general.corpus.txt")
        # True deterministic document-by-document interleaving (plan.md §12)
        a_texts = list(mix_a.texts.values())
        b_texts = list(mix_b.texts.values())
        mixed_texts: list[str] = []
        for i in range(max(len(a_texts), len(b_texts))):
            if i < len(a_texts):
                mixed_texts.append(a_texts[i])
            if i < len(b_texts):
                mixed_texts.append(b_texts[i])
        info["mixed"] = corpus.build_corpus_file(mixed_texts, config.SPLITS / "mixed.corpus.txt")

        # Training pool used for cross-corpus near-dup eval filtering (plan.md §11)
        train_pool = ([(d.document_id, d.semantic_full) for d in azure_train_docs]
                      + [(d.document_id, d.semantic_full) for d in general_train])

        # Build + persist the frozen evaluation document set (plan.md §14),
        # removing eval items that are near-duplicates of any training doc.
        cc_removed = _build_eval_docs(processed, azure_docs, asg, _general_eval,
                                      repo_to_category, train_pool, near_thr)

        # Cross-repo dedup + overlap audit (plan.md §11)
        _write_dedup_audit(processed, azure_docs, near, near_thr)

        # Byte-match gate (plan.md §20 Phase 2)
        contents = {k: v["content_utf8_bytes"] for k, v in info.items()}
        mx_bytes = max(contents.values())
        mn_bytes = min(contents.values())
        byte_match_ok = (mx_bytes - mn_bytes) / mx_bytes <= config.BYTE_MATCH_TOLERANCE if mx_bytes else True

        # Manifests with training_manifest_sha256
        for name, sample_docs in [("azure", azure_sample.docs), ("general", general_sample.docs)]:
            manifest_ids = sorted(d.document_id for d in sample_docs)
            corpus.write_corpus_manifest(name, info[name], {
                "profile": profile, "target_bytes": target_bytes,
                "training_manifest_sha256": sha256_text("|".join(manifest_ids)),
                "n_selected": len(manifest_ids),
            }, config.MANIFESTS)
        mixed_ids = sorted([d.document_id for d in mix_a.docs] + [d.document_id for d in mix_b.docs])
        corpus.write_corpus_manifest("mixed", info["mixed"], {
            "profile": profile, "target_bytes": target_bytes,
            "training_manifest_sha256": sha256_text("|".join(mixed_ids)),
            "n_selected": len(mixed_ids),
            "azure_bytes": mix_a.total_bytes, "general_bytes": mix_b.total_bytes,
        }, config.MANIFESTS)

        summary = {
            "profile": profile, "seed": seed, "target_bytes": target_bytes,
            "normalization": norm_reports,
            "exact_dedup_azure": exact_stats,
            "near_dup_azure": {"threshold": near_thr,
                               "removed_near": near_stats.get("removed_near", 0),
                               "kept_after_near": near_stats.get("kept", 0),
                               "num_pairs": len(near.pairs) if near else 0},
            "exact_dedup_general": gen_exact_stats,
            "near_dup_general": {"removed_near": gen_near_stats.get("removed_near", 0)},
            "cross_corpus_near_dup_eval": cc_removed,
            "azure_splits": asg.stats,
            "leakage_violations": violations,
            "corpora_content_bytes": contents,
            "byte_match_ok": bool(byte_match_ok),
            "byte_match_spread": (mx_bytes - mn_bytes),
            "counts": {r: len(p) for r, p in processed.items()},
        }
        atomic_write_json(out_audit, summary)
        _log(f"audit: byte_match_ok={byte_match_ok} contents={contents}")
        if not byte_match_ok:
            raise RuntimeError(f"BYTE-MATCH FAILED: {contents}")

    res = stage(
        name=f"audit-{profile}",
        input_files=sorted(str(p) for p in config.RAW.glob("*.raw.parquet")),
        output_files=out_corpora + [out_audit, out_splits, out_eval, out_dedup],
        params={"profile": profile, "target_bytes": target_bytes, "near_thr": near_thr, "seed": seed},
        fn=work, force=force,
    )
    return {"skipped": res.skipped, "audit_summary": str(out_audit)}


def _dominant_ct(counts: dict[str, int]) -> str:
    if not counts:
        return "unknown"
    return max(counts.items(), key=lambda kv: kv[1])[0]


def _build_eval_docs(processed: dict, azure_docs: list, asg, general_eval: list,
                     repo_to_category: dict[str, str] | None = None,
                     train_pool: list[tuple[str, str]] | None = None,
                     near_thr: float = 0.8) -> dict:
    """Assemble and freeze the evaluation document set (plan.md §14).

    Removes any evaluation item that is a near-duplicate of a training document
    (cross-corpus leakage control, red-team blocker). Synthetic diagnostics are
    exempt (they are constructed strings, not corpus text).
    """
    from .synthetic import synthetic_edge_cases
    repo_to_category = repo_to_category or {}

    rows = []

    def push(eval_set: str, repo: str, doc_id: str, ctype: str, text: str) -> None:
        if text and text.strip():
            rows.append({"eval_set": eval_set, "repository": repo,
                         "document_id": doc_id, "content_type": ctype, "text": text})

    # Azure holdouts
    for d in azure_docs:
        split = asg.doc_to_split[d.document_id]
        if split in ("azure_same_service_holdout", "azure_cross_service_holdout"):
            push(split, d.source_repo, d.document_id, _dominant_ct(d.content_type_counts), d.semantic_full)

    # Transfer repos -> mapped to plan.md §14 friendly categories (fallback transfer:<repo>)
    for d in processed.get("transfer", []):
        cat = repo_to_category.get(d.source_repo) or f"transfer:{d.source_repo}"
        push(cat, d.source_repo, d.document_id,
             _dominant_ct(d.content_type_counts), d.semantic_full)

    # External technical
    for d in processed.get("external_technical", []):
        push("external_technical", d.source_repo, d.document_id,
             _dominant_ct(d.content_type_counts), d.semantic_full)

    # General English (held-out portion, disjoint from training)
    for d in general_eval:
        push("general_english", d.source_repo, d.document_id,
             _dominant_ct(d.content_type_counts), d.semantic_full)

    # Cross-corpus near-dup removal for corpus-derived eval docs (not synthetic)
    removed_near_train = 0
    removed_by_set: dict[str, int] = {}
    if train_pool:
        eval_items = [(r["document_id"], r["text"]) for r in rows]
        flagged = corpus.dd.flag_eval_near_train(train_pool, eval_items, threshold=near_thr)
        if flagged:
            for r in rows:
                if r["document_id"] in flagged:
                    removed_by_set[r["eval_set"]] = removed_by_set.get(r["eval_set"], 0) + 1
            rows = [r for r in rows if r["document_id"] not in flagged]
            removed_near_train = len(flagged)

    # Synthetic edge cases (diagnostic; exempt from cross-corpus filter)
    for cid, text in synthetic_edge_cases():
        push("synthetic", "synthetic", f"synthetic:{cid}", "mixed", text)

    config.EVALUATION.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(config.EVALUATION / "eval_docs.parquet")
    _log(f"audit: eval docs = {len(rows)} across {len(set(r['eval_set'] for r in rows))} sets; "
         f"cross-corpus near-dup removed={removed_near_train}")
    return {"removed_near_train": removed_near_train, "removed_by_set": removed_by_set}


def _assert_no_content_leak(train_docs: list, eval_docs: list, label: str) -> None:
    """Raise if any exact semantic-hash is shared between train and eval."""
    train_hashes = {d.sha256 for d in train_docs}
    leaked = [d.document_id for d in eval_docs if d.sha256 in train_hashes]
    if leaked:
        raise RuntimeError(f"{label} train/eval content leak: {len(leaked)} docs, e.g. {leaked[:5]}")


def _write_dedup_audit(processed: dict, azure_docs: list, near, near_thr: float) -> None:
    """Write exact/near-duplicate + cross-repo overlap audit parquets (plan.md §11)."""
    config.AUDIT.mkdir(parents=True, exist_ok=True)
    all_docs = [d for docs in processed.values() for d in docs]

    # Exact duplicate groups across ALL sources
    by_hash: dict[str, list] = {}
    for d in all_docs:
        by_hash.setdefault(d.sha256, []).append(d)
    exact_rows = [{"sha256": h, "n": len(g), "document_ids": ",".join(x.document_id for x in g),
                   "repos": ",".join(sorted({x.source_repo for x in g}))}
                  for h, g in by_hash.items() if len(g) > 1]
    pd.DataFrame(exact_rows or [{"sha256": "", "n": 0, "document_ids": "", "repos": ""}]).to_parquet(
        config.AUDIT / "exact_duplicates.parquet")

    # Cross-repo overlap: identical semantic hash appearing under >1 repo (leakage flag)
    cross_rows = [{"sha256": h, "repos": ",".join(sorted({x.source_repo for x in g})),
                   "n_repos": len({x.source_repo for x in g})}
                  for h, g in by_hash.items() if len({x.source_repo for x in g}) > 1]
    pd.DataFrame(cross_rows or [{"sha256": "", "repos": "", "n_repos": 0}]).to_parquet(
        config.AUDIT / "cross_repo_overlap.parquet")

    # Near-duplicate pairs within the Azure anchor
    near_rows = [{"id_a": a, "id_b": b, "jaccard": j} for a, b, j in (near.pairs if near else [])]
    pd.DataFrame(near_rows or [{"id_a": "", "id_b": "", "jaccard": 0.0}]).to_parquet(
        config.AUDIT / "near_duplicates.parquet")
    _log(f"audit: dedup audit — exact_groups={len(exact_rows)} cross_repo={len(cross_rows)} "
         f"near_pairs={len(near_rows)}")


def _hash_split(docs: list, seed: int, eval_frac: float) -> tuple[list, list]:
    train, ev = [], []
    for d in docs:
        f = int(sha256_text(f"geneval|{seed}|{d.document_id}")[:8], 16) / 0xFFFFFFFF
        (ev if f < eval_frac else train).append(d)
    return train, ev


def _assert_no_train_eval_leak(train_docs, all_azure_docs, asg) -> None:
    train_hashes = {d.sha256 for d in train_docs}
    for d in all_azure_docs:
        if asg.doc_to_split[d.document_id] != "azure_train" and d.sha256 in train_hashes:
            raise RuntimeError(f"train/eval exact-hash leak: {d.document_id}")


# --------------------------------------------------------------------------- #
# TRAIN
# --------------------------------------------------------------------------- #
def run_train(profile: str, force: bool = False, vocab_sizes: tuple[int, ...] | None = None) -> dict:
    vocabs = vocab_sizes or _profile_vocabs(profile)
    trained = {}
    for corpus_name in config.TRAINING_CORPORA:
        corpus_path = config.SPLITS / f"{corpus_name}.corpus.txt"
        manifest = config.MANIFESTS / f"{corpus_name}.corpus.json"
        if not corpus_path.exists():
            raise RuntimeError(f"missing corpus {corpus_path}; run audit first")
        man = json.loads(manifest.read_text()) if manifest.exists() else {}
        for vocab in vocabs:
            tok_id = f"{corpus_name}-bytebpe-{vocab}"
            art = config.ARTIFACTS / tok_id / "tokenizer.json"

            def work(corpus_path=corpus_path, vocab=vocab, tok_id=tok_id, corpus_name=corpus_name, man=man):
                _log(f"train: {tok_id}")
                train.train_tokenizer(
                    corpus_path=corpus_path, vocab_size=vocab, tokenizer_id=tok_id,
                    training_corpus=corpus_name,
                    training_bytes=man.get("content_utf8_bytes", corpus_path.stat().st_size),
                    training_documents=man.get("n_documents", 0),
                    training_manifest_sha256=man.get("training_manifest_sha256", ""),
                )

            res = stage(
                name=f"train-{profile}:{tok_id}",
                input_files=[corpus_path],
                output_files=[art, config.ARTIFACTS / f"{tok_id}.json"],
                params={"vocab": vocab, "corpus": corpus_name},
                fn=work, force=force,
            )
            trained[tok_id] = {"skipped": res.skipped}
    return {"tokenizers": trained}

# --------------------------------------------------------------------------- #
# EVALUATE (Track A trained + Track B baselines)
# --------------------------------------------------------------------------- #
def _load_track_a_encoders(vocab_sizes: tuple[int, ...]) -> list:
    from .encoders import HFEncoder
    from .train import load_tokenizer
    encs = []
    for corpus_name in config.TRAINING_CORPORA:
        for vocab in vocab_sizes:
            tok_id = f"{corpus_name}-bytebpe-{vocab}"
            art = config.ARTIFACTS / tok_id / "tokenizer.json"
            if art.exists():
                encs.append(HFEncoder(tok_id, load_tokenizer(art)))
    return encs


def _load_track_b_encoders(exp: dict) -> list:
    from .baselines import load_tiktoken_baselines
    names = tuple(exp.get("baselines", {}).get("tiktoken", ["r50k_base", "cl100k_base", "o200k_base"]))
    try:
        return list(load_tiktoken_baselines(names))
    except Exception as e:  # pragma: no cover
        _log(f"evaluate: WARNING could not load tiktoken baselines: {e}")
        return []


def run_evaluate(profile: str, exp: dict, force: bool = False) -> dict:
    vocabs = _profile_vocabs(profile)
    eval_docs_path = config.EVALUATION / "eval_docs.parquet"
    out_rows = config.RESULTS_RAW / "eval_rows.parquet"
    out_agg = config.RESULTS_PROCESSED / "eval_aggregate.csv"

    def work():
        if not eval_docs_path.exists():
            raise RuntimeError("eval_docs.parquet missing; run audit first")
        df = pd.read_parquet(eval_docs_path)
        docs_by_set: dict[str, list] = {}
        for _, r in df.iterrows():
            docs_by_set.setdefault(r["eval_set"], []).append(
                evaluate.EvalDoc(r["document_id"], r["repository"], r["content_type"], r["text"]))

        encoders = _load_track_a_encoders(vocabs) + _load_track_b_encoders(exp)
        _log(f"evaluate: {len(encoders)} encoders x {len(docs_by_set)} eval sets")

        all_rows = []
        for enc in encoders:
            for eval_set, docs in docs_by_set.items():
                all_rows.extend(evaluate.evaluate_encoder(enc, eval_set, docs))

        rows_df = evaluate.rows_to_frame(all_rows)
        out_rows.parent.mkdir(parents=True, exist_ok=True)
        rows_df.to_parquet(out_rows)

        # Coverage/correctness gate: any unexplained round-trip failure blocks (plan.md §15)
        bad = rows_df[(~rows_df["roundtrip_ok"]) | (rows_df["unk_count"] > 0)]
        # Empty-string docs legitimately round-trip to ""; exclude only true failures
        bad = bad[bad["utf8_bytes"] > 0]
        if len(bad):
            sample = bad[["tokenizer_id", "eval_set", "document_id"]].head(10).to_dict("records")
            raise RuntimeError(f"ROUND-TRIP/UNK FAILURES: {len(bad)} rows, e.g. {sample}")

        agg = evaluate.aggregate(rows_df)
        out_agg.parent.mkdir(parents=True, exist_ok=True)
        agg.to_csv(out_agg, index=False)
        config.RESULTS_TABLES.mkdir(parents=True, exist_ok=True)
        agg.to_csv(config.RESULTS_TABLES / "eval_aggregate.csv", index=False)

        # Track A paired reduction tables per vocab
        for vocab in vocabs:
            tbl = evaluate.paired_reduction_table(
                agg, f"general-bytebpe-{vocab}", f"azure-bytebpe-{vocab}")
            if len(tbl):
                tbl.to_csv(config.RESULTS_TABLES / f"reduction_azure_vs_general_{vocab}.csv", index=False)
            tblm = evaluate.paired_reduction_table(
                agg, f"general-bytebpe-{vocab}", f"mixed-bytebpe-{vocab}")
            if len(tblm):
                tblm.to_csv(config.RESULTS_TABLES / f"reduction_mixed_vs_general_{vocab}.csv", index=False)
        _log(f"evaluate: wrote {len(rows_df)} rows, {len(agg)} aggregates")

    res = stage(
        name=f"evaluate-{profile}",
        input_files=[eval_docs_path] + [str(config.ARTIFACTS / f"{c}-bytebpe-{v}" / "tokenizer.json")
                                        for c in config.TRAINING_CORPORA for v in vocabs
                                        if (config.ARTIFACTS / f"{c}-bytebpe-{v}" / "tokenizer.json").exists()],
        output_files=[out_rows, out_agg],
        params={"profile": profile, "vocabs": list(vocabs), "baselines": exp.get("baselines", {})},
        fn=work, force=force,
    )
    return {"skipped": res.skipped, "rows": str(out_rows), "aggregate": str(out_agg)}


# --------------------------------------------------------------------------- #
# BENCHMARK (runtime, serialized)
# --------------------------------------------------------------------------- #
def run_benchmark(profile: str, exp: dict, force: bool = False, rounds: int = 5) -> dict:
    from .runtime_bench import benchmark_encoders
    out = config.RESULTS_RAW / "runtime_observations.json"
    eval_docs_path = config.EVALUATION / "eval_docs.parquet"
    vocabs = _profile_vocabs(profile)

    def work():
        df = pd.read_parquet(eval_docs_path)
        # Use the principal Azure holdout docs as the benchmark payload
        docs = df[df["eval_set"] == "azure_cross_service_holdout"]["text"].tolist()
        if len(docs) < 20:
            docs = df["text"].tolist()
        docs = [d for d in docs if d.strip()][:500]
        encoders = _load_track_a_encoders(vocabs) + _load_track_b_encoders(exp)
        summaries = benchmark_encoders(encoders, docs, rounds=rounds, seed=config.GLOBAL_SEED)
        payload = {"profile": profile, "rounds": rounds, "n_docs": len(docs),
                   "controls": {"serialized": True, "randomized_tokenizer_order_per_round": True,
                                "warmup_rounds": 1, "batch_sizes": [1, 8, 32, 128],
                                "buckets": ["short", "medium", "long"],
                                "note": "Single-process serialized run on a thermally variable "
                                        "laptop; treat small differences as indicative, not definitive. "
                                        "Plug into power and stop other workloads before running."},
                   "machine": __import__("msdocs_tokenizer.provenance", fromlist=["machine_metadata"]).machine_metadata(),
                   "summaries": [s.__dict__ for s in summaries]}
        out.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(out, payload)
        # Compact throughput table
        rows = [{"tokenizer_id": s.tokenizer_id, "mb_per_second_median": s.mb_per_second_median,
                 "mb_per_second_p95": s.mb_per_second_p95, "load_seconds": s.load_seconds}
                for s in summaries]
        pd.DataFrame(rows).to_csv(config.RESULTS_TABLES / "runtime_throughput.csv", index=False)
        _log(f"benchmark: {len(summaries)} encoders, {len(docs)} docs, {rounds} rounds")

    res = stage(name=f"benchmark-{profile}", input_files=[eval_docs_path],
                output_files=[out], params={"rounds": rounds, "vocabs": list(vocabs)},
                fn=work, force=force)
    return {"skipped": res.skipped, "observations": str(out)}

# --------------------------------------------------------------------------- #
# ANALYZE (paired bootstrap + figures with source tables)
# --------------------------------------------------------------------------- #
def _paired_counts(rows: pd.DataFrame, eval_set: str, tok_g: str, tok_a: str):
    g = rows[(rows.eval_set == eval_set) & (rows.tokenizer_id == tok_g)][["document_id", "token_count", "content_type", "repository"]]
    a = rows[(rows.eval_set == eval_set) & (rows.tokenizer_id == tok_a)][["document_id", "token_count"]]
    m = g.merge(a, on="document_id", suffixes=("_g", "_a"))
    return m


def run_analyze(profile: str, exp: dict, force: bool = False) -> dict:
    from .stats import paired_bootstrap_relative_reduction, stratified_bootstrap
    rows_path = config.RESULTS_RAW / "eval_rows.parquet"
    out_boot = config.RESULTS_PROCESSED / "bootstrap.json"
    out_fig_flag = config.RESULTS_FIGURES / ".figures_done"
    vocabs = _profile_vocabs(profile)
    n_resamples = int(exp.get("bootstrap_resamples", 10000))
    principal_vocab = config.VOCAB_SIZE_PILOT if config.VOCAB_SIZE_PILOT in vocabs else vocabs[0]

    def work():
        rows = pd.read_parquet(rows_path)
        boot = {"profile": profile, "n_resamples": n_resamples, "seed": config.GLOBAL_SEED, "comparisons": {}}
        principal_set = "azure_cross_service_holdout"

        for vocab in vocabs:
            gid, aid, mid = (f"general-bytebpe-{vocab}", f"azure-bytebpe-{vocab}", f"mixed-bytebpe-{vocab}")
            for label, tok_a in [("azure_vs_general", aid), ("mixed_vs_general", mid)]:
                m = _paired_counts(rows, principal_set, gid, tok_a)
                if len(m) >= 5:
                    r = paired_bootstrap_relative_reduction(
                        m.token_count_g.values, m.token_count_a.values, n_resamples=n_resamples, seed=config.GLOBAL_SEED)
                    boot["comparisons"][f"{label}:{vocab}:{principal_set}"] = r.__dict__

            # Stratified analyses at the principal vocab (plan.md §16)
            if vocab == principal_vocab:
                m = _paired_counts(rows, principal_set, gid, aid)
                if len(m) >= 5:
                    strat_ct = stratified_bootstrap(m.token_count_g.values, m.token_count_a.values,
                                                    m.content_type.tolist(), n_resamples=n_resamples,
                                                    seed=config.GLOBAL_SEED)
                    boot["by_content_type"] = {k: v.__dict__ for k, v in strat_ct.items()}
                    strat_repo = stratified_bootstrap(m.token_count_g.values, m.token_count_a.values,
                                                      m.repository.tolist(), n_resamples=n_resamples,
                                                      seed=config.GLOBAL_SEED)
                    boot["by_repository"] = {k: v.__dict__ for k, v in strat_repo.items()}

                # Transfer + regression: azure_vs_general on every eval set
                boot["by_eval_set"] = {}
                for eval_set in sorted(rows.eval_set.unique()):
                    mm = _paired_counts(rows, eval_set, gid, aid)
                    if len(mm) >= 5:
                        rr = paired_bootstrap_relative_reduction(
                            mm.token_count_g.values, mm.token_count_a.values,
                            n_resamples=n_resamples, seed=config.GLOBAL_SEED)
                        boot["by_eval_set"][eval_set] = rr.__dict__

        atomic_write_json(out_boot, boot)
        _make_figures(rows, profile, vocabs, principal_vocab)
        _fragmentation_and_vocab(profile, principal_vocab)
        out_fig_flag.parent.mkdir(parents=True, exist_ok=True)
        out_fig_flag.write_text("done\n")
        _log(f"analyze: {len(boot['comparisons'])} bootstrap comparisons")

    res = stage(name=f"analyze-{profile}", input_files=[rows_path], output_files=[out_boot, out_fig_flag],
                params={"n_resamples": n_resamples, "vocabs": list(vocabs)}, fn=work, force=force)
    return {"skipped": res.skipped, "bootstrap": str(out_boot)}


def _make_figures(rows: pd.DataFrame, profile: str, vocabs, principal_vocab: int) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figdir = config.RESULTS_FIGURES
    figdir.mkdir(parents=True, exist_ok=True)
    tabdir = config.RESULTS_TABLES
    agg = evaluate.aggregate(rows)

    # Figure 2: tokens per 1000 bytes by corpus and vocab (Track A only)
    trackA = agg[agg.tokenizer_id.str.contains("bytebpe")]
    principal = trackA[trackA.eval_set == "azure_cross_service_holdout"].copy()
    if len(principal):
        principal[["tokenizer_id", "tokens_per_1000_utf8_bytes_micro"]].to_csv(
            tabdir / "fig_tokens_per_1k_by_tokenizer.csv", index=False)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        principal = principal.sort_values("tokenizer_id")
        ax.bar(principal.tokenizer_id, principal.tokens_per_1000_utf8_bytes_micro, color="#2b6cb0")
        ax.set_ylabel("tokens / 1000 UTF-8 bytes (lower=better)")
        ax.set_title("Azure cross-service holdout: compression by tokenizer")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout(); fig.savefig(figdir / "fig02_tokens_per_1k.png", dpi=120); plt.close(fig)

    # Figure 1: relative reduction azure vs general per vocab on principal set
    red_rows = []
    for vocab in vocabs:
        sub = agg[(agg.eval_set == "azure_cross_service_holdout")]
        g = sub[sub.tokenizer_id == f"general-bytebpe-{vocab}"]
        a = sub[sub.tokenizer_id == f"azure-bytebpe-{vocab}"]
        if len(g) and len(a):
            from .metrics import relative_token_reduction
            red_rows.append({"vocab": vocab,
                             "relative_token_reduction_pct": relative_token_reduction(
                                 g.iloc[0].tokens_per_1000_utf8_bytes_micro,
                                 a.iloc[0].tokens_per_1000_utf8_bytes_micro)})
    if red_rows:
        rdf = pd.DataFrame(red_rows)
        rdf.to_csv(tabdir / "fig_relative_reduction_by_vocab.csv", index=False)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(rdf.vocab, rdf.relative_token_reduction_pct, "o-", color="#2f855a")
        ax.set_xlabel("vocabulary size"); ax.set_ylabel("Azure vs General reduction (%)")
        ax.set_title("Relative token reduction on Azure cross-service holdout")
        ax.axhline(0, color="gray", lw=0.8)
        plt.tight_layout(); fig.savefig(figdir / "fig01_relative_reduction.png", dpi=120); plt.close(fig)

    # Figure 3/4: transfer across eval sets (azure vs general at principal vocab)
    tset = agg[agg.tokenizer_id.isin([f"azure-bytebpe-{principal_vocab}", f"general-bytebpe-{principal_vocab}"])]
    if len(tset):
        piv = tset.pivot_table(index="eval_set", columns="tokenizer_id",
                               values="tokens_per_1000_utf8_bytes_micro")
        piv.to_csv(tabdir / "fig_transfer_by_eval_set.csv")


def _fragmentation_and_vocab(profile: str, principal_vocab: int) -> None:
    """Identifier fragmentation + vocabulary utilization (plan.md §15, figs 6, 8)."""
    import re
    from collections import Counter

    from .encoders import HFEncoder
    from .metrics import fragmentation_stats
    from .train import load_tokenizer
    from .vocab import vocabulary_utilization

    eval_docs = config.EVALUATION / "eval_docs.parquet"
    if not eval_docs.exists():
        return
    df = pd.read_parquet(eval_docs)
    principal = df[df.eval_set == "azure_cross_service_holdout"]
    text_blob = "\n".join(principal.text.tolist())

    # Extract fragmentation items by category from the principal holdout text
    patterns = {
        "resource_provider": re.compile(r"Microsoft\.[A-Za-z][\w.]+(?:/[A-Za-z][\w]+)*"),
        "cli_flag": re.compile(r"--[a-z][a-z0-9-]+"),
        "url_path": re.compile(r"https?://[^\s`)\"']+"),
        "identifier_camel": re.compile(r"\b[a-z]+(?:[A-Z][a-z0-9]+)+\b"),
        "identifier_snake": re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b"),
        "prose_word": re.compile(r"\b[A-Za-z]{3,}\b"),
    }
    items: dict[str, list[str]] = {}
    for name, pat in patterns.items():
        found = pat.findall(text_blob)
        # Deduplicate + cap per category for a bounded, representative sample
        uniq = list(dict.fromkeys(found))[:2000]
        items[name] = uniq

    encoders = []
    for corpus_name in config.TRAINING_CORPORA:
        art = config.ARTIFACTS / f"{corpus_name}-bytebpe-{principal_vocab}" / "tokenizer.json"
        if art.exists():
            encoders.append((f"{corpus_name}-bytebpe-{principal_vocab}", HFEncoder(corpus_name, load_tokenizer(art)), load_tokenizer(art)))

    frag_rows = []
    for cat, its in items.items():
        if not its:
            continue
        for tok_id, enc, _tok in encoders:
            counts = [enc.count_tokens(x) for x in its]
            s = fragmentation_stats(counts)
            frag_rows.append({
                "category": cat, "tokenizer_id": tok_id, "n_items": s.n,
                "mean_tokens": round(s.mean, 3), "median_tokens": s.median, "p95_tokens": s.p95,
                "frac_one_token": round(s.frac_one_token, 3),
                "frac_two_tokens": round(s.frac_two_tokens, 3),
                "frac_three_plus": round(s.frac_three_plus, 3),
            })
    if frag_rows:
        pd.DataFrame(frag_rows).to_csv(config.RESULTS_TABLES / "fragmentation.csv", index=False)

    # Vocabulary utilization on the principal holdout
    vocab_rows = []
    for tok_id, enc, tok in encoders:
        id_counts: Counter = Counter()
        for text in principal.text.tolist():
            id_counts.update(enc.encode(text))
        u = vocabulary_utilization(tok, id_counts)
        vocab_rows.append({
            "tokenizer_id": tok_id, "vocab_size": u.vocab_size,
            "frac_used": round(u.frac_used, 4), "used_ge_10": u.used_ge_10,
            "used_ge_100": u.used_ge_100, "used_ge_1000": u.used_ge_1000, "unused": u.unused,
            "top1pct_share": round(u.top1pct_occurrence_share, 4),
            "top10pct_share": round(u.top10pct_occurrence_share, 4),
            "mean_token_byte_len": round(u.mean_token_byte_len, 3),
        })
    if vocab_rows:
        pd.DataFrame(vocab_rows).to_csv(config.RESULTS_TABLES / "vocab_utilization.csv", index=False)
    _log(f"analyze: fragmentation ({len(frag_rows)} rows) + vocab utilization ({len(vocab_rows)} rows)")


# --------------------------------------------------------------------------- #
# REPORT + NOTEBOOKS
# --------------------------------------------------------------------------- #
def _read_csv(path: Path):
    return pd.read_csv(path) if path.exists() else None


def run_report(profile: str, exp: dict, force: bool = False) -> dict:
    out_report = config.RESULTS_REPORTS / "FINAL_REPORT.md"

    def work():
        from .report import build_final_report, build_notebooks
        md = build_final_report(profile, exp)
        out_report.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(out_report, md)
        build_notebooks()
        _log(f"report: wrote {out_report}")

    # Depend on the processed results so report regenerates when they change
    inputs = [p for p in [config.AUDIT / "audit_summary.json",
                          config.RESULTS_PROCESSED / "eval_aggregate.csv",
                          config.RESULTS_PROCESSED / "bootstrap.json"] if p.exists()]
    res = stage(name=f"report-{profile}", input_files=inputs or [config.AUDIT / "audit_summary.json"],
                output_files=[out_report], params={"profile": profile}, fn=work, force=force)
    return {"skipped": res.skipped, "report": str(out_report)}


# --------------------------------------------------------------------------- #
# VERIFY (independent recomputation + gates)
# --------------------------------------------------------------------------- #
def run_verify(profile: str, exp: dict) -> dict:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    # Audit gates
    audit = config.AUDIT / "audit_summary.json"
    if audit.exists():
        a = json.loads(audit.read_text())
        check("byte_match_ok", a.get("byte_match_ok", False), str(a.get("corpora_content_bytes")))
        check("no_leakage", not a.get("leakage_violations"), str(a.get("leakage_violations")))
        # Cross-corpus + general leakage controls present (audit raises on any real leak)
        controls = ("exact_dedup_general" in a and "cross_corpus_near_dup_eval" in a)
        cc = (a.get("cross_corpus_near_dup_eval") or {}).get("removed_near_train", None)
        check("leakage_controls_present", controls and cc is not None,
              f"cross_corpus_removed={cc}")
    else:
        check("audit_summary_exists", False, "missing")

    # Round-trip + UNK + totals reconcile (independent recomputation)
    rows_path = config.RESULTS_RAW / "eval_rows.parquet"
    if rows_path.exists():
        rows = pd.read_parquet(rows_path)
        real_fail = rows[((~rows.roundtrip_ok) | (rows.unk_count > 0)) & (rows.utf8_bytes > 0)]
        check("roundtrip_all_ok", len(real_fail) == 0, f"{len(real_fail)} failures")
        # Independent aggregate recomputation matches stored aggregate
        agg_stored = _read_csv(config.RESULTS_PROCESSED / "eval_aggregate.csv")
        agg_recomp = evaluate.aggregate(rows)
        if agg_stored is not None:
            merged = agg_stored.merge(agg_recomp, on=["tokenizer_id", "eval_set"], suffixes=("_s", "_r"))
            recon = bool((abs(merged.total_tokens_s - merged.total_tokens_r) == 0).all())
            check("totals_reconcile", recon, "")
    else:
        check("eval_rows_exists", False, "missing")

    # Provenance completeness for every trained tokenizer
    prov_ok = True
    dist_marked = True
    for pj in config.ARTIFACTS.glob("*.json"):
        p = json.loads(pj.read_text())
        for field in ["artifact_sha256", "config_sha256", "vocab_size_actual", "training_manifest_sha256", "machine_id"]:
            if not p.get(field):
                prov_ok = False
        if "distributable" not in p or not p.get("distribution_note"):
            dist_marked = False
    check("provenance_complete", prov_ok, "")

    # Artifact distribution policy: every provenance marks distributability AND no
    # tokenizer.json artifact is committed (WikiText-derived are local-use-only).
    import subprocess as _sp
    tracked_artifacts = _sp.run(["git", "-C", str(config.ROOT), "ls-files", "artifacts/"],
                                capture_output=True, text=True).stdout
    no_tokenizer_json = "tokenizer.json" not in tracked_artifacts
    check("artifact_distribution_marked", dist_marked and no_tokenizer_json,
          f"all_marked={dist_marked}, no_tokenizer_json_committed={no_tokenizer_json}")

    # Sources pinned
    check("sources_lock_exists", (config.MANIFESTS / "sources.lock.json").exists(), "")

    all_ok = all(ok for _, ok, _ in checks)
    md = ["# Verification report", "", f"Profile: `{profile}`  ", f"Generated: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}", "",
          "| Check | Result | Detail |", "|---|---|---|"]
    for name, ok, detail in checks:
        md.append(f"| {name} | {'✅ PASS' if ok else '❌ FAIL'} | {detail[:80]} |")
    md += ["", f"**Overall: {'✅ ALL CHECKS PASS' if all_ok else '❌ FAILURES PRESENT'}**", ""]
    config.RESULTS_REPORTS.mkdir(parents=True, exist_ok=True)
    atomic_write_text(config.RESULTS_REPORTS / "VERIFICATION.md", "\n".join(md))
    _log(f"verify: {'PASS' if all_ok else 'FAIL'} ({sum(1 for _,o,_ in checks if o)}/{len(checks)})")
    return {"all_ok": all_ok, "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks]}
