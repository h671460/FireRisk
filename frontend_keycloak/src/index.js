import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { ReactKeycloakProvider } from "@react-keycloak/web";
import keycloak from "./keycloak-config";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <ReactKeycloakProvider
      authClient={keycloak}
      initOptions={{
        onLoad: "login-required",   // ✅ force login on page load
        checkLoginIframe: false,
        pkceMethod: "S256",
      }}
    >
      <App />
    </ReactKeycloakProvider>
  </React.StrictMode>
);