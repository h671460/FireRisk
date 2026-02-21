import React, { useState } from "react";
import { useKeycloak } from "@react-keycloak/web";
import { apiFetch } from "../api/apiFetch";

export default function ApiTester() {
  const { keycloak, initialized } = useKeycloak();

  const token = keycloak?.token || "";
  const isAuthed = !!keycloak?.authenticated; // ✅ no useMemo

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function run(fn) {
    setError(null);
    setResult(null);
    try {
      const data = await fn();
      setResult(data);
    } catch (e) {
      setError(e.message || String(e));
    }
  }

  if (!initialized) return null;

  return (
    <div style={{ marginTop: 16 }}>
      <h3>API tester</h3>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button onClick={() => run(() => apiFetch("/healthy"))}>GET /healthy</button>

        <button disabled={!isAuthed} onClick={() => run(() => apiFetch("/user/secure", { token }))}>
          GET /user/secure
        </button>

        <button disabled={!isAuthed} onClick={() => run(() => apiFetch("/user/admin", { token }))}>
          GET /user/admin
        </button>

        <button disabled={!isAuthed} onClick={() => run(() => apiFetch("/user/developer", { token }))}>
          GET /user/developer
        </button>

        <button disabled={!isAuthed} onClick={() => run(() => apiFetch("/frcm/", { token }))}>
          GET /frcm/ (admin)
        </button>
      </div>

      <div style={{ marginTop: 12 }}>
        {error && <pre style={{ color: "crimson" }}>{error}</pre>}
        {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
      </div>
    </div>
  );
}