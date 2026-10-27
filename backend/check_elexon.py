
from app.elexon import fetch_actuals, fetch_forecasts

start = "2026-01-15T00:00:00Z"
end = "2026-01-16T00:00:00Z"

try:
    actuals = fetch_actuals(start, end)
    forecasts = fetch_forecasts(start, end)

    print("\n--- ACTUALS ---")
    print("Rows:", len(actuals))
    print(actuals.head())
    print("Columns:", actuals.columns.tolist())

    print("\n--- FORECASTS ---")
    print("Rows:", len(forecasts))
    print(forecasts.head())
    print("Columns:", forecasts.columns.tolist())

    if not forecasts.empty:
        print("\nForecast publication times:")
        print(forecasts["publishTime"].min())
        print(forecasts["publishTime"].max())

except Exception as error:
    print(type(error).__name__, error)
