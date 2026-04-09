import os

from src.firerisk.api.schemas.authConfiguration import authConfiguration
from dotenv import load_dotenv

if os.path.exists(".env"):  
    load_dotenv(".env")

KEYCLOAK_PUBLIC_URL = os.getenv("KEYCLOAK_PUBLIC_URL", "http://localhost:8080")
KEYCLOAK_INTERNAL_URL = os.getenv("KEYCLOAK_INTERNAL_URL", "http://keycloak:8080")
REALM = os.getenv("REALM", "frcm-realm")
CLIENT_ID = os.getenv("CLIENT_ID", "frcm-api-client")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "your-client-secret")
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL", f"{KEYCLOAK_PUBLIC_URL}/realms/{REALM}/protocol/openid-connect/auth")
TOKEN_URL = os.getenv("TOKEN_URL", f"{KEYCLOAK_PUBLIC_URL}/realms/{REALM}/protocol/openid-connect/token")


settings = authConfiguration(
    keycloak_public_url=KEYCLOAK_PUBLIC_URL,
    keycloak_internal_url=KEYCLOAK_INTERNAL_URL,
    realm=REALM,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorization_url=AUTHORIZATION_URL,
    token_url=TOKEN_URL,
)
