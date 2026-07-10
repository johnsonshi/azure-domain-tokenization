"""Markdown extraction, segmentation, and rule-based content-type classification
(plan.md §10).

Produces reader-visible *segments* from Markdown, removing front matter and
known generated/navigation boilerplate, and classifies each segment into the
controlled ``content_type`` vocabulary. Downstream code builds four corpus
representations from these segments: raw, semantic-full, prose-only, and
technical-syntax-only.

The extractor is deliberately rule-based (no ML) so its behaviour is fully
auditable; every segment records the rule that classified it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# --------------------------------------------------------------------------- #
# Patterns
# --------------------------------------------------------------------------- #
_FENCE_RE = re.compile(r"^(?P<indent>\s*)(?P<fence>`{3,}|~{3,})[ \t]*(?P<lang>[^\s`]*)[ \t]*$")
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<text>.*?)\s*#*\s*$")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|\-]+\|?\s*$")
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Microsoft Docs triple-colon extensions (moniker/zone/row/column/image/code/form)
_TRIPLE_COLON_RE = re.compile(r"^\s*:::.*$")
_INCLUDE_RE = re.compile(r"^\s*\[!INCLUDE\b.*?\]\s*\(?.*?\)?\s*$", re.IGNORECASE)
_ALERT_MARKER_RE = re.compile(r"^\s*>\s*\[!(NOTE|TIP|IMPORTANT|CAUTION|WARNING)\]\s*$", re.IGNORECASE)
_MDLINT_RE = re.compile(r"^\s*<!--\s*markdownlint.*?-->\s*$", re.IGNORECASE)

# Content classification helpers
_URL_RE = re.compile(r"^(https?://|ftp://|www\.)", re.IGNORECASE)
_PATH_RE = re.compile(r"^[~./]?([\w.-]+/){1,}[\w.-]*$")
_RESOURCE_PROVIDER_RE = re.compile(r"^Microsoft\.[A-Za-z][\w.]+")
_ENV_VAR_RE = re.compile(r"^\$?[A-Z][A-Z0-9_]{2,}$")
_JSON_START_RE = re.compile(r"^\s*[{\[]")
_YAML_KEY_RE = re.compile(r"^\s*[\w.-]+:\s")
_CLI_TOKENS = ("az ", "azcopy", "kubectl ", "helm ", "docker ", "git ", "curl ",
               "apt ", "brew ", "npm ", "pip ", "dotnet ", "func ", "terraform ")
_PS_TOKENS = ("Get-", "Set-", "New-", "Remove-", "Add-", "Import-", "Export-",
              "Install-", "$PSVersionTable", "Write-Host", "-ResourceGroupName")


@dataclass
class ExtractedSegment:
    content_type: str
    text: str
    lang: str = ""
    classifier_rule: str = ""
    confidence: float = 1.0


@dataclass
class CleaningReport:
    front_matter_removed: bool = False
    html_comments_removed: int = 0
    include_directives_removed: int = 0
    triple_colon_markers_removed: int = 0
    alert_markers_removed: int = 0
    segments: int = 0
    by_type: dict[str, int] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Front matter + boilerplate
# --------------------------------------------------------------------------- #
def strip_front_matter(md: str) -> tuple[str, bool]:
    """Remove a leading YAML front-matter block delimited by ``---`` lines."""
    if not md.startswith("---"):
        return md, False
    lines = md.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n\r") != "---":
        return md, False
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n\r") in ("---", "..."):
            return "".join(lines[i + 1 :]), True
    return md, False


def _classify_fence(lang: str, content: str) -> tuple[str, str, float]:
    """Return (content_type, rule, confidence) for a fenced code block."""
    lang_l = lang.strip().lower()
    mapping = {
        "json": "json", "jsonc": "json",
        "yaml": "yaml", "yml": "yaml",
        "powershell": "powershell", "pwsh": "powershell", "ps": "powershell",
        "ps1": "powershell", "azurepowershell": "powershell",
        "bicep": "bicep",
    }
    if lang_l in mapping:
        return mapping[lang_l], f"fence_lang:{lang_l}", 1.0
    cli_langs = {"bash", "sh", "shell", "shellscript", "console", "cmd", "bat",
                 "terminal", "azurecli", "cli", "azcli"}
    if lang_l in cli_langs:
        return "cli", f"fence_lang:{lang_l}", 1.0
    if lang_l:
        return "code", f"fence_lang:{lang_l}", 1.0
    # No language tag -> content heuristics
    stripped = content.strip()
    if _JSON_START_RE.match(stripped) and stripped.rstrip().endswith(("}", "]")):
        return "json", "fence_heuristic:json", 0.7
    lines = [ln for ln in content.splitlines() if ln.strip()]
    if lines and all(_YAML_KEY_RE.match(ln) or ln.strip().startswith("-") for ln in lines):
        return "yaml", "fence_heuristic:yaml", 0.6
    if any(t in content for t in _PS_TOKENS):
        return "powershell", "fence_heuristic:powershell", 0.6
    if any(t in content for t in _CLI_TOKENS) or stripped.startswith(("$", "#!", "> ")):
        return "cli", "fence_heuristic:cli", 0.6
    return "code", "fence_heuristic:code", 0.5


def _classify_inline(token: str) -> tuple[str, str, float]:
    t = token.strip()
    if _URL_RE.match(t) or _RESOURCE_PROVIDER_RE.match(t) or _PATH_RE.match(t) or _ENV_VAR_RE.match(t):
        return "url_path", "inline_url_path", 0.8
    return "inline_code", "inline_code", 1.0


# --------------------------------------------------------------------------- #
# Main extraction
# --------------------------------------------------------------------------- #
def extract_segments(md: str, report: CleaningReport | None = None) -> list[ExtractedSegment]:
    """Parse Markdown into classified, reader-visible segments."""
    report = report or CleaningReport()

    body, fm = strip_front_matter(md)
    report.front_matter_removed = fm

    # Remove HTML comments (build directives invisible to readers).
    n_comments = len(_HTML_COMMENT_RE.findall(body))
    report.html_comments_removed += n_comments
    body = _HTML_COMMENT_RE.sub("", body)

    segments: list[ExtractedSegment] = []
    lines = body.splitlines()
    i = 0
    n = len(lines)
    prose_buf: list[str] = []

    def flush_prose() -> None:
        if not prose_buf:
            return
        text = "\n".join(prose_buf).strip()
        prose_buf.clear()
        if not text:
            return
        # Extract inline code spans as their own segments; keep surrounding prose.
        last = 0
        prose_pieces: list[str] = []
        for m in _INLINE_CODE_RE.finditer(text):
            prose_pieces.append(text[last : m.start()])
            ctype, rule, conf = _classify_inline(m.group(1))
            segments.append(ExtractedSegment(ctype, m.group(1), "", rule, conf))
            last = m.end()
        prose_pieces.append(text[last:])
        prose_text = "".join(prose_pieces).strip()
        if prose_text:
            segments.append(ExtractedSegment("prose", prose_text, "", "paragraph", 1.0))

    while i < n:
        line = lines[i]

        # Fenced code block
        fm_match = _FENCE_RE.match(line)
        if fm_match:
            flush_prose()
            fence = fm_match.group("fence")[0]
            fence_len = len(fm_match.group("fence"))
            lang = fm_match.group("lang")
            j = i + 1
            content_lines: list[str] = []
            closed = False
            while j < n:
                close = re.match(rf"^\s*{re.escape(fence)}{{{fence_len},}}\s*$", lines[j])
                if close:
                    closed = True
                    break
                content_lines.append(lines[j])
                j += 1
            content = "\n".join(content_lines)
            ctype, rule, conf = _classify_fence(lang, content)
            if content.strip():
                segments.append(ExtractedSegment(ctype, content, lang, rule, conf))
            i = j + 1 if closed else j
            continue

        # Heading
        h = _HEADING_RE.match(line)
        if h and line.lstrip().startswith("#"):
            flush_prose()
            text = h.group("text").strip()
            if text:
                segments.append(ExtractedSegment("heading", text, "", "heading", 1.0))
            i += 1
            continue

        # Table (row followed by rows; skip separator rows)
        if _TABLE_ROW_RE.match(line):
            flush_prose()
            j = i
            cells: list[str] = []
            while j < n and _TABLE_ROW_RE.match(lines[j]):
                if not _TABLE_SEP_RE.match(lines[j]) or "-" not in lines[j].replace("|", ""):
                    row_cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    cells.extend(c for c in row_cells if c and not set(c) <= {"-", ":", " "})
                j += 1
            text = " ".join(cells).strip()
            if text:
                segments.append(ExtractedSegment("table", text, "", "table", 1.0))
            i = j
            continue

        # Boilerplate / directive lines
        if _TRIPLE_COLON_RE.match(line):
            report.triple_colon_markers_removed += 1
            i += 1
            continue
        if _INCLUDE_RE.match(line):
            report.include_directives_removed += 1
            i += 1
            continue
        if _ALERT_MARKER_RE.match(line):
            report.alert_markers_removed += 1
            i += 1
            continue

        # Blank line ends a paragraph
        if not line.strip():
            flush_prose()
            i += 1
            continue

        # Ordinary prose / list / blockquote line: strip leading markers
        cleaned = re.sub(r"^\s{0,3}(>+\s?|[-*+]\s+|\d+\.\s+)", "", line)
        prose_buf.append(cleaned)
        i += 1

    flush_prose()

    report.segments = len(segments)
    for s in segments:
        report.by_type[s.content_type] = report.by_type.get(s.content_type, 0) + 1
    return segments


# --------------------------------------------------------------------------- #
# Corpus representations (plan.md §10)
# --------------------------------------------------------------------------- #
_TECHNICAL = frozenset({"code", "cli", "json", "yaml", "powershell", "bicep", "url_path", "inline_code"})
_PROSE = frozenset({"prose", "heading", "table"})


def to_representation(segments: list[ExtractedSegment], kind: str) -> str:
    """Join segments into one of: raw, semantic_full, prose_only, technical_syntax."""
    if kind == "semantic_full":
        keep = [s for s in segments]
    elif kind == "prose_only":
        keep = [s for s in segments if s.content_type in _PROSE]
    elif kind == "technical_syntax":
        keep = [s for s in segments if s.content_type in _TECHNICAL]
    elif kind == "raw":
        keep = list(segments)
    else:
        raise ValueError(f"unknown representation {kind!r}")
    return "\n\n".join(s.text for s in keep if s.text.strip())
