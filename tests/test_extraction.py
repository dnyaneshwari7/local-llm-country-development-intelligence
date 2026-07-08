from country_dev_intel.extraction import extract_indicator_candidates, extract_time_series_candidates


def test_extract_indicator_candidates() -> None:
    text = "The HDI was 0.793. The population was 2.1 million. Life expectancy reached 74.2 years."
    indicators = extract_indicator_candidates(text)
    assert indicators["hdi_value"] == 0.793
    assert indicators["population"] == "2.1 million"
    assert indicators["life_expectancy_years"] == 74.2


def test_extract_time_series_candidates() -> None:
    rows = extract_time_series_candidates("In 2004 unemployment was 37 percent. In 1998 it was 31 percent.")
    assert rows[0]["year"] == 2004
    assert rows[0]["value"] == 37

