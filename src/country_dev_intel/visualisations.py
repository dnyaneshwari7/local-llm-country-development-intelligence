from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def theme_distribution(theme_rows: list[dict]) -> go.Figure:
    df = pd.DataFrame(theme_rows)
    return px.bar(df, x="theme", y="count", title="Distribution of Development Themes")


def model_scores(evaluations: list[dict]) -> go.Figure:
    df = pd.DataFrame(evaluations)
    if df.empty:
        return go.Figure()
    return px.bar(
        df,
        x="evaluated_model",
        y=["consistency_score", "completeness_score", "factual_alignment_score", "usefulness_score"],
        barmode="group",
        title="Cross-LLM Evaluation Scores",
    )


def indicator_comparison(rows: list[dict]) -> go.Figure:
    df = pd.DataFrame(rows)
    if df.empty:
        return go.Figure()
    return px.bar(df, x="indicator", y="value", color="model", barmode="group", title="Numerical Indicator Comparison")


def time_series_plot(rows: list[dict]) -> go.Figure:
    df = pd.DataFrame(rows)
    if df.empty:
        return go.Figure()
    return px.scatter(
        df,
        x="year",
        y="value",
        color="model",
        hover_data=["unit", "source_phrase"],
        title="Extracted Time-Based Quantities",
    )


def radar_chart(rows: list[dict]) -> go.Figure:
    df = pd.DataFrame(rows)
    if df.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=df["score"],
            theta=df["dimension"],
            fill="toself",
            name="Development intelligence profile",
        )
    )
    fig.update_layout(
        title="Radar Profile of Extracted Development Intelligence",
        polar={"radialaxis": {"visible": True, "range": [0, 10]}},
        showlegend=False,
    )
    return fig

