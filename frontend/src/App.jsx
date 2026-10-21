
import { useCallback, useEffect, useState } from "react";
import StatusTable from "./components/StatusTable";
import HistoryChart from "./components/HistoryChart";
import IncidentLog from "./components/IncidentLog";
import AddTargetForm from "./components/AddTargetForm";
import {
  USE_MOCK,
  getStatus,
  getHistory,
  getIncidents,
  addTarget,
} from "./api";
import "./App.css";

function App() {
  const [targets, setTargets] = useState([]);
  const [history, setHistory] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [range, setRange] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refreshData = useCallback(async () => {
    try {
      setError("");

      const [statusData, historyData, incidentData] = await Promise.all([
        getStatus(),
        getHistory(),
        getIncidents(),
      ]);

      setTargets(Array.isArray(statusData) ? statusData : statusData.targets ?? []);
      setHistory(Array.isArray(historyData) ? historyData : historyData.history ?? []);
      setIncidents(
        Array.isArray(incidentData)
          ? incidentData
          : incidentData.incidents ?? []
      );
    } catch (err) {
      setError(err.message || "Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshData();

    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, [refreshData]);

  async function handleAddTarget(target) {
    try {
      const addedTarget = await addTarget(target);
      setTargets((current) => [addedTarget, ...current]);
    } catch (err) {
      setError(err.message || "Unable to add website.");
    }
  }

  const upCount = targets.filter((target) => target.ok === true).length;
  const downCount = targets.filter((target) => target.ok === false).length;
  const uptime =
    targets.length > 0
      ? (
          targets.reduce(
            (sum, target) => sum + Number(target.uptime_24h ?? 0),
            0
          ) / targets.length
        ).toFixed(2)
      : "—";

  const cutoff = Date.now() - range * 60 * 60 * 1000;
  const filteredHistory = history.filter(
    (item) => new Date(item.timestamp).getTime() >= cutoff
  );

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">MONITORING OVERVIEW</p>
          <h1>Uptime Monitor</h1>
          <p className="subtitle">
            Keep an eye on your websites, all in one place.
          </p>
        </div>

        <div className="header-right">
          <span className={`mode-badge ${USE_MOCK ? "mock" : "live"}`}>
            {USE_MOCK ? "Demo mode" : "Live mode"}
          </span>
          <button className="refresh-button" onClick={refreshData}>
            ↻ Refresh
          </button>
        </div>
      </header>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <section className="summary-grid">
        <article className="summary-card">
          <p>Total websites</p>
          <strong>{targets.length}</strong>
          <span>Monitored targets</span>
        </article>

        <article className="summary-card">
          <p>Websites up</p>
          <strong className="text-up">{upCount}</strong>
          <span>Responding normally</span>
        </article>

        <article className="summary-card">
          <p>Websites down</p>
          <strong className="text-down">{downCount}</strong>
          <span>Need attention</span>
        </article>

        <article className="summary-card">
          <p>Average uptime</p>
          <strong>{uptime}{uptime !== "—" ? "%" : ""}</strong>
          <span>Across displayed targets</span>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Website status</h2>
            <p>Current health and response details</p>
          </div>
          <span className="small-count">{targets.length} websites</span>
        </div>

        {loading ? (
          <div className="empty-state">Loading dashboard…</div>
        ) : (
          <StatusTable targets={targets} />
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Performance history</h2>
            <p>Response time over time</p>
          </div>

          <div className="range-controls" aria-label="Chart time range">
            {[1, 6, 24].map((hours) => (
              <button
                key={hours}
                className={range === hours ? "range-active" : ""}
                onClick={() => setRange(hours)}
              >
                {hours}h
              </button>
            ))}
          </div>
        </div>

        <HistoryChart history={filteredHistory} range={range} />
      </section>

      <section className="lower-grid">
        <div className="panel">
          <IncidentLog incidents={incidents} />
        </div>

        <div className="panel">
          <AddTargetForm onAdd={handleAddTarget} mockMode={USE_MOCK} />
        </div>
      </section>

      <footer className="dashboard-footer">
        Uptime Monitor · Dashboard refreshes every 30 seconds
      </footer>
    </main>
  );
}

export default App;
