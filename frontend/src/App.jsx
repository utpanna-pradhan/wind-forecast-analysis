
import { useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  ArrowDownRight,
  ArrowUpRight,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Download,
  RefreshCw,
  Wind,
  Zap,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function formatNumber(value, digits = 0) {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "N/A";
  }

  return new Intl.NumberFormat("en-GB", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(value);
}

function MetricCard({ title, value, unit, description, icon: Icon, trend }) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span className="metric-title">{title}</span>
        <span className="metric-icon">
          <Icon size={19} />
        </span>
      </div>

      <div className="metric-value">
        {value}
        <span className="metric-unit">{unit}</span>
      </div>

      <div className="metric-bottom">
        <span className={`metric-trend ${trend === "positive" ? "positive" : ""}`}>
          {trend === "positive" ? (
            <ArrowDownRight size={15} />
          ) : (
            <ArrowUpRight size={15} />
          )}
          {description}
        </span>
      </div>
    </article>
  );
}

function App() {
  const [decisionDate, setDecisionDate] = useState("2026-01-14");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadAnalysis(date = decisionDate) {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/analysis?decision_date=${date}&cutoff_time=10:00:00`
      );

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(
          body.detail || `Request failed with status ${response.status}`
        );
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(
        `${err.message}. Check that your FastAPI backend is running on port 8000.`
      );
      setData(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAnalysis(decisionDate);
    // Load the initial date when the component mounts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const chartData = (data?.rows ?? []).map((row) => ({
    time: new Date(row.startTime).toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "UTC",
    }),
    forecast: Number(row.forecast_mw),
    actual: Number(row.actual_mw),
    error: Number(row.error_mw),
  }));

  function handleDateChange(event) {
    const nextDate = event.target.value;
    setDecisionDate(nextDate);

    if (nextDate) {
      loadAnalysis(nextDate);
    }
  }

  function downloadCSV() {
    if (!data?.rows?.length) return;

    const headers = [
      "Delivery time (UTC)",
      "Forecast (MW)",
      "Actual (MW)",
      "Error (MW)",
      "Absolute error (MW)",
    ];

    const rows = data.rows.map((row) => [
      row.startTime,
      row.forecast_mw,
      row.actual_mw,
      row.error_mw,
      row.absolute_error_mw,
    ]);

    const csv = [headers, ...rows]
      .map((row) =>
        row.map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(",")
      )
      .join("\n");

    const url = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8;" })
    );

    const link = document.createElement("a");
    link.href = url;
    link.download = `wind-analysis-${data.delivery_date}.csv`;
    link.click();

    URL.revokeObjectURL(url);
  }

  const metrics = data?.metrics;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview">
          <span className="brand-mark">
            <Wind size={24} />
          </span>
          <span>
            <strong>Windwise</strong>
            <small>PROCUREMENT INTELLIGENCE</small>
          </span>
        </a>

        <div className="sidebar-label">WORKSPACE</div>

        <a className="nav-item active" href="#overview">
          <Activity size={18} />
          Overview
        </a>

        <a className="nav-item" href="#performance">
          <Zap size={18} />
          Forecast performance
        </a>

        <a className="nav-item" href="#hourly-data">
          <Clock3 size={18} />
          Hourly breakdown
        </a>

        <div className="sidebar-bottom">
          <div className="status-indicator">
            <span className="status-dot" />
            <span>
              <strong>API connection</strong>
              <small>{error ? "Connection issue" : "Check via dashboard"}</small>
            </span>
          </div>
          <p>UK WIND GENERATION DATA</p>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div className="breadcrumb">Workspace / <strong>Overview</strong></div>
          <div className="topbar-right">
            <span className="live-label">
              <span className="status-dot" />
              Historical analysis
            </span>
            <span className="avatar">WI</span>
          </div>
        </header>

        <section className="page-heading">
          <div>
            <p className="eyebrow">ENERGY ANALYTICS / DAY-AHEAD</p>
            <h1>Wind forecast overview</h1>
            <p className="page-description">
              Evaluate forecast accuracy against actual UK wind generation.
            </p>
          </div>

          <button
            className="button button-secondary"
            onClick={downloadCSV}
            disabled={!data?.rows?.length}
          >
            <Download size={16} />
            Export CSV
          </button>
        </section>

        <section className="filter-panel">
          <div className="filter-info">
            <span className="filter-icon"><CalendarDays size={19} /></span>
            <div>
              <strong>Decision date</strong>
              <small>Choose a date in January 2026</small>
            </div>
          </div>

          <input
            className="date-input"
            type="date"
            min="2026-01-01"
            max="2026-01-31"
            value={decisionDate}
            onChange={handleDateChange}
          />

          <div className="cutoff-badge">
            <Clock3 size={15} />
            Cutoff: 10:00 UTC
          </div>

          <button
            className="button button-primary"
            onClick={() => loadAnalysis()}
            disabled={loading}
          >
            <RefreshCw size={16} className={loading ? "spin" : ""} />
            {loading ? "Loading..." : "Refresh"}
          </button>
        </section>

        {error && (
          <div className="error-banner">
            <AlertCircle size={20} />
            <div>
              <strong>Unable to load analysis</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {loading && !data ? (
          <div className="loading-panel">
            <span className="loader" />
            <strong>Loading wind generation data...</strong>
            <p>Fetching historical forecasts and actual generation.</p>
          </div>
        ) : (
          <>
            <section className="metrics-grid">
              <MetricCard
                title="Mean absolute error"
                value={formatNumber(metrics?.mae_mw, 1)}
                unit="MW"
                description="Average absolute difference"
                icon={Activity}
              />

              <MetricCard
                title="RMSE"
                value={formatNumber(metrics?.rmse_mw, 1)}
                unit="MW"
                description="Penalises larger errors"
                icon={Zap}
              />

              <MetricCard
                title="WAPE"
                value={formatNumber(metrics?.wape_percent, 2)}
                unit="%"
                description="Error relative to actual output"
                icon={CheckCircle2}
                trend="positive"
              />

              <MetricCard
                title="Forecast bias"
                value={formatNumber(metrics?.bias_mw, 1)}
                unit="MW"
                description={
                  metrics?.bias_mw == null
                    ? "No matched data"
                    : metrics.bias_mw < 0
                      ? "Underforecast on average"
                      : metrics.bias_mw > 0
                        ? "Overforecast on average"
                        : "No average bias"
                }
                icon={Wind}
              />
            </section>

            <section className="insight-strip">
              <div className="insight-icon"><Wind size={20} /></div>
              <div>
                <strong>
                  Delivery day: {data?.delivery_date ?? "Waiting for data"}
                </strong>
                <p>
                  {data?.matched_periods ?? 0} matched hourly periods.
                  {" "}Forecast bias is forecast minus actual generation.
                </p>
              </div>
              <span className="insight-tag">
                {data?.matched_periods === 24 ? "FULL DAY" : "PARTIAL DATA"}
              </span>
            </section>

            <section className="charts-grid" id="performance">
              <article className="panel forecast-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Forecast vs actual</h2>
                    <p>Hourly wind generation · MW</p>
                  </div>
                  <span className="chart-legend-label">
                    <span className="legend-dot forecast-dot" /> Forecast
                    <span className="legend-dot actual-dot" /> Actual
                  </span>
                </div>

                <div className="chart-container">
                  {chartData.length ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartData} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
                        <defs>
                          <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#14b8a6" stopOpacity={0.22} />
                            <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.01} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e8edf2" />
                        <XAxis dataKey="time" tickLine={false} axisLine={false} tick={{ fill: "#7b8794", fontSize: 11 }} interval={3} />
                        <YAxis tickLine={false} axisLine={false} tick={{ fill: "#7b8794", fontSize: 11 }} width={55} tickFormatter={(value) => `${Math.round(value / 1000)}k`} />
                        <Tooltip formatter={(value) => [`${formatNumber(value, 1)} MW`]} />
                        <Area type="monotone" dataKey="actual" name="Actual" stroke="#14b8a6" strokeWidth={2.5} fill="url(#actualGradient)" />
                        <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#6478e8" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
                        <Legend />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="empty-state">No matching hourly data available.</div>
                  )}
                </div>
              </article>

              <article className="panel error-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Forecast error</h2>
                    <p>Forecast minus actual · MW</p>
                  </div>
                </div>

                <div className="chart-container">
                  {chartData.length ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e8edf2" />
                        <XAxis dataKey="time" tickLine={false} axisLine={false} tick={{ fill: "#7b8794", fontSize: 11 }} interval={5} />
                        <YAxis tickLine={false} axisLine={false} tick={{ fill: "#7b8794", fontSize: 11 }} width={55} />
                        <Tooltip formatter={(value) => [`${formatNumber(value, 1)} MW`]} />
                        <Line type="monotone" dataKey="error" name="Forecast error" stroke="#e5a04b" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="empty-state">No error data available.</div>
                  )}
                </div>
              </article>
            </section>

            <section className="panel table-panel" id="hourly-data">
              <div className="panel-heading table-heading">
                <div>
                  <h2>Hourly generation breakdown</h2>
                  <p>Actual output compared with the selected day-ahead forecast</p>
                </div>
                <span className="row-count">{data?.rows?.length ?? 0} periods</span>
              </div>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Delivery time (UTC)</th>
                      <th>Forecast (MW)</th>
                      <th>Actual (MW)</th>
                      <th>Error (MW)</th>
                      <th>Absolute error (MW)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(data?.rows ?? []).map((row) => (
                      <tr key={row.startTime}>
                        <td className="time-cell">
                          {new Date(row.startTime).toLocaleString("en-GB", {
                            day: "2-digit",
                            month: "short",
                            hour: "2-digit",
                            minute: "2-digit",
                            timeZone: "UTC",
                          })}
                        </td>
                        <td>{formatNumber(row.forecast_mw)}</td>
                        <td>{formatNumber(row.actual_mw, 1)}</td>
                        <td className={row.error_mw < 0 ? "negative" : "positive-number"}>
                          {row.error_mw > 0 ? "+" : ""}
                          {formatNumber(row.error_mw, 1)}
                        </td>
                        <td>{formatNumber(row.absolute_error_mw, 1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {!data?.rows?.length && (
                  <div className="empty-state">No data found for this decision date.</div>
                )}
              </div>
            </section>

            <footer className="page-footer">
              <span>Data source: Elexon BMRS API</span>
              <span>Decision cutoff: {data?.cutoff_time_utc ?? "10:00 UTC"}</span>
              <span>Prototype for analytical evaluation, not live trading advice.</span>
            </footer>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
