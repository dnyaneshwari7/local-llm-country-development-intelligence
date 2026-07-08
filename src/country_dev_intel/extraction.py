from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .llm import OllamaClient, parse_json_response


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def summarise_chapters(
    chapters: list[dict],
    model: str,
    client: OllamaClient | None,
    prompt_path: Path,
    temperature: float,
) -> list[dict]:
    prompt_template = load_prompt(prompt_path)
    summaries: list[dict] = []
    for chapter in chapters:
        source = chapter["text"][:9000]
        if client:
            prompt = prompt_template.replace("{source_text}", source)
            try:
                data = parse_json_response(client.generate(model, prompt, temperature))
            except Exception as exc:
                data = fallback_chapter_summary(chapter, str(exc))
        else:
            data = fallback_chapter_summary(chapter)
        summaries.append(data)
    return summaries


def extract_with_models(
    full_text: str,
    models: list[str],
    client: OllamaClient | None,
    prompt_path: Path,
    temperature: float,
) -> list[dict]:
    prompt_template = load_prompt(prompt_path)
    outputs: list[dict] = []
    source = full_text[:24000]
    for model in models:
        if client:
            prompt = prompt_template.replace("{source_text}", source)
            try:
                data = parse_json_response(client.generate(model, prompt, temperature))
                data["model_name"] = model
            except Exception as exc:
                data = fallback_extraction(full_text, model, str(exc))
        else:
            data = fallback_extraction(full_text, model)
        outputs.append(data)
    return outputs


def fallback_chapter_summary(chapter: dict, error: str | None = None) -> dict:
    words = chapter["text"].split()
    summary = " ".join(words[:85])
    result = {
        "chapter_title": chapter["chapter_title"],
        "summary_under_100_words": summary,
        "key_points": sentence_points(chapter["text"], 3),
    }
    if error:
        result["fallback_reason"] = error
    return result


def fallback_extraction(text: str, model_name: str, error: str | None = None) -> dict[str, Any]:
    strengths = [
        "Human development is treated as a multidimensional policy priority.",
        "The report includes education, health, income, and social inclusion evidence.",
        "The document provides quantitative material suitable for dashboard visualisation.",
        "Institutional reform and development planning are discussed across the report.",
        "The source includes references to vulnerable groups and regional disparities.",
    ]
    challenges = [
        "Poverty and exclusion remain recurring development concerns.",
        "Unemployment and labour-market weakness are repeatedly discussed.",
        "Regional and social inequalities require targeted policy responses.",
        "Some indicators are embedded in narrative text rather than clean tables.",
        "Evidence quality depends on the PDF extraction quality and historical data availability.",
    ]
    result = {
        "country": "North Macedonia",
        "model_name": model_name,
        "key_strengths": [{"item": item, "evidence": find_evidence(text, item)} for item in strengths],
        "key_challenges": [{"item": item, "evidence": find_evidence(text, item)} for item in challenges],
        "indicators": extract_indicator_candidates(text),
        "time_series": extract_time_series_candidates(text),
        "notes": "Rule-based fallback output. Run Ollama for richer LLM-generated extraction.",
    }
    if error:
        result["llm_error"] = error
    return result


def extract_indicator_candidates(text: str) -> dict[str, float | int | str | None]:
    patterns = {
        "hdi_value": r"HDI[^0-9]{0,30}([0-9]\.[0-9]{2,3})",
        "hdi_rank": r"rank(?:ed)?[^0-9]{0,30}([0-9]{1,3})",
        "life_expectancy_years": r"life expectancy[^0-9]{0,40}([0-9]{2}\.?[0-9]?)",
        "population": r"population[^0-9]{0,40}([0-9]+(?:\.[0-9]+)?\s*(?:million|thousand)?)",
    }
    indicators: dict[str, float | int | str | None] = {
        "hdi_value": None,
        "hdi_rank": None,
        "life_expectancy_years": None,
        "expected_years_schooling": None,
        "mean_years_schooling": None,
        "gni_per_capita": None,
        "population": None,
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            indicators[key] = match.group(1).strip() if key == "population" else parse_number_or_text(match.group(1))
    return indicators


def extract_time_series_candidates(text: str, limit: int = 25) -> list[dict]:
    pattern = re.compile(
        r"(?P<year>19[8-9][0-9]|20[0-2][0-9])[^.\n]{0,90}?(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>%|percent|million|thousand|years|USD)?",
        flags=re.IGNORECASE,
    )
    rows: list[dict] = []
    for match in pattern.finditer(text):
        rows.append(
            {
                "name": "candidate_time_based_quantity",
                "year": int(match.group("year")),
                "value": float(match.group("value")),
                "unit": match.group("unit") or "",
                "source_phrase": match.group(0)[:180],
            }
        )
        if len(rows) >= limit:
            break
    return rows


def sentence_points(text: str, limit: int) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if len(sentence.split()) > 8][:limit]


def find_evidence(text: str, item: str) -> str:
    keywords = [word for word in re.findall(r"[A-Za-z]{5,}", item.lower())[:3]]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in keywords):
            return sentence[:240]
    return ""


def parse_number_or_text(value: str) -> float | int | str:
    cleaned = value.replace(",", "").strip()
    try:
        number = float(cleaned.split()[0])
    except ValueError:
        return value
    return int(number) if number.is_integer() else number


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
