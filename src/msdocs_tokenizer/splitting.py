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


class _SplitUnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def assign_azure_splits(
    docs: list[DocumentRef],
    seed: int,
    cross_service_fraction: float = 0.15,
    same_service_holdout_fraction: float = 0.12,
) -> SplitAssignment:
    """Assign every Azure document to a split with strict group isolation.

    Leakage groups are the connected components after unioning documents that
    share a top-level service OR a near-duplicate cluster. This guarantees no
    near-duplicate cluster and no service can straddle the train/holdout boundary
    even when a near-duplicate cluster spans multiple services.

    1. Route a deterministic fraction of whole leakage groups to the
       cross-service holdout (service- and near-dup-disjoint from train).
    2. Within train-pool groups, route whole near-duplicate clusters (by global
       cluster id) to the same-service holdout.
    """
    uf = _SplitUnionFind()
    for d in docs:
        uf.find(d.document_id)

    # Union by service
    service_rep: dict[str, str] = {}
    for d in docs:
        svc = top_level_service(d.source_path)
        if svc in service_rep:
            uf.union(service_rep[svc], d.document_id)
        else:
            service_rep[svc] = d.document_id
    # Union by near-duplicate cluster
    cluster_rep: dict[int, str] = {}
    for d in docs:
        if d.cluster_id >= 0:
            if d.cluster_id in cluster_rep:
                uf.union(cluster_rep[d.cluster_id], d.document_id)
            else:
                cluster_rep[d.cluster_id] = d.document_id

    groups: dict[str, list[DocumentRef]] = {}
    for d in docs:
        groups.setdefault(uf.find(d.document_id), []).append(d)

    doc_to_split: dict[str, str] = {}
    for gid, gdocs in groups.items():
        if _stable_fraction(f"grp|{seed}|{gid}") < cross_service_fraction:
            for d in gdocs:
                doc_to_split[d.document_id] = "azure_cross_service_holdout"
        else:
            # Train-pool group: hold out whole near-dup clusters (global id) as same-service.
            for d in gdocs:
                key_id = d.cluster_id if d.cluster_id >= 0 else d.document_id
                if _stable_fraction(f"ssh|{seed}|{key_id}") < same_service_holdout_fraction:
                    doc_to_split[d.document_id] = "azure_same_service_holdout"
                else:
                    doc_to_split[d.document_id] = "azure_train"

    # Report service -> split (a service is wholly in one leakage group)
    service_to_split: dict[str, str] = {}
    svc_splits: dict[str, set[str]] = {}
    for d in docs:
        svc_splits.setdefault(top_level_service(d.source_path), set()).add(doc_to_split[d.document_id])
    for svc, splits in svc_splits.items():
        if splits == {"azure_cross_service_holdout"}:
            service_to_split[svc] = "azure_cross_service_holdout"
        else:
            service_to_split[svc] = "azure_train"

    stats: dict[str, int] = {}
    for s in doc_to_split.values():
        stats[s] = stats.get(s, 0) + 1
    stats["n_services"] = len(svc_splits)
    stats["n_leakage_groups"] = len(groups)
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
