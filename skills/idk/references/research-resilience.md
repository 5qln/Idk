# Research Resilience During the Cycle

When the human drops a search directive during Q-phase (or any phase), tool
limitations are common. This documents working fallback paths and the correct
pattern when blocked.

## Search Backend Priority

| Backend | URL / Access | Best For | Reliability |
|---------|-------------|----------|-------------|
| Semantic Scholar API | `api.semanticscholar.org/graph/v1/paper/search` | Academic papers, research findings | High (no captcha) |
| arXiv API | `export.arxiv.org/api/query` | Preprints, fast-moving research | High |
| Google News RSS | `news.google.com/rss/search` | Mainstream media sentiment | Medium (sometimes blocks) |
| DuckDuckGo HTML | `html.duckduckgo.com/html/` | General web search | Low (captcha-heavy) |
| Direct URLs | — | Specific articles | Variable (403 common on news sites) |

## Pattern: When Primary Search Fails

1. Start with DuckDuckGo HTML (fastest, broadest) — but expect captcha.
2. If captcha: switch to Semantic Scholar for academic findings + Google News RSS for sentiment.
3. If both partially blocked: arXiv API is the most reliable fallback for any research topic.
4. Do NOT fight a blocked backend. Move on immediately — three failed attempts in a row
   is tool-fighting, not research. The search serves the reflection, not the other way around.
5. Synthesize from whatever was found and return the open space. The human's φ is the
   shape of the findings, not the completeness of the search.

## Pattern: When Direct URLs Return 403/404

News sites and research outlets frequently block programmatic access. Alternatives:
- Wayback Machine: `web.archive.org/web/2025/<original-url>`
- Check if the study is also on arXiv or Semantic Scholar
- Work with what's extractable from RSS headlines and snippets

## Key: Don't Let Tool-Fighting Dominate the Void

If search tools are throttled or blocked after reasonable attempts, note what was
found and what was inaccessible. Ask whether the human wants to redirect. The
research supports the reflection — the reflection is the phase work, not the
search count.

## Pip Installation for Semantic Scholar (if not available)

```bash
pip install semanticscholar
```

But the REST API at `api.semanticscholar.org` works without any library — plain
`urllib.request` is sufficient.
