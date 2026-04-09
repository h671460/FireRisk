# FireRisk

FireRisk is a Python-based project for fire risk prediction.

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

# Go to the client -> Credentials and copy the client secret
CLIENT_SECRET=""
KEYCLOAK_PUBLIC_URL=https://${KC_SOURCE_ENDPOINT}/
KEYCLOAK_INTERNAL_URL=http://keycloak:8080/auth/

# dynamic.frcm uses https://frost.met.no/ - request credentials at:
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
BROKER_USERNAME=""
BROKER_PASSWORD=""
BROKER_HOST=""
BROKER_PORT=
BROKER_TOPIC="ada502/firerisk/60.383/5.3327"
TOPIC_QOS=1
FIRERISK_PUBLISHER_CLIENT_ID=ada502pubfrcm
PUBLISH_INTERVAL=30

KEYCLOAK_TOKEN_URL="https://nginx/auth/realms/frcm-realm/protocol/openid-connect/token"
MQTT_KEYCLOAK_CLIENT_ID="mqtt-client"
# Go to the mqtt-client -> Credentials and copy the client secret
MQTT_KEYCLOAK_CLIENT_SECRET=""
FIRERISK_API_URL="https://nginx/api/v1/frcm/range"
```

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

### 4. Comment out services in `docker-compose.yml`

In `docker-compose.yml`, make sure the `nginx` depends_on section looks like this:

```yaml
depends_on:
  keycloak:
    condition: service_started
  # frcm-api:
  #   condition: service_started
  # frontend:
  #   condition: service_started
```

### 5. Comment out location blocks in `nginx/conf.d/localhost.conf`

Make sure the api and frontend location blocks are commented out:

```nginx
location /auth/ {
    proxy_pass              http://keycloak:8080/auth/;
    proxy_set_header        Host                $host;
    proxy_set_header        X-Forwarded-Proto   https;
    proxy_set_header        X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Host    $host;
    proxy_set_header        X-Forwarded-Port    443;
}

# location /api/v1/ {
#     proxy_pass              http://frcm-api:6767/;
#     ...
# }

# location / {
#     proxy_pass              http://frontend:3000;
#     ...
# }
```

### 6. Start Keycloak

```bash
docker compose up -d --build nginx
```

### 7. Access Keycloak

Once the containers are running, open your browser and go to `https://localhost/auth/`.

> **Note:** Keycloak may take a minute or two to fully start up. If the page does not load immediately, wait a moment and refresh.

Since the certificate is self-signed, your browser will show a security warning. Click **Advanced** (or **Show details**) and then **Continue anyway** (or **Proceed to localhost**). Log in with the admin credentials from your `.env` file.

---

## Keycloak Configuration

### Create a realm

After logging in, create a new realm named `frcm-realm`. Then go to **Realm settings -> Login** and enable the following:

- User registration: **On**
- Forgot password: **On**
- Remember me: **On**

### Create clients

Go to **Clients** and create the following three clients.

#### frcm-api-client

Create a client with Client ID `frcm-api-client`. Enable **Client authentication** and check: Standard flow, Direct access grants, Implicit flow, Service account roles.

- Valid redirect URIs: `https://localhost/api/v1/*`
- Web origins: `https://localhost/api/v1/`

#### frcm-react-app-client

Create a client with Client ID `frcm-react-app-client`. Leave **Client authentication** off and check: Standard flow, Direct access grants.

- Valid redirect URIs: `https://localhost/*`
- Web origins: `https://localhost/`

#### mqtt-client

Create a client with Client ID `mqtt-client`. Enable **Client authentication** and check: Standard flow, Direct access grants, Implicit flow, Service account roles. No redirect URIs needed.

### Create roles

Go to **Realm roles** and create the following roles: `admin` and `developer`.

The frcm-api checks for `admin`, `developer`, and `default-roles-frcm-realm`. The `default-roles-frcm-realm` role is assigned to all users automatically by Keycloak.

### Create users

Go to **Users**, create the users you need, and assign the appropriate roles to each.

---

## Running the Full Application

The frcm-api runs internally on port `6767` as set in `src/firerisk/api/__init__.py`. This can be changed via `APP_PORT` in your `.env` file.

### 1. Update environment variables

Update the Keycloak and MQTT variables in your `.env` file, then reload:

```bash
source ./setup_terminal_env.sh
```

### 2. Uncomment services in `docker-compose.yml`

```yaml
depends_on:
  keycloak:
    condition: service_started
  frcm-api:
    condition: service_started
  frontend:
    condition: service_started
```

### 3. Uncomment location blocks in `nginx/conf.d/localhost.conf`

```nginx
location /api/v1/ {
    proxy_pass              http://frcm-api:6767/;
    proxy_set_header        Host                $host;
    proxy_set_header        X-Forwarded-Proto   https;
    proxy_set_header        X-Forwarded-For     $proxy_add_x_forwarded_for;
    proxy_set_header        X-Forwarded-Host    $host;
    proxy_set_header        X-Forwarded-Port    443;
}

location / {
    proxy_pass              http://frontend:3000;
    proxy_set_header        Host                $host;
    proxy_set_header        X-Forwarded-Proto   https;
    proxy_set_header        X-Forwarded-For     $proxy_add_x_forwarded_for;
}
```

### 4. Start all services

```bash
docker compose down
docker compose up -d --build
```

### 5. Verify the application is running

Once all containers are up, the following endpoints should be accessible:

- `https://localhost/auth` - Keycloak
- `https://localhost/api/v1` - frcm-api
- `https://localhost/` - Frontend

### 6. Run the MQTT publisher

```bash
docker exec firerisk-frcm-api-1 uv run python src/mqtt/frcm_publisher.py --configfile=src/mqtt/connector/config-ada502-pub.yml
```

> **Note:** The publisher runs once per execution and then exits. For automated periodic publishing during deployment, this command can be scheduled using cron to run at the desired interval.

---

## Demo

[![Watch the demo](https://drive.google.com/thumbnail?id=1mtzZBOPRZ4B8-WT2dQaLFJuRzOLPUc23)](https://drive.google.com/file/d/1mtzZBOPRZ4B8-WT2dQaLFJuRzOLPUc23/view?usp=sharing)