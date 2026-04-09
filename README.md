# FireRisk

FireRisk is a Python-based project for fire risk prediction.

## Prerequisites

- Docker Desktop installed and running on your machine

## Setup

### Create the `.env` file

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

# change this to your actual client secret! go to the client -> credentials and copy client secret
CLIENT_SECRET=""
KEYCLOAK_PUBLIC_URL=https://${KC_SOURCE_ENDPOINT}/
KEYCLOAK_INTERNAL_URL=http://keycloak:8080/auth/

# dynamic.frcm needs these env variables, since it uses https://frost.met.no/ API.
# you can request these values from here https://frost.met.no/auth/requestCredentials.html
MET_CLIENT_ID=
MET_CLIENT_SECRET=

# not used in code, still have it in the .env, because these env variables might be called with os.getenv("")
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
# change this to your actual mqtt-client client secret
MQTT_KEYCLOAK_CLIENT_SECRET=""
FIRERISK_API_URL="https://nginx/api/v1/frcm/range"
```

### Load environment variables

Run the following command to load the environment variables into your terminal session:

```bash
source ./setup_terminal_env.sh
```

### Generate SSL certificates

Create the certs folder and generate a self-signed certificate for local development.

On Windows (Git Bash):

```bash
mkdir -p nginx/certs
MSYS_NO_PATHCONV=1 openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/key.pem \
  -out nginx/certs/cert.pem \
  -subj "/CN=localhost"
```

On Mac/Linux:

```bash
mkdir -p nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/key.pem \
  -out nginx/certs/cert.pem \
  -subj "/CN=localhost"
```

### Check that the following are commented out

In `docker-compose.yml`, make sure the `nginx` depends_on section looks like this:

```yaml
depends_on:
  - keycloak
  # - frcm-api
  # - frontend
```

In `nginx/conf.d/localhost.conf`, make sure the api and frontend location blocks are commented out:

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

### Start Keycloak

Run the following command to start Postgres, Keycloak, and Nginx:

```bash
docker compose up -d --build nginx
```

### Access Keycloak

Once the containers are running, open your browser and go to:

```
https://localhost/auth/
```

> **Note:** Keycloak may take a minute or two to fully start up. If the page does not load immediately, wait a moment and refresh.

Since the SSL certificate is self-signed, your browser will warn you that the connection is not secure. This is expected for local development. Find the "Advanced" or "Show details" option and click "Continue anyway" or "Proceed to localhost" to access the app.

Log in with the admin credentials you set in your `.env` file.

## Keycloak Configuration

### Create a realm

After logging in as admin, create a new realm called `frcm-realm`.

Then go to **Realm settings -> Login** and turn on the following:

- User registration: **On**
- Forgot password: **On**
- Remember me: **On**

### Create clients

Head to **Clients** and create the following three clients.

#### frcm-api-client

Create a new client with Client ID `frcm-api-client`.

On the next page, turn on **Client authentication** and check the following authentication flows:

- Standard flow
- Direct access grants
- Implicit flow
- Service account roles

On the next page, set the following:

- Valid redirect URIs: `https://localhost/api/v1/*`
- Web origins: `https://localhost/api/v1/`

Save.

#### frcm-react-app-client

Create a new client with Client ID `frcm-react-app-client`.

Leave **Client authentication** off and check the following authentication flows:

- Standard flow
- Direct access grants

On the next page, set the following:

- Valid redirect URIs: `https://localhost/*`
- Web origins: `https://localhost/`

Save.

#### mqtt-client

Create a new client with Client ID `mqtt-client`.

Turn on **Client authentication** and check the following authentication flows:

- Standard flow
- Direct access grants
- Implicit flow
- Service account roles

No redirect URIs needed. Save.

### Create roles

Go to **Realm roles** and create the following roles:

- `admin`
- `developer`

The frcm-api checks for the roles `admin`, `developer`, and `default-roles-frcm-realm`, where `default-roles-frcm-realm` is assigned to all users automatically by Keycloak.

### Create users

Go to **Users** and create the users you need. Assign the appropriate roles to each user.


## Running the Full Application

The frcm-api runs internally inside its container on port `6767`, as configured in `src/firerisk/api/__init__.py`. This can be changed via the `APP_PORT` environment variable in your `.env` file.

### Start all services

Once Keycloak is configured, uncomment the following in `docker-compose.yml`:

```yaml
depends_on:
  - keycloak
  - frcm-api
  - frontend
```

And uncomment the api and frontend location blocks in `nginx/conf.d/localhost.conf`:

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

Then run:

```bash
docker compose up -d --build
```

### Run the MQTT publisher

To publish fire risk data to the MQTT broker, run the following command:

```bash
docker exec firerisk-frcm-api-1 uv run python src/mqtt/frcm_publisher.py --configfile=src/mqtt/connector/config-ada502-pub.yml
```

> **Note:** The publisher runs once per execution and then exits. For automated periodic publishing during deployment, this command can be scheduled using cron to run at the desired interval.