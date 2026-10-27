# Windwise | Wind Forecast Procurement Intelligence

A full-stack analytics dashboard for evaluating day-ahead UK wind generation forecasts against actual generation data. Built to help energy procurement teams understand forecast accuracy, quantify prediction errors, and investigate hourly differences between forecast and actual output.

## Live Demo

- **Frontend:** https://wind-forecast-analysis-wine.vercel.app/
- **Backend API:** https://wind-forecast-analysis-mcwx.onrender.com/
- **API Documentation:** https://wind-forecast-analysis-mcwx.onrender.com/docs
- **Health Check:** https://wind-forecast-analysis-mcwx.onrender.com/health
- **Source Code:** https://github.com/utpanna-pradhan/wind-forecast-analysis

> The application is an analytical prototype, not a live trading or procurement recommendation system.

## Features

- **Historical analysis:** Evaluate selected decision dates in January 2026.
- **Day-ahead forecast comparison:** Compare forecast wind generation with actual generation for the following delivery day.
- **Forecast performance metrics:** Calculate MAE, RMSE, WAPE, and forecast bias.
- **Hourly breakdown:** Inspect forecast, actual generation, signed error, and absolute error for each matched hour.
- **Interactive charts:** Visualize forecast versus actual generation and hourly forecast errors.
- **CSV export:** Export hourly analysis data for further investigation.
- **API integration:** Retrieve and analyse historical data from the Elexon BMRS API.
- **Responsive dashboard:** Access the analysis interface on desktop and smaller screens.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Charts | Recharts |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| Data processing | Pandas |
| Data source | Elexon BMRS API |
| Deployment | Vercel, Render |
| Containerization | Docker |

## Project Structure

```text
wind-forecast-analysis/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── elexon.py
│   │   └── analysis.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
├── Dockerfile
├── .gitignore
└── README.md
```

The frontend handles date selection, data presentation, charts, and CSV export. The FastAPI backend retrieves historical Elexon data, processes actual and forecast generation records, matches hourly periods, and calculates performance metrics.

## Data Source

The application uses the **Elexon Balancing Mechanism Reporting Service (BMRS)** API to retrieve historical UK wind generation forecasts and actual generation data.

- **Provider:** Elexon
- **API base URL:** https://data.elexon.co.uk/bmrs/api/v1/
- **Actual generation endpoint:** `/generation/actual/per-type/wind-and-solar`
- **Historical forecast endpoint:** `/forecast/generation/wind/history`

Only records relevant to wind generation are used in the analysis.

### Data Processing

1. Retrieve actual generation records for the delivery day.
2. Filter the actual generation records to wind-related categories.
3. Select the latest available publication for each relevant generation period and type.
4. Aggregate the half-hourly actual generation records into hourly MW values.
5. Retrieve historical wind forecast records published on or before the selected decision cutoff.
6. Select the latest eligible forecast for each delivery hour.
7. Match forecast and actual values by delivery timestamp.
8. Calculate forecast errors and aggregate performance metrics.

The analysis reports the number of matched hourly periods so users can see how many observations contribute to the results.

## Forecast Evaluation Methodology

For each matched delivery hour:

**Forecast error**

`Error = Forecast − Actual`

A negative error means the forecast underestimated actual generation. A positive error means it overestimated actual generation.

**Mean Absolute Error (MAE)**

`MAE = Mean(|Forecast − Actual|)`

Measures the average absolute forecast error in MW. Lower values indicate better accuracy.

**Root Mean Squared Error (RMSE)**

`RMSE = √Mean((Forecast − Actual)²)`

Penalizes larger forecast errors more heavily than MAE. Lower values indicate better accuracy.

**Weighted Absolute Percentage Error (WAPE)**

`WAPE = Sum(|Forecast − Actual|) / Sum(Actual) × 100`

Expresses total absolute error as a percentage of total actual generation. Lower values indicate better performance when total actual generation is positive.

**Forecast Bias**

`Bias = Mean(Forecast − Actual)`

A negative bias indicates systematic underforecasting, while a positive bias indicates systematic overforecasting. Values are reported in MW.

## Decision Date and Cutoff Assumptions

The selected decision date represents the date on which the forecast is evaluated as available to the decision-maker. The delivery date is the following calendar day.

- Supported decision dates: 1–31 January 2026.
- Default decision cutoff: 10:00 UTC.
- Delivery period: the following calendar day.
- Forecast selection: the latest eligible publication at or before the configured cutoff.
- Reported delivery timestamps and cutoff timestamps use UTC.

**Important:** The 10:00 UTC cutoff is a prototype assumption, not a verified procurement or trading deadline. It should be confirmed with the intended user before the results are used for operational decisions.

The actual generation aggregation and forecast publication-selection rules are implementation choices and should be validated against the relevant market reporting conventions before production use.

## Getting Started

### Prerequisites

Install the following:

- Python 3.10 or newer, compatible with the backend dependencies
- Node.js and npm
- Git

Docker is optional for local development.

### 1. Clone the repository

```bash
git clone https://github.com/utpanna-pradhan/wind-forecast-analysis.git
cd wind-forecast-analysis
```

### 2. Start the backend

Open a terminal in the repository root:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

**macOS/Linux:**

```bash
source .venv/bin/activate
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies and start FastAPI:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend should be available at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 3. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create a `.env.local` file inside `frontend/`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the Vite development server:

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

Keep both the backend and frontend running while using the local dashboard.

## Running Tests

From the repository root, activate the backend virtual environment and run:

```bash
cd backend
pytest
```

The tests cover the analysis logic and Elexon data handling. Run the tests before submitting changes to the project.

## Docker

A Dockerfile is included in the repository.

To build and run the container from the repository root, use:

```bash
docker build -t windwise-api -f Dockerfile .
docker run --rm -p 8000:8000 windwise-api
```

These commands assume the root-level Dockerfile is configured to build the backend from the repository root and start FastAPI on port 8000. The container build context and copy paths must match the actual Dockerfile.

For a production container, ensure the application binds to `0.0.0.0` and handles the hosting platform's configured port where required.

## Deployment

### Frontend: Vercel

The React application is deployed on Vercel.

Configure the following project settings:

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_URL`

Set `VITE_API_URL` to the public Render backend URL. This variable is intentionally public because it is used by browser-side code; it must not contain secrets.

### Backend: Render

The FastAPI backend is deployed on Render.

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

The backend CORS configuration must allow the deployed Vercel frontend origin.

The free Render instance may spin down during inactivity, so the first request after a period of inactivity can be slow.

## Limitations

- The analysis is restricted to January 2026 decision dates.
- The default decision cutoff is an assumption and has not been confirmed as an operational procurement deadline.
- Results depend on the availability, publication timing, and quality of the source data.
- Hourly aggregation can hide variations within half-hourly settlement periods.
- Missing or unmatched forecast and actual records can affect the number of evaluated periods.
- The prototype does not incorporate electricity prices, balancing costs, demand, storage constraints, or other factors required for a complete procurement decision.
- Historical forecast accuracy does not guarantee future forecast performance.
- The application is intended for analytical evaluation and demonstration, not live trading advice.

## AI Usage Disclosure

AI assistance was used during development to support implementation, debugging, code explanations, documentation, and deployment troubleshooting.

The developer reviewed and tested the application, including the forecast analysis workflow and the deployed interface. The project should be evaluated based on the submitted code, methodology, tests, and demonstrated behaviour.

## Author

**Utpanna Pradhan**

GitHub: https://github.com/utpanna-pradhan

---

Built as a prototype for evaluating day-ahead UK wind generation forecast accuracy using historical Elexon data.
