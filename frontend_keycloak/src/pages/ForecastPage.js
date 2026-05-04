import React, { useEffect, useMemo, useState } from "react";
import { useKeycloak } from "@react-keycloak/web";
import { apiFetch } from "../api/apiFetch";

function toDatetimeLocal(date) {
  const pad = (n) => String(n).padStart(2, "0");

  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
    date.getDate()
  )}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toIsoLocal(datetimeLocalValue) {
  const d = new Date(datetimeLocalValue);
  return d.toISOString();
}

export default function ForecastPage() {
  const { keycloak, initialized } = useKeycloak();

  const now = useMemo(() => new Date(), []);
  const yesterday = useMemo(
    () => new Date(now.getTime() - 24 * 60 * 60 * 1000),
    [now]
  );

  const [lon, setLon] = useState("5.3327");
  const [lat, setLat] = useState("60.3830");
  const [startLocal, setStartLocal] = useState(toDatetimeLocal(yesterday));
  const [endLocal, setEndLocal] = useState(toDatetimeLocal(now));

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!initialized) return;

    if (!keycloak.authenticated) {
      keycloak.login({
        redirectUri: `${window.location.origin}/forecast`,
      });
    }
  }, [initialized, keycloak]);

  if (!initialized) {
    return <p className="page-container">Loading...</p>;
  }

  if (!keycloak.authenticated) {
    return <p className="page-container">Redirecting to login...</p>;
  }

  async function handleSearch(e) {
    e.preventDefault();
    setError("");
    setResults([]);

    setLoading(true);

    try {
      const qs = new URLSearchParams({
        lon: String(lon),
        lat: String(lat),
        start_time: toIsoLocal(startLocal),
        end_time: toIsoLocal(endLocal),
      }).toString();

      const data = await apiFetch(`/frcm/range?${qs}`, {
        token: keycloak.token,
      });

      setResults(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Could not fetch fire risk forecast");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <h1>Fire Risk Forecast</h1>
      <p>
        Enter longitude, latitude, and a time range to compute fire risk
        forecasts.
      </p>

      <form className="forecast-form" onSubmit={handleSearch}>
        <div className="form-grid">
          <label>
            Longitude
            <input
              type="number"
              step="0.0001"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
            />
          </label>

          <label>
            Latitude
            <input
              type="number"
              step="0.0001"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
            />
          </label>

          <label>
            Start time
            <input
              type="datetime-local"
              value={startLocal}
              onChange={(e) => setStartLocal(e.target.value)}
            />
          </label>

          <label>
            End time
            <input
              type="datetime-local"
              value={endLocal}
              onChange={(e) => setEndLocal(e.target.value)}
            />
          </label>
        </div>

        <div className="forecast-actions">
          <button type="submit" disabled={loading}>
            {loading ? "Searching..." : "Get Forecast"}
          </button>
        </div>
      </form>

      {error && <p className="error-text">{error}</p>}

      <div className="results-wrapper">
        {results.length === 0 ? (
          !loading && <p>No results yet.</p>
        ) : (
          <table className="forecast-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Location</th>
                <th>Lat</th>
                <th>Lon</th>
                <th>Temperature</th>
                <th>Humidity</th>
                <th>Wind Speed</th>
                <th>Risk Score</th>
                <th>Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {results.map((row, idx) => (
                <tr key={`${row.location}-${row.time}-${idx}`}>
                  <td>{new Date(row.time).toLocaleString()}</td>
                  <td>{row.location}</td>
                  <td>{row.lat}</td>
                  <td>{row.lon}</td>
                  <td>{row.temperature}</td>
                  <td>{row.humidity}</td>
                  <td>{row.wind_speed}</td>
                  <td>{row.risk_score}</td>
                  <td>{row.risk_level}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}