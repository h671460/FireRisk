import React from "react";
import { useKeycloak } from "@react-keycloak/web";
import { useNavigate } from "react-router-dom";

export default function HomePage() {
  const { keycloak, initialized } = useKeycloak();
  const navigate = useNavigate();

  if (!initialized) {
    return <p className="page-container">Loading...</p>;
  }

  const isAuthed = !!keycloak.authenticated;

  function handleLogin() {
    keycloak.login({
      redirectUri: `${window.location.origin}/`,
    });
  }

  function handleGoToForecast() {
    if (!isAuthed) {
      keycloak.login({
        redirectUri: `${window.location.origin}/forecast`,
      });
      return;
    }

    navigate("/forecast");
  }

  return (
    <div className="page-container">
      <section className="hero">
        <h1>Fire Risk Forecast</h1>
        <p>
          This application provides fire risk forecasts based on longitude,
          latitude, and a selected time range. Log in with Keycloak to access
          the forecast computation page.
        </p>

        <div className="hero-actions">
          {!isAuthed ? (
            <button className="primary-btn" onClick={handleLogin}>
              Log In with Keycloak
            </button>
          ) : (
            <button className="primary-btn" onClick={handleGoToForecast}>
              Go to Fire Risk Forecast
            </button>
          )}

          <button className="secondary-btn" onClick={handleGoToForecast}>
            Fire Risk Forecast
          </button>
        </div>
      </section>
    </div>
  );
}