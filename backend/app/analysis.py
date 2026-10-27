
import numpy as np
import pandas as pd


def analyse_wind_data(
    actuals: pd.DataFrame,
    forecasts: pd.DataFrame,
    decision_cutoff: str,
) -> dict:
    """
    Compare actual wind generation with the latest forecast
    published on or before a specified decision cutoff.

    decision_cutoff must be an ISO-8601 timestamp.
    """

    cutoff = pd.Timestamp(decision_cutoff)

    if cutoff.tzinfo is None:
        cutoff = cutoff.tz_localize("UTC")
    else:
        cutoff = cutoff.tz_convert("UTC")

    actuals = actuals.copy()
    forecasts = forecasts.copy()

    if not actuals.empty:
        actuals["startTime"] = pd.to_datetime(
            actuals["startTime"], utc=True
        )

    if not forecasts.empty:
        forecasts["startTime"] = pd.to_datetime(
            forecasts["startTime"], utc=True
        )
        forecasts["publishTime"] = pd.to_datetime(
            forecasts["publishTime"], utc=True
        )

        # Exclude forecasts that were not yet published at decision time.
        forecasts = forecasts[
            forecasts["publishTime"] <= cutoff
        ]

        # One eligible forecast per delivery period.
        forecasts = (
            forecasts.sort_values(
                ["startTime", "publishTime"]
            )
            .drop_duplicates(
                subset=["startTime"], keep="last"
            )
        )

    if actuals.empty or forecasts.empty:
        return {
            "decision_cutoff": cutoff.isoformat(),
            "matched_periods": 0,
            "metrics": {
                "mae_mw": None,
                "rmse_mw": None,
                "bias_mw": None,
                "wape_percent": None,
            },
            "rows": [],
        }

    merged = pd.merge(
        forecasts[["startTime", "publishTime", "forecast_mw"]],
        actuals[["startTime", "actual_mw"]],
        on="startTime",
        how="inner",
        validate="one_to_one",
    )

    merged["error_mw"] = (
        merged["forecast_mw"] - merged["actual_mw"]
    )
    merged["absolute_error_mw"] = merged["error_mw"].abs()

    if merged.empty:
        metrics = {
            "mae_mw": None,
            "rmse_mw": None,
            "bias_mw": None,
            "wape_percent": None,
        }
    else:
        errors = merged["error_mw"].to_numpy(dtype=float)
        actual_values = merged["actual_mw"].to_numpy(dtype=float)

        total_actual = float(np.abs(actual_values).sum())

        metrics = {
            "mae_mw": float(np.mean(np.abs(errors))),
            "rmse_mw": float(np.sqrt(np.mean(errors ** 2))),
            "bias_mw": float(np.mean(errors)),
            "wape_percent": (
                float(np.abs(errors).sum() / total_actual * 100)
                if total_actual > 0
                else None
            ),
        }

    # Make the response safe for JSON serialization.
    rows = merged.sort_values("startTime").copy()
    rows["startTime"] = rows["startTime"].map(
        lambda x: x.isoformat()
    )
    rows["publishTime"] = rows["publishTime"].map(
        lambda x: x.isoformat()
    )

    return {
        "decision_cutoff": cutoff.isoformat(),
        "matched_periods": len(rows),
        "metrics": metrics,
        "rows": rows.to_dict(orient="records"),
    }
