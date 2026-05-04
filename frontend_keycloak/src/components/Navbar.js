import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useKeycloak } from "@react-keycloak/web";

export default function Navbar() {
  const { keycloak, initialized } = useKeycloak();
  const location = useLocation();

  if (!initialized) {
    return null;
  }

  const isAuthed = !!keycloak.authenticated;
  const username =
    keycloak?.tokenParsed?.preferred_username ||
    keycloak?.tokenParsed?.email ||
    "User";

  function handleLogin() {
    keycloak.login({
      redirectUri: `${window.location.origin}${location.pathname}`,
    });
  }

  function handleForecastClick(e) {
    if (!isAuthed) {
      e.preventDefault();
      keycloak.login({
        redirectUri: `${window.location.origin}/forecast`,
      });
    }
  }

  function handleLogout() {
    keycloak.logout({
      redirectUri: `${window.location.origin}/`,
    });
  }

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link className="nav-brand" to="/">
          Fire Risk Forecast
        </Link>
      </div>

      <div className="navbar-right">
        <Link className="nav-link" to="/">
          Home
        </Link>

        <Link className="nav-link" to="/forecast" onClick={handleForecastClick}>
          Fire Risk Forecast
        </Link>

        {!isAuthed ? (
          <button className="nav-button" onClick={handleLogin}>
            Log In
          </button>
        ) : (
          <>
            <span className="nav-user">Hi, {username}</span>
            <button className="nav-button" onClick={handleLogout}>
              Log Out
            </button>
          </>
        )}
      </div>
    </nav>
  );
}