"""Exact and near-duplicate detection (plan.md §11).

- Exact: SHA-256 over normalized text.
- Near: MinHash + LSH over character n-gram shingles, clustered with union-find.

Near-duplicate removal prevents train/eval leakage that would inflate the
apparent compression advantage of any tokenizer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from datasketch import MinHash, MinHashLSH

from .provenance import sha256_text

_WS_RE = re.compile(r"\s+")


def canonical_for_hash(text: str) -> str:
    """Whitespace-collapsed text used for exact-duplicate hashing."""
    return _WS_RE.sub(" ", text).strip()


def exact_hash(text: str) -> str:
    return sha256_text(canonical_for_hash(text))


def find_exact_duplicates(items: list[tuple[str, str]]) -> dict[str, list[str]]:
    """items = [(id, text)]. Return {hash: [ids...]} for groups with >1 member."""
    by_hash: dict[str, list[str]] = {}
    for _id, text in items:
        by_hash.setdefault(exact_hash(text), []).append(_id)
    return {h: ids for h, ids in by_hash.items() if len(ids) > 1}


def _shingles(text: str, k: int = 5) -> set[bytes]:
    t = canonical_for_hash(text)
    if len(t) <= k:
        return {t.encode("utf-8")} if t else set()
    return {t[i : i + k].encode("utf-8") for i in range(len(t) - k + 1)}


def _minhash(text: str, num_perm: int, k: int) -> MinHash:
    m = MinHash(num_perm=num_perm)
    for sh in _shingles(text, k):
        m.update(sh)
    return m


@dataclass
class NearDupResult:
    threshold: float
    clusters: dict[str, int]          # id -> cluster_id
    pairs: list[tuple[str, str, float]]  # (id_a, id_b, jaccard_estimate)

    @property
    def num_clusters(self) -> int:
        return len(set(self.clusters.values()))

    @property
    def num_near_dup_items(self) -> int:
        sizes: dict[int, int] = {}
        for c in self.clusters.values():
            sizes[c] = sizes.get(c, 0) + 1
        return sum(s for s in sizes.values() if s > 1)


class _UnionFind:
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


def find_near_duplicates(
    items: list[tuple[str, str]],
    threshold: float = 0.8,
    num_perm: int = 128,
    k: int = 5,
) -> NearDupResult:
    """Cluster near-duplicates by estimated Jaccard >= threshold."""
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    minhashes: dict[str, MinHash] = {}
    for _id, text in items:
        m = _minhash(text, num_perm, k)
        minhashes[_id] = m
        # insert may raise if duplicate key; keys are unique by contract
        lsh.insert(_id, m)

    uf = _UnionFind()
    pairs: list[tuple[str, str, float]] = []
    seen: set[frozenset[str]] = set()
    for _id, m in minhashes.items():
        uf.find(_id)  # ensure present
        for cand in lsh.query(m):
            if cand == _id:
                continue
            key = frozenset((_id, cand))
            if key in seen:
                continue
            seen.add(key)
            j = m.jaccard(minhashes[cand])
            if j >= threshold:
                uf.union(_id, cand)
                pairs.append((_id, cand, float(j)))

    # Assign compact integer cluster ids
    root_to_cid: dict[str, int] = {}
    clusters: dict[str, int] = {}
    for _id, _ in items:
        root = uf.find(_id)
        if root not in root_to_cid:
            root_to_cid[root] = len(root_to_cid)
        clusters[_id] = root_to_cid[root]
    return NearDupResult(threshold=threshold, clusters=clusters, pairs=pairs)
