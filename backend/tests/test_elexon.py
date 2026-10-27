
import pandas as pd
from app.elexon import fetch_actuals, fetch_forecasts


def test_actuals_return_hourly_wind_values():
    actuals = fetch_actuals(
        "2026-01-15T00:00:00Z",
        "2026-01-16T00:00:00Z",
    )

    assert not actuals.empty
    assert list(actuals.columns) == ["startTime", "actual_mw"]
    assert len(actuals) == 24
    assert actuals["startTime"].is_monotonic_increasing
    assert actuals["actual_mw"].notna().all()


def test_forecasts_respect_delivery_window_and_cutoff():
    forecasts = fetch_forecasts(
        "2026-01-15T00:00:00Z",
        "2026-01-16T00:00:00Z",
        "2026-01-14T10:00:00Z",
    )

    assert not forecasts.empty
    assert list(forecasts.columns) == [
        "startTime",
        "publishTime",
        "forecast_mw",
    ]

    start = pd.Timestamp("2026-01-15T00:00:00Z")
    end = pd.Timestamp("2026-01-16T00:00:00Z")
    cutoff = pd.Timestamp("2026-01-14T10:00:00Z")

    assert (forecasts["startTime"] >= start).all()
    assert (forecasts["startTime"] < end).all()
    assert (forecasts["publishTime"] <= cutoff).all()
    assert forecasts["forecast_mw"].notna().all()
