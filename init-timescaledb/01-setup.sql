-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- fire_risk data table
CREATE TABLE IF NOT EXISTS fire_risk (
  time          TIMESTAMPTZ      NOT NULL,
  lat           DOUBLE PRECISION NOT NULL,
  lon           DOUBLE PRECISION NOT NULL,
  location      TEXT             NOT NULL,
  temperature   DOUBLE PRECISION NOT NULL,
  humidity      DOUBLE PRECISION NOT NULL,
  wind_speed    DOUBLE PRECISION NOT NULL,
  risk_score    DOUBLE PRECISION NOT NULL,
  risk_level    TEXT             NOT NULL,
  created_at    TIMESTAMPTZ      NOT NULL DEFAULT now(),
  PRIMARY KEY (time, lat, lon, created_at)
);

SELECT create_hypertable('fire_risk', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS fire_risk_location_time_idx
  ON fire_risk (location, time DESC);

CREATE INDEX IF NOT EXISTS fire_risk_time_idx
  ON fire_risk (time DESC);