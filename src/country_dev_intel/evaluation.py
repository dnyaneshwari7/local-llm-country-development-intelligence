from __future__ import annotations

import json
from pathlib import Path

from .llm import OllamaClient, parse_json_response


def evaluate_outputs(
    full_text: str,
    outputs: list[dict],
    evaluator_model: str,
    client: OllamaClient | None,
    prompt_path: Path,
    temperature: float,
) -> list[dict]:
    prompt_template = prompt_path.read_text(encoding="utf-8")
    source = full_text[:24000]
    evaluations: list[dict] = []
    for output in outputs:
        if client:
            prompt = prompt_template.replace("{source_text}", source).replace(
                "{candidate_output}",
                json.dumps(output, indent=2),
            )
            try:
                data = parse_json_response(client.generate(evaluator_model, prompt, temperature))
                data["evaluated_model"] = output.get("model_name", "unknown")
            except Exception as exc:
                data = fallback_evaluation(output, str(exc))
        else:
            data = fallback_evaluation(output)
        evaluations.append(data)
    return evaluations


def fallback_evaluation(output: dict, error: str | None = None) -> dict:
    strengths = len(output.get("key_strengths", []))
    challenges = len(output.get("key_challenges", []))
    indicators = output.get("indicators", {})
    available_indicators = sum(value is not None for value in indicators.values())
    time_series = len(output.get("time_series", []))

    completeness = min(10, 2 + strengths + challenges + available_indicators + min(time_series, 3))
    factual_alignment = 6 if output.get("notes", "").lower().startswith("rule-based") else 7
    consistency = 8
    usefulness = min(10, 4 + available_indicators + min(time_series, 4))
    overall = round((completeness + factual_alignment + consistency + usefulness) / 4, 2)

    issues = []
    if available_indicators < 3:
        issues.append("Several headline indicators were not found directly in the extracted text.")
    if time_series < 3:
        issues.append("Few clean time-based values were available for plotting.")
    if error:
        issues.append(f"LLM evaluator unavailable: {error}")

    return {
        "evaluated_model": output.get("model_name", "unknown"),
        "consistency_score": consistency,
        "completeness_score": completeness,
        "factual_alignment_score": factual_alignment,
        "usefulness_score": usefulness,
        "overall_score": overall,
        "main_issues": issues,
        "recommended_improvements": [
            "Run the extraction with local LLMs through Ollama for richer narrative outputs.",
            "Manually verify key numerical indicators against the PDF tables before final report submission.",
        ],
    }
