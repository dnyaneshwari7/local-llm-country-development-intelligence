You are extracting structured country development intelligence from a UN Human Development Report.

Use only the supplied source text. If a value is not present, return null and explain the evidence gap briefly.

Extract:
- 5 to 8 key strengths
- 5 to 8 key challenges
- Core indicators: HDI value, HDI rank, life expectancy, expected years of schooling, mean years of schooling, GNI per capita, population
- Any demographic or time-based quantities that can be plotted
- Short evidence snippets for important claims

Return JSON only matching this schema:

```json
{
  "country": "North Macedonia",
  "model_name": "...",
  "key_strengths": [{"item": "...", "evidence": "..."}],
  "key_challenges": [{"item": "...", "evidence": "..."}],
  "indicators": {
    "hdi_value": null,
    "hdi_rank": null,
    "life_expectancy_years": null,
    "expected_years_schooling": null,
    "mean_years_schooling": null,
    "gni_per_capita": null,
    "population": null
  },
  "time_series": [
    {"name": "...", "year": 2004, "value": 0.0, "unit": "...", "source_phrase": "..."}
  ],
  "notes": "..."
}
```

Source text:
{source_text}

