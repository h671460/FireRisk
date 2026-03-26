import os

from src.firerisk.api_keycloak.schemas.authConfiguration import authConfiguration
from dotenv import load_dotenv

load_dotenv(".env.keycloak")

KEYCLOAK_PUBLIC_URL = os.getenv("KEYCLOAK_PUBLIC_URL")
KEYCLOAK_INTERNAL_URL = os.getenv("KEYCLOAK_INTERNAL_URL")
REALM = os.getenv("REALM")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")
TOKEN_URL = os.getenv("TOKEN_URL")


settings = authConfiguration(
    keycloak_public_url=KEYCLOAK_PUBLIC_URL,
    keycloak_internal_url=KEYCLOAK_INTERNAL_URL,
    realm=REALM,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorization_url=AUTHORIZATION_URL,
    token_url=TOKEN_URL,
)
