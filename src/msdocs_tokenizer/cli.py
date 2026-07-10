"""`msdocs-tok` command-line interface (plan.md §18, §22).

Each subcommand maps to a resumable pipeline stage and is safe to re-run.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import typer

from . import config, pipeline

app = typer.Typer(add_completion=False, help="Domain-specialized tokenizer efficiency study (CPU-only).")

DEFAULT_SOURCES = config.CONFIGS / "sources.yaml"


def _exp() -> dict:
    return pipeline.load_experiment()


@app.command()
def doctor() -> None:
    """Print environment + budget summary (see also scripts/doctor.sh)."""
    from .provenance import machine_metadata, package_versions
    typer.echo(json.dumps({
        "machine": machine_metadata(),
        "packages": package_versions(),
        "max_workers": config.max_workers(),
        "seed": config.GLOBAL_SEED,
        "root": str(config.ROOT),
    }, indent=2))


@app.command()
def inventory(out: Path = config.INVENTORY / "microsoftdocs_repos.json") -> None:
    """Fetch the MicrosoftDocs public repo inventory via `gh` and write CSV."""
    import pandas as pd
    out.parent.mkdir(parents=True, exist_ok=True)
    typer.echo("Fetching MicrosoftDocs public repos via gh api ...")
    proc = subprocess.run(
        ["gh", "api", "--paginate", "--slurp",
         "orgs/MicrosoftDocs/repos?per_page=100&type=public"],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise typer.Exit(code=1)
    pages = json.loads(proc.stdout)
    repos = [r for page in pages for r in (page if isinstance(page, list) else [page])]
    out.write_text(json.dumps(repos, indent=2))
    rows = [{
        "full_name": r.get("full_name"), "description": r.get("description"),
        "html_url": r.get("html_url"), "default_branch": r.get("default_branch"),
        "stargazers_count": r.get("stargazers_count"), "forks_count": r.get("forks_count"),
        "watchers_count": r.get("watchers_count"), "open_issues_count": r.get("open_issues_count"),
        "size_kb": r.get("size"), "language": r.get("language"),
        "license_spdx": (r.get("license") or {}).get("spdx_id"),
        "archived": r.get("archived"), "disabled": r.get("disabled"),
        "pushed_at": r.get("pushed_at"), "updated_at": r.get("updated_at"),
        "created_at": r.get("created_at"),
    } for r in repos]
    csv = config.INVENTORY / "repo_inventory.csv"
    pd.DataFrame(rows).to_csv(csv, index=False)
    typer.echo(f"Wrote {len(repos)} repos -> {out} and {csv}")


@app.command()
def acquire(profile: str = "pilot", sources: Path = DEFAULT_SOURCES, force: bool = False) -> None:
    """Acquire + pin sources (Azure anchor, transfer, external, general English)."""
    typer.echo(json.dumps(pipeline.run_acquire(profile, sources, force=force), indent=2))


@app.command()
def audit(profile: str = "pilot", force: bool = False) -> None:
    """Process, dedupe, split, and build byte-matched corpora."""
    typer.echo(json.dumps(pipeline.run_audit(profile, _exp(), force=force), indent=2))


@app.command()
def train(profile: str = "pilot", force: bool = False) -> None:
    """Train the controlled byte-level BPE tokenizers."""
    typer.echo(json.dumps(pipeline.run_train(profile, force=force), indent=2))


@app.command()
def evaluate(profile: str = "pilot", force: bool = False) -> None:
    """Evaluate Track A + Track B encoders on all frozen eval sets."""
    typer.echo(json.dumps(pipeline.run_evaluate(profile, _exp(), force=force), indent=2))


@app.command()
def benchmark(profile: str = "pilot", rounds: int = 5, force: bool = False) -> None:
    """Serialized CPU runtime benchmark."""
    typer.echo(json.dumps(pipeline.run_benchmark(profile, _exp(), force=force, rounds=rounds), indent=2))


@app.command()
def analyze(profile: str = "pilot", force: bool = False) -> None:
    """Paired bootstrap + figures with source tables."""
    typer.echo(json.dumps(pipeline.run_analyze(profile, _exp(), force=force), indent=2))


@app.command()
def report(profile: str = "pilot", force: bool = False) -> None:
    """Assemble FINAL_REPORT.md + notebooks."""
    typer.echo(json.dumps(pipeline.run_report(profile, _exp(), force=force), indent=2))


@app.command()
def verify(profile: str = "pilot") -> None:
    """Independent recomputation + gate checks. Exits nonzero on failure."""
    res = pipeline.run_verify(profile, _exp())
    typer.echo(json.dumps(res, indent=2))
    raise typer.Exit(code=0 if res["all_ok"] else 1)


@app.command("run-pilot")
def run_pilot(sources: Path = DEFAULT_SOURCES) -> None:
    """End-to-end pilot: acquire -> audit -> train -> evaluate -> analyze -> report -> verify."""
    profile = "pilot"
    pipeline.run_acquire(profile, sources)
    pipeline.run_audit(profile, _exp())
    pipeline.run_train(profile)
    pipeline.run_evaluate(profile, _exp())
    pipeline.run_analyze(profile, _exp())
    pipeline.run_report(profile, _exp())
    res = pipeline.run_verify(profile, _exp())
    typer.echo(json.dumps(res, indent=2))
    raise typer.Exit(code=0 if res["all_ok"] else 1)


if __name__ == "__main__":
    app()
