
from datetime import date, datetime, time, timedelta, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.elexon import fetch_actuals, fetch_forecasts
from app.analysis import analyse_wind_data

app = FastAPI(
    title="Wind Procurement Intelligence API",
    description="UK wind generation forecast analysis",
    version="1.0.0",
)

# Local React development server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Wind Procurement Intelligence API",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/analysis")
def get_analysis(
    decision_date: date = Query(
        ...,
        description="Decision date in January 2026, YYYY-MM-DD",
    ),
    cutoff_time: time = Query(
        default=time(10, 0),
        description="Assumed UK decision cutoff in UTC, HH:MM",
    ),
):
    """
    Analyse the forecast available on a decision date
    for the following delivery day.

    The 10:00 UTC default is a pilot assumption, not a
    confirmed client trading rule.
    """

    if not (
        date(2026, 1, 1)
        <= decision_date
        <= date(2026, 1, 31)
    ):
        raise HTTPException(
            status_code=400,
            detail="decision_date must be in January 2026",
        )

    delivery_date = decision_date + timedelta(days=1)

    cutoff = datetime.combine(
        decision_date,
        cutoff_time,
        tzinfo=timezone.utc,
    )

    start = datetime.combine(
        delivery_date,
        time.min,
        tzinfo=timezone.utc,
    )
    end = start + timedelta(days=1)

    start_str = start.isoformat().replace("+00:00", "Z")
    end_str = end.isoformat().replace("+00:00", "Z")
    cutoff_str = cutoff.isoformat().replace("+00:00", "Z")

    try:
        actuals = fetch_actuals(start_str, end_str)

        forecasts = fetch_forecasts(
            start_str,
            end_str,
            cutoff_str,
        )

        # Keep delivery periods strictly within the delivery day.
        actuals = actuals[
            (actuals["startTime"] >= start)
            & (actuals["startTime"] < end)
        ]

        forecasts = forecasts[
            (forecasts["startTime"] >= start)
            & (forecasts["startTime"] < end)
        ]

        result = analyse_wind_data(
            actuals,
            forecasts,
            cutoff_str,
        )

        return {
            "decision_date": decision_date.isoformat(),
            "delivery_date": delivery_date.isoformat(),
            "cutoff_time_utc": cutoff_str,
            "units": "MW",
            "note": (
                "Forecast selection uses the configured cutoff. "
                "Confirm the actual market decision cutoff before "
                "using results for operational purchasing."
            ),
            **result,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to retrieve or analyse Elexon data: {exc}",
        ) from exc
