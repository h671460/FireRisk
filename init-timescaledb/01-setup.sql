-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- fire_risk data table
CREATE TABLE IF NOT EXISTS fire_risk (
  time        TIMESTAMPTZ NOT NULL,
  lat         DOUBLE PRECISION NOT NULL,
  lon         DOUBLE PRECISION NOT NULL,
  location    TEXT NOT NULL,
  temperature DOUBLE PRECISION NOT NULL,
  humidity    DOUBLE PRECISION NOT NULL,
  wind_speed  DOUBLE PRECISION NOT NULL,
  risk_score  DOUBLE PRECISION NOT NULL,
  risk_level  TEXT NOT NULL,
  PRIMARY KEY (time, location)
);

SELECT create_hypertable('fire_risk', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS fire_risk_location_time_idx
  ON fire_risk (location, time DESC);

CREATE INDEX IF NOT EXISTS fire_risk_time_idx
  ON fire_risk (time DESC);


-- synthetic data generation
-- t_0
-- same time for all locations
\set number_rows 10000

TRUNCATE fire_risk;

WITH params AS (
  SELECT now() AS t0
),
locations AS (
  SELECT *
  FROM (VALUES
    ('Oslo', 59.9139, 10.7522),
    ('Bergen', 60.39299, 5.32415),
    ('Stavanger', 58.96998, 5.73311),
    ('Trondheim', 63.4305, 10.3951),
    ('Drammen', 59.7439, 10.2045),
    ('Fredrikstad', 59.2181, 10.9296),
    ('Skien', 59.2096, 9.6080),
    ('Kristiansand', 58.1467, 7.9956),
    ('Tonsberg', 59.2675, 10.4076),
    ('Aalesund', 62.4722, 6.1549)
  ) AS v(location, lat, lon)
),
gen AS (
  SELECT
    l.location,
    l.lat,
    l.lon,
    params.t0 - ((:number_rows - gs) * interval '1 hour') AS time,
    round(random()::numeric, 2) AS risk_score
  FROM params
  CROSS JOIN locations l
  CROSS JOIN generate_series(1, :number_rows) AS gs
)
INSERT INTO fire_risk (time, lat, lon, location, temperature, humidity, wind_speed, risk_score, risk_level)
SELECT
  g.time,
  g.lat,
  g.lon,
  g.location,
  (6
   + 3 * sin(extract(epoch from g.time) / 86400.0 * 2 * pi())
   + (random() * 1.5 - 0.75)
  )::double precision AS temperature,
  (50 + random() * 45)::double precision AS humidity,
  (random() * 15)::double precision AS wind_speed,
  g.risk_score::double precision,
  CASE
    WHEN g.risk_score >= 0.75 THEN 'High'
    WHEN g.risk_score >= 0.45 THEN 'Medium'
    ELSE 'Low'
  END AS risk_level
FROM gen g;

-- t_1