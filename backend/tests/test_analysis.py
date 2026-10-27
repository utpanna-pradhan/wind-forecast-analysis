
import pandas as pd

from app.analysis import analyse_wind_data


def test_accuracy_metrics():
    actuals = pd.DataFrame({
        "startTime": [
            "2026-01-15T00:00:00Z",
            "2026-01-15T00:30:00Z",
        ],
        "actual_mw": [9000.0, 10000.0],
    })

    forecasts = pd.DataFrame({
        "startTime": [
            "2026-01-15T00:00:00Z",
            "2026-01-15T00:30:00Z",
        ],
        "publishTime": [
            "2026-01-14T09:00:00Z",
            "2026-01-14T09:00:00Z",
        ],
        "forecast_mw": [10000.0, 9000.0],
    })

    result = analyse_wind_data(
        actuals,
        forecasts,
        "2026-01-14T10:00:00Z",
    )

    assert result["matched_periods"] == 2
    assert result["metrics"]["mae_mw"] == 1000.0
    assert result["metrics"]["rmse_mw"] == 1000.0
    assert result["metrics"]["bias_mw"] == 0.0
    assert result["metrics"]["wape_percent"] == (
        2000 / 19000 * 100
    )


def test_forecast_after_cutoff_is_excluded():
    actuals = pd.DataFrame({
        "startTime": ["2026-01-15T00:00:00Z"],
        "actual_mw": [9000.0],
    })

    forecasts = pd.DataFrame({
        "startTime": [
            "2026-01-15T00:00:00Z",
            "2026-01-15T00:00:00Z",
        ],
        "publishTime": [
            "2026-01-14T09:00:00Z",
            "2026-01-14T11:00:00Z",
        ],
        "forecast_mw": [10000.0, 8000.0],
    })

    result = analyse_wind_data(
        actuals,
        forecasts,
        "2026-01-14T10:00:00Z",
    )

    assert result["matched_periods"] == 1
    assert result["rows"][0]["forecast_mw"] == 10000.0
