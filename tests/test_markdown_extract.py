"""Markdown extraction: front matter, code fences, inline code, tables,
classification, and representations (plan.md §23)."""
from __future__ import annotations

from msdocs_tokenizer import markdown_extract as mx


def test_front_matter_removed(azure_md):
    body, removed = mx.strip_front_matter(azure_md)
    assert removed is True
    assert "ms.service: container-registry" not in body
    assert "Deploy a container" in body


def test_front_matter_absent():
    body, removed = mx.strip_front_matter("# Just a heading\n\ntext")
    assert removed is False
    assert body.startswith("# Just a heading")


def test_code_fence_extracted_and_classified(azure_md):
    segs = mx.extract_segments(azure_md)
    json_segs = [s for s in segs if s.content_type == "json"]
    cli_segs = [s for s in segs if s.content_type == "cli"]
    assert json_segs, "expected a json fenced block"
    assert '"adminUserEnabled": false' in json_segs[0].text
    assert cli_segs, "expected a cli fenced block"
    assert "az acr create" in cli_segs[0].text


def test_powershell_yaml_bicep_classified(automation_md):
    segs = mx.extract_segments(automation_md)
    types = {s.content_type for s in segs}
    assert "powershell" in types
    assert "yaml" in types
    assert "bicep" in types


def test_inline_code_extracted(azure_md):
    segs = mx.extract_segments(azure_md)
    inline = [s for s in segs if s.content_type in ("inline_code", "url_path")]
    texts = [s.text for s in inline]
    assert any("az acr" in t for t in texts)
    # Resource provider recognised as url_path
    assert any(t == "Microsoft.ContainerRegistry" for t in texts)


def test_table_extracted(azure_md):
    segs = mx.extract_segments(azure_md)
    tables = [s for s in segs if s.content_type == "table"]
    assert tables, "expected a table segment"
    text = tables[0].text
    assert "Premium" in text and "SKU" in text
    # Separator row (---) must not leak into the extracted text
    assert "---" not in text


def test_html_comment_removed(azure_md):
    report = mx.CleaningReport()
    segs = mx.extract_segments(azure_md, report)
    joined = " ".join(s.text for s in segs)
    assert "build directive" not in joined
    assert report.html_comments_removed >= 1


def test_headings_extracted(azure_md):
    segs = mx.extract_segments(azure_md)
    headings = [s.text for s in segs if s.content_type == "heading"]
    assert any("Prerequisites" in h for h in headings)
    assert all(not h.startswith("#") for h in headings)


def test_representations(azure_md):
    segs = mx.extract_segments(azure_md)
    semantic = mx.to_representation(segs, "semantic_full")
    prose = mx.to_representation(segs, "prose_only")
    tech = mx.to_representation(segs, "technical_syntax")

    # Prose keeps natural language, excludes fenced code blocks.
    assert "Azure Container Registry stores" in prose
    assert '"adminUserEnabled": false' not in prose
    # Technical syntax keeps code, excludes pure prose sentences.
    assert '"adminUserEnabled": false' in tech
    assert "Azure Container Registry stores" not in tech
    # Semantic full keeps both.
    assert "Azure Container Registry stores" in semantic
    assert "az acr create" in semantic
