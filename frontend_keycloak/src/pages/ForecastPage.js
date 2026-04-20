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

async function getCoordinatesFromPlace(placeName) {
  const trimmedPlace = placeName.trim();

  if (!trimmedPlace) {
    throw new Error("Please enter a location");
  }

  const url = `https://ws.geonorge.no/stedsnavn/v1/navn?sok=${encodeURIComponent(
    trimmedPlace
  )}&fuzzy=false`;

  const res = await fetch(url);

  if (!res.ok) {
    throw new Error("Could not fetch coordinates from Geonorge");
  }

  const data = await res.json();
  console.log("Geonorge response:", data);

  if (!data.navn || data.navn.length === 0) {
    throw new Error("No location found for that place name");
  }

  // Velg helst By, deretter Tettsted, deretter Kommune, ellers første treff
  const preferredTypes = ["By", "Tettsted", "Kommune"];

  const bestMatch =
    data.navn.find((item) => preferredTypes.includes(item.navneobjekttype)) ||
    data.navn[0];

  const lat = bestMatch?.representasjonspunkt?.nord;
  const lon = bestMatch?.representasjonspunkt?.øst;

  if (lat == null || lon == null) {
    throw new Error("Could not extract latitude/longitude from Geonorge response");
  }

  return {
    lat,
    lon,
    locationName: bestMatch.skrivemåte || trimmedPlace,
    objectType: bestMatch.navneobjekttype || "Unknown",
    rawMatch: bestMatch,
  };
}

export default function ForecastPage() {
  const { keycloak, initialized } = useKeycloak();

  const now = useMemo(() => new Date(), []);
  const yesterday = useMemo(
    () => new Date(now.getTime() - 24 * 60 * 60 * 1000),
    [now]
  );

  const [location, setLocation] = useState("Bergen");
  const [resolvedCoords, setResolvedCoords] = useState(null);

  const [startLocal, setStartLocal] = useState(toDatetimeLocal(yesterday));
  const [endLocal, setEndLocal] = useState(toDatetimeLocal(now));

  const [results, setResults] = useState([]);
  const [rawResponse, setRawResponse] = useState(null);

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
    setResolvedCoords(null);
    setRawResponse(null);
    setLoading(true);

    try {
      const coords = await getCoordinatesFromPlace(location);
      setResolvedCoords(coords);

      const requestParams = {
        lon: String(coords.lon),
        lat: String(coords.lat),
        start_time: toIsoLocal(startLocal),
        end_time: toIsoLocal(endLocal),
      };

      console.log("Resolved coords:", coords);
      console.log("Backend request params:", requestParams);

      const qs = new URLSearchParams(requestParams).toString();

      const data = await apiFetch(`/frcm/range?${qs}`, {
        token: keycloak.token,
      });

      console.log("Backend response:", data);

      setRawResponse(data);
      setResults(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Search error:", err);
      setError(err.message || "Could not fetch fire risk forecast");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container">
      <h1>Fire Risk Forecast</h1>
      <p>
        Enter a place name and a time range to compute fire risk forecasts.
      </p>

      <form className="forecast-form" onSubmit={handleSearch}>
        <div className="form-grid">
          <label>
            Location
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="For example Bergen, Oslo, Trondheim"
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
          <button type="submit" disabled={loading || !location.trim()}>
            {loading ? "Searching..." : "Get Forecast"}
          </button>
        </div>
      </form>

      {resolvedCoords && (
        <div style={{ marginTop: 12, padding: 12, background: "#fff", borderRadius: 8 }}>
          <p style={{ margin: 0 }}>
            Using coordinates for <b>{resolvedCoords.locationName}</b>
          </p>
          <p style={{ margin: "8px 0 0 0" }}>
            Type: <b>{resolvedCoords.objectType}</b>
          </p>
          <p style={{ margin: "8px 0 0 0" }}>
            Latitude: <b>{resolvedCoords.lat}</b>
          </p>
          <p style={{ margin: "8px 0 0 0" }}>
            Longitude: <b>{resolvedCoords.lon}</b>
          </p>
        </div>
      )}

      {error && <p className="error-text">{error}</p>}

      {!loading && rawResponse && Array.isArray(rawResponse) && rawResponse.length === 0 && (
        <div
          style={{
            marginTop: 16,
            padding: 12,
            background: "#fff4e5",
            border: "1px solid #facc15",
            borderRadius: 8,
          }}
        >
          <p style={{ margin: 0 }}>
            Backend returned an empty array for this location and time range.
          </p>
          <p style={{ margin: "8px 0 0 0" }}>
            This usually means the backend has no data for these coordinates.
          </p>
        </div>
      )}

      {rawResponse && (
        <div style={{ marginTop: 20 }}>
          <h3>Debug: Raw backend response</h3>
          <pre
            style={{
              background: "#fff",
              padding: 12,
              borderRadius: 8,
              overflowX: "auto",
            }}
          >
            {JSON.stringify(rawResponse, null, 2)}
          </pre>
        </div>
      )}

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