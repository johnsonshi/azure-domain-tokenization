"""Resume-after-interruption for pipeline stages (plan.md §23)."""
from __future__ import annotations

from msdocs_tokenizer import staging


def test_stage_runs_then_skips(tmp_path):
    inp = tmp_path / "in.txt"
    inp.write_text("hello")
    out = tmp_path / "out.txt"
    calls = {"n": 0}

    def work():
        calls["n"] += 1
        out.write_text("done")

    r1 = staging.stage("s1", [inp], [out], {"p": 1}, work, marker_dir=tmp_path / "m")
    assert not r1.skipped and calls["n"] == 1

    # Re-run: inputs unchanged, output exists -> skipped, fn not called again
    r2 = staging.stage("s1", [inp], [out], {"p": 1}, work, marker_dir=tmp_path / "m")
    assert r2.skipped and calls["n"] == 1


def test_stage_reruns_on_input_change(tmp_path):
    inp = tmp_path / "in.txt"
    inp.write_text("hello")
    out = tmp_path / "out.txt"
    calls = {"n": 0}

    def work():
        calls["n"] += 1
        out.write_text("done")

    staging.stage("s2", [inp], [out], {"p": 1}, work, marker_dir=tmp_path / "m")
    inp.write_text("changed")  # invalidate
    r = staging.stage("s2", [inp], [out], {"p": 1}, work, marker_dir=tmp_path / "m")
    assert not r.skipped and calls["n"] == 2


def test_stage_reruns_on_param_change(tmp_path):
    inp = tmp_path / "in.txt"
    inp.write_text("hello")
    out = tmp_path / "out.txt"
    calls = {"n": 0}

    def work():
        calls["n"] += 1
        out.write_text("done")

    staging.stage("s3", [inp], [out], {"p": 1}, work, marker_dir=tmp_path / "m")
    r = staging.stage("s3", [inp], [out], {"p": 2}, work, marker_dir=tmp_path / "m")
    assert not r.skipped and calls["n"] == 2


def test_stage_reruns_when_output_deleted(tmp_path):
    """Simulate interruption: output vanished after marker written."""
    inp = tmp_path / "in.txt"
    inp.write_text("hello")
    out = tmp_path / "out.txt"
    calls = {"n": 0}

    def work():
        calls["n"] += 1
        out.write_text("done")

    staging.stage("s4", [inp], [out], {"p": 1}, work, marker_dir=tmp_path / "m")
    out.unlink()  # interruption / partial state
    r = staging.stage("s4", [inp], [out], {"p": 1}, work, marker_dir=tmp_path / "m")
    assert not r.skipped and calls["n"] == 2


def test_missing_output_raises(tmp_path):
    inp = tmp_path / "in.txt"
    inp.write_text("x")
    out = tmp_path / "never.txt"

    def noop():
        pass

    try:
        staging.stage("s5", [inp], [out], {}, noop, marker_dir=tmp_path / "m")
        assert False, "expected RuntimeError"
    except RuntimeError as e:
        assert "did not produce outputs" in str(e)
