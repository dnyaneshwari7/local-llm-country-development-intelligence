from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from country_dev_intel.visualisations import (  # noqa: E402
    indicator_comparison,
    model_scores,
    radar_chart,
    theme_distribution,
    time_series_plot,
)


st.set_page_config(page_title="Country Development Intelligence", layout="wide")

data_path = PROJECT_ROOT / "data" / "processed" / "dashboard_data.json"
st.title("North Macedonia Development Intelligence")
st.caption("Local LLM extraction, evaluation, and visualisation from the assigned UN report.")

if not data_path.exists():
    st.warning("Run the pipeline first: python -m country_dev_intel.cli run --config config/settings.json")
    st.stop()

data = json.loads(data_path.read_text(encoding="utf-8"))

score_rows = data.get("model_evaluations", [])
if score_rows:
    best_model = max(score_rows, key=lambda row: row["overall_score"])
    st.metric("Highest scoring model", best_model["evaluated_model"], f"{best_model['overall_score']}/10")

left, right = st.columns(2)
with left:
    st.plotly_chart(theme_distribution(data["theme_counts"]), use_container_width=True)
with right:
    st.plotly_chart(model_scores(score_rows), use_container_width=True)

left, right = st.columns(2)
with left:
    st.plotly_chart(indicator_comparison(data["indicator_rows"]), use_container_width=True)
with right:
    st.plotly_chart(time_series_plot(data["time_series_rows"]), use_container_width=True)

st.plotly_chart(radar_chart(data["radar_values"]), use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Key Strengths")
    for item in data.get("key_strengths", []):
        st.markdown(f"- **{item['item']}**")
with right:
    st.subheader("Key Challenges")
    for item in data.get("key_challenges", []):
        st.markdown(f"- **{item['item']}**")

with st.expander("Chapter summaries"):
    for chapter in data.get("chapter_summaries", []):
        st.markdown(f"**{chapter['chapter_title']}**")
        st.write(chapter["summary_under_100_words"])
