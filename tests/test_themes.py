from country_dev_intel.themes import count_themes


def test_count_themes_counts_configured_terms() -> None:
    text = "Education and health improve development. Unemployment remains an employment issue."
    themes = {
        "education": ["education", "school"],
        "health": ["health"],
        "employment": ["employment", "unemployment"],
    }
    assert count_themes(text, themes) == {"employment": 2, "education": 1, "health": 1}

