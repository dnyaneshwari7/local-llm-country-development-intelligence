from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any


def build_dashboard_data(
    theme_counts: dict[str, int],
    model_outputs: list[dict],
    evaluations: list[dict],
    chapter_summaries: list[dict],
) -> dict[str, Any]:
    indicator_rows = []
    for output in model_outputs:
        model = output["model_name"]
        for indicator, value in output.get("indicators", {}).items():
            if value is not None:
                indicator_rows.append({"model": model, "indicator": indicator, "value": value})

    time_series_rows = []
    for output in model_outputs:
        for row in output.get("time_series", []):
            time_series_rows.append({"model": output["model_name"], **row})

    first_output = model_outputs[0] if model_outputs else {}
    radar = make_radar_values(theme_counts, evaluations, indicator_rows, time_series_rows)

    return {
        "theme_counts": [{"theme": key, "count": value} for key, value in theme_counts.items()],
        "model_evaluations": evaluations,
        "indicator_rows": indicator_rows,
        "time_series_rows": time_series_rows,
        "radar_values": radar,
        "key_strengths": first_output.get("key_strengths", []),
        "key_challenges": first_output.get("key_challenges", []),
        "chapter_summaries": chapter_summaries,
    }


def make_radar_values(
    theme_counts: dict[str, int],
    evaluations: list[dict],
    indicator_rows: list[dict],
    time_series_rows: list[dict],
) -> list[dict]:
    max_theme = max(theme_counts.values()) if theme_counts else 1
    average_score = mean([row["overall_score"] for row in evaluations]) if evaluations else 0
    return [
        {"dimension": "Education signal", "score": scale(theme_counts.get("education", 0), max_theme)},
        {"dimension": "Health signal", "score": scale(theme_counts.get("health", 0), max_theme)},
        {"dimension": "Economy signal", "score": scale(theme_counts.get("economy", 0), max_theme)},
        {"dimension": "Inequality signal", "score": scale(theme_counts.get("inequality", 0), max_theme)},
        {"dimension": "Model quality", "score": average_score},
        {"dimension": "Indicator coverage", "score": min(10, len(indicator_rows))},
        {"dimension": "Trend coverage", "score": min(10, len(time_series_rows) / 3)},
    ]


def scale(value: float, max_value: float) -> float:
    if max_value <= 0:
        return 0
    return round((value / max_value) * 10, 2)


def write_dashboard_data(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

