"""Exact and near-duplicate detection (plan.md §23)."""
from __future__ import annotations

from msdocs_tokenizer import dedup


def test_exact_duplicates_found():
    items = [
        ("a", "The Azure CLI is great."),
        ("b", "The  Azure   CLI is great."),  # whitespace-only difference
        ("c", "A completely different sentence about maps."),
    ]
    groups = dedup.find_exact_duplicates(items)
    # a and b collapse (whitespace canonicalized); c is unique
    assert any(set(ids) == {"a", "b"} for ids in groups.values())
    assert all("c" not in ids for ids in groups.values())


def test_exact_hash_whitespace_invariant():
    assert dedup.exact_hash("a b  c") == dedup.exact_hash("a  b c")
    assert dedup.exact_hash("a b c") != dedup.exact_hash("a b d")


def test_near_duplicates_clustered():
    base = "Azure Container Registry stores and manages container images for you. " * 5
    near = base.replace("stores and manages", "stores plus manages")
    far = "Cartography is the study and practice of making maps across the world. " * 5
    items = [("doc1", base), ("doc2", near), ("doc3", far)]
    res = dedup.find_near_duplicates(items, threshold=0.7)
    # doc1 and doc2 should share a cluster; doc3 should not join them
    assert res.clusters["doc1"] == res.clusters["doc2"]
    assert res.clusters["doc3"] != res.clusters["doc1"]
    assert res.num_near_dup_items == 2


def test_near_dup_deterministic():
    items = [("x", "same text here about clouds " * 4), ("y", "same text here about clouds " * 4)]
    r1 = dedup.find_near_duplicates(items, threshold=0.8)
    r2 = dedup.find_near_duplicates(items, threshold=0.8)
    assert r1.clusters == r2.clusters
