-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- fire_risk data table
CREATE TABLE IF NOT EXISTS fire_risk (
  time        TIMESTAMPTZ NOT NULL,
  lat         DOUBLE PRECISION,
  lon         DOUBLE PRECISION,
  location    TEXT NOT NULL,
  temperature DOUBLE PRECISION,
  humidity    DOUBLE PRECISION,
  wind_speed  DOUBLE PRECISION,
  risk_score  DOUBLE PRECISION,
  risk_level  TEXT NOT NULL,
  PRIMARY KEY (time, location)
);

SELECT create_hypertable('fire_risk', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS fire_risk_location_time_idx
  ON fire_risk (location, time DESC);

CREATE INDEX IF NOT EXISTS fire_risk_time_idx
  ON fire_risk (time DESC);



INSERT INTO fire_risk (time, lat, lon, location, temperature, humidity, wind_speed, risk_score, risk_level)
VALUES ('2024-01-01 00:00:00+00', 34.05, -118.25, 'Los Angeles', 30.0, 20.0, 5.0, 0.8, 'High'),
('2024-01-01 01:00:00+00', 34.05, -118.25, 'Los Angeles', 28.0, 25.0, 3.0, 0.6, 'Medium'),
('2024-01-01 02:00:00+00', 34.05, -118.25, 'Los Angeles', 25.0, 30.0, 2.0, 0.4, 'Low');