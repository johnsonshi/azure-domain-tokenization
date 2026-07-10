"""Deterministic sampling + exact byte matching (plan.md §23)."""
from __future__ import annotations

from msdocs_tokenizer import sampling


def _docs(n=200):
    return [(f"doc{i}", f"Document number {i}. " + "content " * (i % 30 + 1)) for i in range(n)]


def test_deterministic_selection():
    docs = _docs()
    r1 = sampling.deterministic_sample(docs, target_bytes=5000, seed=1, source_commit="abc")
    r2 = sampling.deterministic_sample(docs, target_bytes=5000, seed=1, source_commit="abc")
    assert [d.document_id for d in r1.docs] == [d.document_id for d in r2.docs]
    assert r1.total_bytes == r2.total_bytes


def test_seed_changes_selection():
    docs = _docs()
    r1 = sampling.deterministic_sample(docs, target_bytes=5000, seed=1, source_commit="abc")
    r2 = sampling.deterministic_sample(docs, target_bytes=5000, seed=2, source_commit="abc")
    assert [d.document_id for d in r1.docs] != [d.document_id for d in r2.docs]


def test_hits_exact_byte_budget():
    docs = _docs(500)
    target = 8000
    r = sampling.deterministic_sample(docs, target_bytes=target, seed=3, source_commit="c")
    assert r.total_bytes == target  # truncation lands on exact budget
    assert r.within_tolerance
    # Reconstructed bytes equal reported bytes
    total = sum(len(t.encode("utf-8")) for t in r.texts.values())
    assert total == r.total_bytes


def test_truncation_utf8_safe():
    docs = [("d0", "🚀" * 1000)]  # 4 bytes each
    r = sampling.deterministic_sample(docs, target_bytes=10, seed=0, source_commit="c")
    # 10 bytes / 4 = 2 full emoji = 8 bytes; must not split a codepoint
    text = r.texts["d0"]
    assert text.encode("utf-8").decode("utf-8") == text
    assert len(text.encode("utf-8")) <= 10


def test_byte_matching_across_corpora():
    a = _docs(300)
    b = [(f"b{i}", f"Alternate corpus doc {i}. " + "words " * (i % 25 + 1)) for i in range(300)]
    target = 6000
    ra = sampling.deterministic_sample(a, target, seed=5, source_commit="ca")
    rb = sampling.deterministic_sample(b, target, seed=5, source_commit="cb")
    # Both corpora match the target within 0.1%
    assert ra.within_tolerance and rb.within_tolerance
    assert abs(ra.total_bytes - rb.total_bytes) <= max(1, int(0.001 * target))


def test_mixed_5050():
    a = _docs(300)
    b = [(f"b{i}", f"Alternate {i}. " + "words " * (i % 25 + 1)) for i in range(300)]
    target = 8000
    sa, sb = sampling.interleave_mixed(a, b, target, seed=9, commit_a="ca", commit_b="cb")
    assert abs((sa.total_bytes + sb.total_bytes) - target) <= 2
    # roughly balanced halves
    assert abs(sa.total_bytes - sb.total_bytes) <= max(2, int(0.01 * target))
