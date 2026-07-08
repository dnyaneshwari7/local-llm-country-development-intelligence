from __future__ import annotations

import re
from collections import Counter


def count_themes(text: str, theme_terms: dict[str, list[str]]) -> dict[str, int]:
    lower_text = text.lower()
    counts: dict[str, int] = {}
    for theme, terms in theme_terms.items():
        count = 0
        for term in terms:
            count += len(re.findall(rf"\b{re.escape(term.lower())}\b", lower_text))
        counts[theme] = count
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def top_terms(text: str, limit: int = 30) -> list[dict]:
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", text.lower())
    stopwords = {
        "that",
        "with",
        "from",
        "this",
        "have",
        "were",
        "their",
        "which",
        "development",
        "human",
        "report",
        "macedonia",
    }
    counts = Counter(word for word in words if word not in stopwords)
    return [{"term": term, "count": count} for term, count in counts.most_common(limit)]

