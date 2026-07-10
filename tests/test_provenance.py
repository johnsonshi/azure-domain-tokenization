"""Provenance, hashing, atomic + locked writes (plan.md §23)."""
from __future__ import annotations

import json

from msdocs_tokenizer import provenance as pv


def test_sha256_stable():
    assert pv.sha256_text("hello") == pv.sha256_text("hello")
    assert pv.sha256_bytes(b"hello") == pv.sha256_text("hello")
    assert len(pv.sha256_text("x")) == 64


def test_atomic_write_roundtrip(tmp_path):
    p = tmp_path / "sub" / "file.json"
    pv.atomic_write_json(p, {"b": 2, "a": 1})
    loaded = json.loads(p.read_text())
    assert loaded == {"a": 1, "b": 2}
    # No leftover temp files
    assert list(tmp_path.rglob("*.tmp")) == []


def test_atomic_write_is_atomic_overwrite(tmp_path):
    p = tmp_path / "f.txt"
    pv.atomic_write_text(p, "first")
    pv.atomic_write_text(p, "second")
    assert p.read_text() == "second"


def test_file_lock_serializes(tmp_path):
    target = tmp_path / "shared.txt"
    with pv.file_lock(target):
        assert (tmp_path / "shared.txt.lock").exists()
    assert not (tmp_path / "shared.txt.lock").exists()


def test_machine_metadata_complete():
    md = pv.machine_metadata()
    for key in ("platform", "machine", "logical_cores", "python_version"):
        assert md.get(key) is not None


def test_package_versions_tracked():
    versions = pv.package_versions()
    assert versions.get("tokenizers") not in (None, "not-installed")
    assert versions.get("numpy") not in (None, "not-installed")


def test_provenance_stamp_complete():
    stamp = pv.provenance_stamp()
    for key in ("git_commit", "machine_id", "machine", "package_versions", "seed", "created_at"):
        assert key in stamp
    assert stamp["machine_id"]


def test_machine_id_stable():
    assert pv.machine_id() == pv.machine_id()
