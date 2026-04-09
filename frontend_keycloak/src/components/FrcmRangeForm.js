import React, { useState } from "react";
import { useKeycloak } from "@react-keycloak/web";
import { apiFetch } from "../api/apiFetch";

function toIsoLocal(datetimeLocalValue) {
  // datetime-local gives "YYYY-MM-DDTHH:mm"
  // Convert to ISO string with seconds, in local time converted to UTC
  const d = new Date(datetimeLocalValue);
  return d.toISOString();
}

export default function FrcmRangeForm() {
  const { keycloak, initialized } = useKeycloak();
  const isAuthed = !!keycloak?.authenticated;
  const token = keycloak?.token || "";

  // Defaults similar to your backend examples
  const now = new Date();
  const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);

  const toDatetimeLocal = (d) => {
    // format to "YYYY-MM-DDTHH:mm"
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
      d.getHours()
    )}:${pad(d.getMinutes())}`;
  };

  const [lon, setLon] = useState(5.3327);
  const [lat, setLat] = useState(60.383);
  const [startLocal, setStartLocal] = useState(toDatetimeLocal(yesterday));
  const [endLocal, setEndLocal] = useState(toDatetimeLocal(now));

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (!initialized) return null;

  async function callRange() {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const start_time = toIsoLocal(startLocal);
      const end_time = toIsoLocal(endLocal);

      const qs = new URLSearchParams({
        lon: String(lon),
        lat: String(lat),
        start_time,
        end_time,
      }).toString();

      const data = await apiFetch(`/frcm/range?${qs}`, { token });
      setResult(data);
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginTop: 16 }}>
      <h3>FRCM range</h3>
      <p style={{ marginTop: 4, opacity: 0.8 }}>
        Calls <code>/frcm/range</code> with lon/lat + start/end time.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
          maxWidth: 700,
        }}
      >
        <label>
          Longitude
          <input
            type="number"
            step="0.0001"
            value={lon}
            onChange={(e) => setLon(e.target.value)}
            style={{ display: "block", width: "100%" }}
          />
        </label>

        <label>
          Latitude
          <input
            type="number"
            step="0.0001"
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            style={{ display: "block", width: "100%" }}
          />
        </label>

        <label>
          Start time
          <input
            type="datetime-local"
            value={startLocal}
            onChange={(e) => setStartLocal(e.target.value)}
            style={{ display: "block", width: "100%" }}
          />
        </label>

        <label>
          End time
          <input
            type="datetime-local"
            value={endLocal}
            onChange={(e) => setEndLocal(e.target.value)}
            style={{ display: "block", width: "100%" }}
          />
        </label>
      </div>

      <div style={{ marginTop: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button disabled={!isAuthed || loading} onClick={callRange}>
          {loading ? "Calling..." : "GET /frcm/range"}
        </button>

        <button
          onClick={() => {
            setError(null);
            setResult(null);
          }}
        >
          Clear
        </button>
      </div>

      {!isAuthed && (
        <p style={{ color: "crimson", marginTop: 10 }}>
          You must be logged in (and have the <code>default-roles-frcm-realm</code> role)
          to call this endpoint.
        </p>
      )}

      {error && <pre style={{ color: "crimson", marginTop: 10 }}>{error}</pre>}
      {result && <pre style={{ marginTop: 10 }}>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}