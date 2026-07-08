# Local LLMs for Country Development Intelligence and Evaluation

This project analyses the UN Human Development Report for North Macedonia using local LLMs. It extracts report text, segments it into chapters and chunks, generates structured development intelligence, evaluates model outputs with a second model, and builds an interactive dashboard with the required visualisations.

## What the project does

- Reads and cleans the assigned PDF report: `data/raw/macedonia2004en.pdf`
- Produces report-level key findings and chapter summaries under 100 words
- Extracts themes for education, health, inequality, economy, gender, climate, and employment
- Extracts strengths, challenges, numerical indicators, and time-based values as JSON
- Compares outputs from multiple local LLMs
- Evaluates consistency, completeness, and factual alignment using a separate evaluator model
- Generates dashboard-ready files and plots
- Provides a Streamlit dashboard with at least four charts, including an advanced radar chart

## Repository structure

```text
.
├── config/
│   ├── settings.json
│   └── settings.yaml
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   │   └── macedonia2004en.pdf
│   └── processed/
├── prompts/
│   ├── extraction_prompt.md
│   ├── evaluation_prompt.md
│   └── summarisation_prompt.md
├── src/
│   └── country_dev_intel/
│       ├── cli.py
│       ├── dashboard_data.py
│       ├── evaluation.py
│       ├── extraction.py
│       ├── llm.py
│       ├── pdf_pipeline.py
│       ├── schemas.py
│       ├── themes.py
│       └── visualisations.py
└── tests/
```

## Requirements

Python 3.10 or later is recommended.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests after installing dependencies:

```bash
python -m pytest
```

The LLM workflow is designed for Ollama. Install Ollama and pull at least two local models, for example:

```bash
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

## Run the full pipeline

```bash
python -m country_dev_intel.cli run --config config/settings.json
```

If Ollama is not running, the pipeline still produces deterministic baseline outputs using rule-based extraction. This makes the code testable by markers even before local models are configured.

## Launch the dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard reads files from `data/processed/` and shows:

- Theme distribution
- Model comparison scores
- Numerical indicator comparison
- Time-based trend values
- Radar chart of development indicators
- Strengths and challenges extracted from the report

## Main outputs

After running the pipeline, the important files are:

- `data/processed/report_text.txt`
- `data/processed/chunks.json`
- `data/processed/chapter_summaries.json`
- `data/processed/theme_counts.json`
- `data/processed/model_outputs.json`
- `data/processed/evaluations.json`
- `data/processed/dashboard_data.json`

## Notes for the final report

The final written report should cite the UN report and describe:

- The PDF parsing and cleaning approach
- Prompt design and why separate extraction and evaluation models were used
- The extracted indicators, strengths, challenges, and theme distributions
- The model comparison findings
- Dashboard interpretation and limitations
