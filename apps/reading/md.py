"""Reading app utilities."""

import html
import re


_HEADING_RE  = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
_BOLD_RE     = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE   = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_CODE_RE     = re.compile(r"`([^`]+)`")
_FENCE_RE    = re.compile(r"```([\s\S]*?)```")
_ULIST_RE    = re.compile(r"(?:^[ \t]*[-*]\s+.+\n?)+", re.MULTILINE)
_OLIST_RE    = re.compile(r"(?:^[ \t]*\d+\.\s+.+\n?)+", re.MULTILINE)
_TABLE_RE    = re.compile(r"((?:^\|.*\|\n)+)", re.MULTILINE)


def markdown(text, extensions=None):
    """Tiny markdown subset → HTML. Headings, bold/italic, lists, code, tables."""
    if not text:
        return ""

    def _escape(s):
        return html.escape(s, quote=False)

    # fenced code
    def _fence(m):
        body = _escape(m.group(1))
        return f'<pre class="rounded-md bg-muted/60 px-3 py-2 text-xs overflow-x-auto"><code>{body}</code></pre>'

    out = _FENCE_RE.sub(_fence, text)

    # tables (| col | col |\n|---|---|\n| … |)
    def _table(m):
        block = m.group(1).strip().splitlines()
        if len(block) < 2 or not re.search(r"^\|?[\s:|-]+\|?$", block[1]):
            return m.group(0)
        head = [c.strip() for c in block[0].strip("|").split("|")]
        rows = [
            [c.strip() for c in ln.strip("|").split("|")]
            for ln in block[2:]
        ]
        th = "".join(f"<th class='px-2 py-1 text-left'>{_escape(h)}</th>" for h in head)
        trs = "".join(
            "<tr class='border-t border-border'>" +
            "".join(f"<td class='px-2 py-1'>{_escape(c)}</td>" for c in r) +
            "</tr>"
            for r in rows
        )
        return f"<table class='text-sm my-3 border border-border rounded-md'><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"

    out = _TABLE_RE.sub(_table, out)

    # headings
    def _heading(m):
        level = len(m.group(1))
        body = _inline(m.group(2))
        size = {1: "text-2xl", 2: "text-xl", 3: "text-lg"}.get(level, "text-base")
        return f"<h{level} class='{size} font-bold tracking-tight mt-4 mb-2'>{body}</h{level}>"

    out = _HEADING_RE.sub(_heading, out)

    # lists (unordered)
    def _ulist(m):
        items = re.findall(r"^[ \t]*[-*]\s+(.+)$", m.group(0), re.MULTILINE)
        return "<ul class='list-disc pl-6 my-2'>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>"

    out = _ULIST_RE.sub(_ulist, out)

    # ordered
    def _olist(m):
        items = re.findall(r"^[ \t]*\d+\.\s+(.+)$", m.group(0), re.MULTILINE)
        return "<ol class='list-decimal pl-6 my-2'>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ol>"

    out = _OLIST_RE.sub(_olist, out)

    # paragraphs (anything separated by blank lines that isn't already wrapped in a block)
    parts = re.split(r"\n{2,}", out)
    rendered = []
    block_re = re.compile(r"^\s*<(h\d|ul|ol|table|pre|blockquote)")
    for p in parts:
        if block_re.match(p):
            rendered.append(p)
        else:
            rendered.append(f"<p class='my-2 leading-relaxed'>{_inline(p.replace(chr(10), ' ').strip())}</p>")
    return "\n".join(rendered)


def _inline(text):
    text = _BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = _ITALIC_RE.sub(r"<em>\1</em>", text)
    text = _CODE_RE.sub(r"<code class='rounded bg-muted/60 px-1'>\1</code>", text)
    return text
