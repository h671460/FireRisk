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
      initOptions={{ onLoad: "login-required", checkLoginIframe: false, pkceMethod: "S256" }}
      onEvent={(event, error) => console.log("KC event", event, error)}
      onTokens={(tokens) => console.log("KC tokens", tokens)}
    >
      <App />
    </ReactKeycloakProvider>
  </React.StrictMode>
);