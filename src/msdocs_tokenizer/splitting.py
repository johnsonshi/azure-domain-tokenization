"""Group-aware train/eval splitting (plan.md §11).

Never split lines/paragraphs from the same document (or the same near-duplicate
cluster, or the same top-level service directory) across train and test. This is
the core leakage control for the controlled comparison.

For Azure we produce three splits:
- ``azure_train``
- ``azure_same_service_holdout``      (held-out docs from services also in train)
- ``azure_cross_service_holdout``     (held-out docs from services never in train)

The cross-service holdout is the principal Azure evaluation set.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


def top_level_service(source_path: str) -> str:
    """The service/product grouping key = first meaningful path component.

    e.g. ``articles/storage/blobs/foo.md`` -> ``storage``.
    """
    parts = [p for p in source_path.replace("\\", "/").split("/") if p and p != "."]
    # Skip common repo-root wrappers.
    skip = {"articles", "docs", "content", "azure-docs", "includes"}
    for p in parts:
        if p.lower() not in skip:
            return p.lower()
    return parts[0].lower() if parts else "_root"


def _stable_fraction(key: str) -> float:
    """Deterministic uniform value in [0, 1) from a string key."""
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / float(1 << 64)


@dataclass
class DocumentRef:
    document_id: str
    source_repo: str
    source_path: str
    cluster_id: int = -1  # near-duplicate cluster; -1 = singleton


@dataclass
class SplitAssignment:
    doc_to_split: dict[str, str]
    service_to_split: dict[str, str]
    stats: dict[str, int] = field(default_factory=dict)


def assign_azure_splits(
    docs: list[DocumentRef],
    seed: int,
    cross_service_fraction: float = 0.15,
    same_service_holdout_fraction: float = 0.12,
) -> SplitAssignment:
    """Assign every Azure document to a split with strict group isolation.

    Strategy:
    1. Group documents by top-level service. Deterministically route a fraction
       of *services* wholly into the cross-service holdout (no doc from those
       services appears in train).
    2. Within the remaining (train) services, deterministically hold out a
       fraction of *near-duplicate clusters* as the same-service holdout.
    """
    # Group by service
    services: dict[str, list[DocumentRef]] = {}
    for d in docs:
        services.setdefault(top_level_service(d.source_path), []).append(d)

    service_to_split: dict[str, str] = {}
    for svc in services:
        if _stable_fraction(f"svc|{seed}|{svc}") < cross_service_fraction:
            service_to_split[svc] = "azure_cross_service_holdout"
        else:
            service_to_split[svc] = "azure_train"

    doc_to_split: dict[str, str] = {}
    for svc, svc_docs in services.items():
        if service_to_split[svc] == "azure_cross_service_holdout":
            for d in svc_docs:
                doc_to_split[d.document_id] = "azure_cross_service_holdout"
            continue
        # Same-service holdout: route whole near-dup clusters out of train.
        for d in svc_docs:
            group_key = f"clu|{seed}|{svc}|{d.cluster_id if d.cluster_id >= 0 else d.document_id}"
            if _stable_fraction(group_key) < same_service_holdout_fraction:
                doc_to_split[d.document_id] = "azure_same_service_holdout"
            else:
                doc_to_split[d.document_id] = "azure_train"

    stats: dict[str, int] = {}
    for s in doc_to_split.values():
        stats[s] = stats.get(s, 0) + 1
    stats["n_services"] = len(services)
    stats["n_cross_service_holdout_services"] = sum(
        1 for v in service_to_split.values() if v == "azure_cross_service_holdout"
    )
    return SplitAssignment(doc_to_split=doc_to_split, service_to_split=service_to_split, stats=stats)


def verify_no_cross_split_leakage(
    docs: list[DocumentRef], assignment: SplitAssignment
) -> list[str]:
    """Return a list of violation messages (empty => clean).

    Checks: (a) every doc has exactly one split; (b) no near-duplicate cluster
    spans train and any holdout; (c) no service spans train and cross-service.
    """
    violations: list[str] = []
    cluster_splits: dict[int, set[str]] = {}
    service_splits: dict[str, set[str]] = {}
    for d in docs:
        split = assignment.doc_to_split.get(d.document_id)
        if split is None:
            violations.append(f"doc {d.document_id} has no split")
            continue
        if d.cluster_id >= 0:
            cluster_splits.setdefault(d.cluster_id, set()).add(split)
        service_splits.setdefault(top_level_service(d.source_path), set()).add(split)

    for cid, splits in cluster_splits.items():
        if "azure_train" in splits and (splits - {"azure_train"}):
            violations.append(f"near-dup cluster {cid} spans train and holdout: {sorted(splits)}")
    for svc, splits in service_splits.items():
        if "azure_cross_service_holdout" in splits and (splits - {"azure_cross_service_holdout"}):
            violations.append(f"service {svc} spans cross-service holdout and other: {sorted(splits)}")
    return violations
