from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dashboard_data import build_dashboard_data, write_dashboard_data
from .evaluation import evaluate_outputs
from .extraction import extract_with_models, save_json, summarise_chapters
from .llm import OllamaClient
from .pdf_pipeline import save_text_artifacts
from .schemas import validate_evaluations, validate_extractions
from .themes import count_themes, top_terms


def run_pipeline(config_path: Path) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parent.parent
    pdf_path = root / config["project"]["pdf_path"]
    output_dir = root / config["project"]["output_dir"]
    prompts_dir = root / "prompts"

    text_artifacts = save_text_artifacts(
        pdf_path,
        output_dir,
        max_words=config["chunking"]["max_words"],
        overlap_words=config["chunking"]["overlap_words"],
    )
    full_text = text_artifacts["text"]
    theme_counts = count_themes(full_text, config["themes"])
    save_json(output_dir / "theme_counts.json", theme_counts)
    save_json(output_dir / "top_terms.json", top_terms(full_text))

    client = make_client(config)
    extraction_models = config["llm"]["extraction_models"]
    temperature = config["llm"]["temperature"]
    chapter_model = extraction_models[0]

    chapter_summaries = summarise_chapters(
        text_artifacts["chapters"],
        chapter_model,
        client,
        prompts_dir / "summarisation_prompt.md",
        temperature,
    )
    save_json(output_dir / "chapter_summaries.json", chapter_summaries)

    model_outputs = extract_with_models(
        full_text,
        extraction_models,
        client,
        prompts_dir / "extraction_prompt.md",
        temperature,
    )
    model_outputs = validate_extractions(model_outputs)
    save_json(output_dir / "model_outputs.json", model_outputs)

    evaluations = evaluate_outputs(
        full_text,
        model_outputs,
        config["llm"]["evaluator_model"],
        client,
        prompts_dir / "evaluation_prompt.md",
        temperature,
    )
    evaluations = validate_evaluations(evaluations)
    save_json(output_dir / "evaluations.json", evaluations)

    dashboard_data = build_dashboard_data(theme_counts, model_outputs, evaluations, chapter_summaries)
    write_dashboard_data(output_dir / "dashboard_data.json", dashboard_data)
    print(json.dumps({"status": "complete", "output_dir": str(output_dir)}, indent=2))


def make_client(config: dict) -> OllamaClient | None:
    if config["llm"].get("provider") != "ollama":
        return None
    client = OllamaClient(
        base_url=config["llm"]["base_url"],
        timeout_seconds=config["llm"]["timeout_seconds"],
    )
    return client if client.is_available() else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Country development intelligence pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run the full PDF to dashboard-data pipeline")
    run_parser.add_argument("--config", type=Path, default=Path("config/settings.json"))
    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(args.config)


if __name__ == "__main__":
    main()
