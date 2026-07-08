from __future__ import annotations

INDICATOR_KEYS = [
    "hdi_value",
    "hdi_rank",
    "life_expectancy_years",
    "expected_years_schooling",
    "mean_years_schooling",
    "gni_per_capita",
    "population",
]


def validate_extractions(rows: list[dict]) -> list[dict]:
    validated = []
    for row in rows:
        indicators = row.get("indicators") or {}
        validated.append(
            {
                "country": row.get("country", "North Macedonia"),
                "model_name": str(row.get("model_name", "unknown")),
                "key_strengths": normalise_evidence_items(row.get("key_strengths", [])),
                "key_challenges": normalise_evidence_items(row.get("key_challenges", [])),
                "indicators": {key: indicators.get(key) for key in INDICATOR_KEYS},
                "time_series": normalise_time_series(row.get("time_series", [])),
                "notes": str(row.get("notes", "")),
            }
        )
    return validated


def validate_evaluations(rows: list[dict]) -> list[dict]:
    return [
        {
            "evaluated_model": str(row.get("evaluated_model", "unknown")),
            "consistency_score": float(row.get("consistency_score", 0)),
            "completeness_score": float(row.get("completeness_score", 0)),
            "factual_alignment_score": float(row.get("factual_alignment_score", 0)),
            "usefulness_score": float(row.get("usefulness_score", 0)),
            "overall_score": float(row.get("overall_score", 0)),
            "main_issues": list(row.get("main_issues", [])),
            "recommended_improvements": list(row.get("recommended_improvements", [])),
        }
        for row in rows
    ]


def normalise_evidence_items(rows: list) -> list[dict]:
    output = []
    for row in rows:
        if isinstance(row, str):
            output.append({"item": row, "evidence": ""})
        elif isinstance(row, dict):
            output.append({"item": str(row.get("item", "")), "evidence": str(row.get("evidence", ""))})
    return output


def normalise_time_series(rows: list) -> list[dict]:
    output = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            output.append(
                {
                    "name": str(row.get("name", "time_based_quantity")),
                    "year": int(row.get("year")),
                    "value": float(row.get("value")),
                    "unit": str(row.get("unit", "")),
                    "source_phrase": str(row.get("source_phrase", "")),
                }
            )
        except (TypeError, ValueError):
            continue
    return output
