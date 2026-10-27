
import requests

BASE = "https://data.elexon.co.uk/bmrs/api/v1"

tests = [
    (
        "Historical wind and solar actuals",
        f"{BASE}/generation/actual/per-type/wind-and-solar",
        {
            "from": "2026-01-15T00:00:00Z",
            "to": "2026-01-16T00:00:00Z",
        },
    ),
    (
        "Wind forecast history",
        f"{BASE}/forecast/generation/wind/history",
        {
            "publishTime": "2026-01-14T10:00:00Z",
        },
    ),
]

for name, url, params in tests:
    print(f"\n--- {name} ---")
    try:
        response = requests.get(url, params=params, timeout=30)
        print("URL:", response.url)
        print("HTTP:", response.status_code)
        response.raise_for_status()

        payload = response.json()
        if isinstance(payload, dict):
            records = payload.get("data", [])
        else:
            records = payload

        print("Records:", len(records) if isinstance(records, list) else "Unexpected format")

        if isinstance(records, list) and records:
            print("First record:", records[0])
            print("Last record:", records[-1])
        else:
            print("Response:", str(payload)[:1000])

    except Exception as exc:
        print("ERROR:", repr(exc))
