"""Unicode normalization tests (plan.md §23)."""
from __future__ import annotations

import unicodedata

from msdocs_tokenizer import normalize as nz


def test_nfc_composes():
    # "é" as e + combining acute -> single codepoint under NFC
    decomposed = "e\u0301"
    composed = nz.nfc(decomposed)
    assert composed == "\u00e9"
    assert nz.is_nfc(composed)
    assert len(composed) == 1


def test_case_and_accents_preserved():
    text = "Azure CLI — café PÑEÑO 版本 3.14.0 🚀"
    out = nz.normalize_document(text)
    assert out is not None
    # Case preserved, accents preserved, emoji preserved
    assert "Azure CLI" in out
    assert "café" in out
    assert "🚀" in out
    assert "版本" in out


def test_report_counts_changes():
    report = nz.NormalizationReport()
    nz.normalize_document("e\u0301", report)   # changes under NFC
    nz.normalize_document("plain", report)      # unchanged
    assert report.total == 2
    assert report.changed_by_nfc == 1


def test_malformed_quarantined():
    report = nz.NormalizationReport()
    out = nz.normalize_document("bad\ud800surrogate", report)
    assert out is None
    assert report.malformed == 1


def test_count_metrics():
    b, c, w = nz.count_metrics("café 🚀 test")
    assert c == len("café 🚀 test")
    assert b == len("café 🚀 test".encode("utf-8"))
    assert w == 3


def test_nfc_idempotent():
    text = "Ångström café"
    once = nz.nfc(text)
    assert once == nz.nfc(once)
    assert unicodedata.is_normalized("NFC", once)
