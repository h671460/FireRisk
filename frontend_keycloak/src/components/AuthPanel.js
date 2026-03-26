import React from "react";
import { useKeycloak } from "@react-keycloak/web";

export default function AuthPanel() {
  const { keycloak, initialized } = useKeycloak();

  if (!initialized) return <p>Loading auth…</p>;

  const isAuthed = !!keycloak.authenticated;
  const username =
    keycloak?.tokenParsed?.preferred_username ||
    keycloak?.tokenParsed?.email ||
    "(unknown)";

  return (
    <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
      <span>
        Status: <b>{isAuthed ? `Logged in as ${username}` : "Logged out"}</b>
      </span>

      {!isAuthed ? (
        <button onClick={() => keycloak.login({ prompt: "login" })}>Login</button>
      ) : (
        <button onClick={() => keycloak.logout({ redirectUri: window.location.origin })}>
          Logout
        </button>
      )}
    </div>
  );
}