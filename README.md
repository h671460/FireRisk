# FireRisk

FireRisk is a Python-based project for fire risk prediction.

## Architecture

![FireRisk Architecture](images/FireRisk%20-%20Architecture%20Sprint%205.svg)

FireRisk follows a microservices architecture with all external traffic routed through nginx as a reverse proxy.

### nginx

nginx is the single entry point for all external traffic, routing requests to the appropriate services:
- `https://localhost/` - serves the frontend client
- `https://localhost/auth` - proxies to Keycloak for authentication
- `https://localhost/api/v1` - proxies to the frcm-api backend

SSL termination is handled at the nginx layer using self-signed certificates for local development.

### Keycloak

Keycloak handles authentication and authorization. It manages two realms: `master_realm` for admin access and `frcm_realm` for application users. User data is persisted in a dedicated PostgreSQL database.

The realm configuration including clients, roles, and users is exported and automatically imported on startup, so no manual Keycloak setup is required.

### frcm-api

The core backend service exposing a REST API. It is internally organized into three services:
- `database service` - reads and writes fire risk records to TimescaleDB
- `frcm service` - orchestrates fire risk computation using the dynamic-frcm library
- `frcm lib` - fetches real-time weather data from the MET API (Norwegian Meteorological Institute)

### TimescaleDB

Stores all computed fire risk records as time series data, optimized for time-based queries.

### MQTT Publisher

A Python script that fetches fire risk predictions and publishes them to an external MQTT broker. External client dashboards can subscribe to these topics via a subscriber/forwarder to receive live fire risk updates.

The script can be run manually or scheduled using cron to execute at a desired interval.

---

## Prerequisites

- Docker Desktop installed and running on your machine

---

## Setup

### 1. Create the `.env` file

In the root of the project, create a file named `.env` and fill in the following environment variables:

```dotenv
# postgres for keycloak
POSTGRES_USER=keycloak
POSTGRES_PASSWORD=keycloak
POSTGRES_DB=keycloak

KC_ADMIN_USERNAME=admin
KC_ADMIN_PASSWORD=admin
KC_SOURCE_ENDPOINT=localhost/auth
KC_HOSTNAME=https://${KC_SOURCE_ENDPOINT}
KC_HOSTNAME_ADMIN=https://${KC_SOURCE_ENDPOINT}

# nginx external ports
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443

# timescaledb
TIMESCALE_USER=timescale
TIMESCALE_PASSWORD=timescale
TIMESCALE_DATABASE=timescaledb
TIMESCALE_HOST=timescaledb
TIMESCALE_PORT=5432
TIMESCALE_SCHEMA=public

# frcm-api
APP_HOST=0.0.0.0
APP_PORT=6767
REALM=frcm-realm
CLIENT_ID=frcm-api-client
CLIENT_SECRET="E6rxRIkF7RwV4RXYxL80DlTgvimX5f1a"
KEYCLOAK_PUBLIC_URL=https://${KC_SOURCE_ENDPOINT}/
KEYCLOAK_INTERNAL_URL=http://keycloak:8080/auth/

# dynamic-frcm uses https://frost.met.no/ - request credentials at:
# https://frost.met.no/auth/requestCredentials.html
MET_CLIENT_ID=
MET_CLIENT_SECRET=

AUTHORIZATION_URL=https://${KC_SOURCE_ENDPOINT}/realms/frcm-realm/protocol/openid-connect/auth
TOKEN_URL=https://${KC_SOURCE_ENDPOINT}/realms/frcm-realm/protocol/openid-connect/token

# frontend
HOST=0.0.0.0
PORT=3000
REACT_APP_API=https://localhost/api/v1
REACT_APP_KEYCLOAK_URL=https://localhost/auth
REACT_APP_KEYCLOAK_REALM=frcm-realm
REACT_APP_KEYCLOAK_CLIENT_ID=frcm-react-app-client

# mqtt env variables from hivemq
BROKER_USERNAME=''
BROKER_PASSWORD=''
BROKER_HOST=''
BROKER_PORT=
BROKER_TOPIC="ada502/firerisk/60.383/5.3327"
TOPIC_QOS=1
FIRERISK_PUBLISHER_CLIENT_ID=ada502pubfrcm
PUBLISH_INTERVAL=30

KEYCLOAK_TOKEN_URL="https://nginx/auth/realms/frcm-realm/protocol/openid-connect/token"
MQTT_KEYCLOAK_CLIENT_ID="mqtt-client"
MQTT_KEYCLOAK_CLIENT_SECRET="otSZwrTEd3ZNXZEJPQLlNqaQenhWyAxI"
FIRERISK_API_URL="https://nginx/api/v1/frcm/range"
```

> **Note:** `MET_CLIENT_ID` and `MET_CLIENT_SECRET` are required for fetching weather data from the Norwegian Meteorological Institute. Request credentials at [https://frost.met.no/auth/requestCredentials.html](https://frost.met.no/auth/requestCredentials.html). Fill in your MQTT broker credentials if you want to use the publisher.

### 2. Load environment variables

```bash
source ./setup_terminal_env.sh
```

### 3. Generate SSL certificates

**Windows (Git Bash):**

```bash
mkdir -p nginx/certs
MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/key.pem \
  -out nginx/certs/cert.pem \
  -subj "/CN=localhost"
```

**Mac/Linux:**

```bash
mkdir -p nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/key.pem \
  -out nginx/certs/cert.pem \
  -subj "/CN=localhost"
```

### 4. Start all services

```bash
docker compose up -d --build
```

Keycloak will automatically import the realm configuration on first startup. This includes all clients, roles, and users, so no manual Keycloak setup is needed.

### 5. Verify the application is running

Once all containers are up, the following endpoints should be accessible:

- `https://localhost/auth` - Keycloak
- `https://localhost/api/v1` - frcm-api
- `https://localhost/` - Frontend

> **Note:** Since the certificate is self-signed, your browser will show a security warning. Click **Advanced** and then **Continue anyway** to proceed.

> **Note:** Keycloak may take a minute or two to fully start up. If the page does not load immediately, wait and refresh.

To follow the Keycloak startup logs:

```bash
docker compose logs -f keycloak
```

Wait until you see `http://0.0.0.0:8080` in the logs before proceeding, then press `CTRL+C` to exit the logs.

### 6. Default credentials

The following user is available out of the box:

| Username | Password |
|----------|----------|
| anne     | 1234     |

Admin credentials are set via `KC_ADMIN_USERNAME` and `KC_ADMIN_PASSWORD` in your `.env` file.

---

## Running the MQTT Publisher

The MQTT publisher fetches fire risk predictions and publishes them to your configured broker:

```bash
docker exec firerisk-frcm-api-1 uv run python src/mqtt/frcm_publisher.py --configfile=src/mqtt/connector/config-ada502-pub.yml
```

> **Note:** The publisher runs once per execution and then exits. It can be scheduled using cron to run at a desired interval.

---