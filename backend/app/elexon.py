
import requests
import pandas as pd

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"
TIMEOUT = 30


def fetch_actuals(start: str, end: str) -> pd.DataFrame:
    """Fetch actual wind generation and aggregate it to hourly MW."""

    url = f"{BASE_URL}/generation/actual/per-type/wind-and-solar"
    response = requests.get(
        url,
        params={"from": start, "to": end},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    records = response.json()

    if isinstance(records, dict):
        records = records.get("data", [])

    columns = ["startTime", "actual_mw"]
    if not records:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(records)

    required = {"startTime", "publishTime", "businessType", "psrType", "quantity"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Actuals response missing fields: {sorted(missing)}")

    # Keep wind records only. Exclude solar.
    df = df[
        df["businessType"].astype(str).str.contains(
            "wind generation", case=False, na=False
        )
        & df["psrType"].astype(str).str.contains(
            "wind", case=False, na=False
        )
    ].copy()

    df["startTime"] = pd.to_datetime(df["startTime"], utc=True, errors="coerce")
    df["publishTime"] = pd.to_datetime(
        df["publishTime"], utc=True, errors="coerce"
    )
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df = df.dropna(subset=["startTime", "publishTime", "quantity"])

    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    df = df[
        (df["startTime"] >= start_ts)
        & (df["startTime"] < end_ts)
    ]

    # If a wind type/period has multiple publications, keep its latest value.
    df = df.sort_values("publishTime")
    df = df.drop_duplicates(
        subset=["startTime", "psrType"],
        keep="last",
    )

    # Sum onshore + offshore wind for each half-hour.
    half_hourly = (
        df.groupby("startTime", as_index=False)["quantity"]
        .sum()
        .rename(columns={"quantity": "actual_mw"})
    )

    # WINDFOR is hourly. Average the two half-hourly MW values
    # to align actuals with the forecast periods.
    half_hourly["hour"] = half_hourly["startTime"].dt.floor("h")

    hourly = (
        half_hourly.groupby("hour", as_index=False)["actual_mw"]
        .mean()
        .rename(columns={"hour": "startTime"})
    )

    return hourly[columns].sort_values("startTime").reset_index(drop=True)


def fetch_forecasts(
    start: str,
    end: str,
    decision_cutoff: str,
) -> pd.DataFrame:
    """Fetch the wind forecast snapshot available at the decision cutoff."""

    url = f"{BASE_URL}/forecast/generation/wind/history"

    response = requests.get(
        url,
        params={"publishTime": decision_cutoff},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    records = response.json()

    if isinstance(records, dict):
        records = records.get("data", [])

    columns = ["startTime", "publishTime", "forecast_mw"]
    if not records:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(records)

    required = {"startTime", "publishTime", "generation"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Forecast response missing fields: {sorted(missing)}")

    df["startTime"] = pd.to_datetime(df["startTime"], utc=True, errors="coerce")
    df["publishTime"] = pd.to_datetime(
        df["publishTime"], utc=True, errors="coerce"
    )
    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
    df = df.dropna(subset=["startTime", "publishTime", "generation"])

    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    cutoff_ts = pd.Timestamp(decision_cutoff)

    # Enforce both the delivery window and the decision-time cutoff.
    df = df[
        (df["startTime"] >= start_ts)
        & (df["startTime"] < end_ts)
        & (df["publishTime"] <= cutoff_ts)
    ].copy()

    df = df.sort_values(["startTime", "publishTime"])
    df = df.drop_duplicates(subset=["startTime"], keep="last")

    df = df.rename(columns={"generation": "forecast_mw"})
    return df[columns].sort_values("startTime").reset_index(drop=True)
