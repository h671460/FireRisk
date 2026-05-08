CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE TABLE IF NOT EXISTS fire_risk (
  time          TIMESTAMPTZ      NOT NULL,
  lat           DOUBLE PRECISION NOT NULL,
  lon           DOUBLE PRECISION NOT NULL,
  location      TEXT             NOT NULL,
  temperature   DOUBLE PRECISION,
  humidity      DOUBLE PRECISION,
  wind_speed    DOUBLE PRECISION,
  risk_score    DOUBLE PRECISION,
  risk_level    TEXT,
  created_at    TIMESTAMPTZ      NOT NULL DEFAULT now(),
  PRIMARY KEY (time, lat, lon, created_at)
);
SELECT create_hypertable('fire_risk', 'time', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS fire_risk_location_time_idx
  ON fire_risk (location, time DESC);
CREATE INDEX IF NOT EXISTS fire_risk_time_idx
  ON fire_risk (time DESC);