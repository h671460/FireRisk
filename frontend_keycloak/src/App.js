import React from "react";
import AuthPanel from "./components/AuthPanel";
import ApiTester from "./components/ApiTester";
import FrcmRangeForm from "./components/FrcmRangeForm";
import TokenPanel from "./components/TokenPanel";

export default function App() {
  return (
    <div style={{ fontFamily: "sans-serif", padding: 20, maxWidth: 1100, margin: "0 auto" }}>
      <h2>React ↔ Keycloak ↔ FastAPI</h2>

      <AuthPanel />

      <ApiTester />

      <FrcmRangeForm />

      <TokenPanel />
    </div>
  );
}