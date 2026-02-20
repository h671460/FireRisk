from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID  # pip require python-keycloak
from src.firerisk.api_keycloak.config.keycloak_config import settings
from fastapi import Security, HTTPException, status, Depends
from src.firerisk.api_keycloak.schemas.userPayload import userPayload

from pprint import pprint

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl=settings.token_url
# )


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{settings.keycloak_public_url}realms/{settings.realm}/protocol/openid-connect/auth?prompt=login",#?prompt=login
    tokenUrl=f"{settings.keycloak_public_url}realms/{settings.realm}/protocol/openid-connect/token",
)

keycloak_openid = KeycloakOpenID(
    server_url=settings.keycloak_internal_url,
    client_id=settings.client_id,
    realm_name=settings.realm,
    client_secret_key=settings.client_secret,
    verify=True
)


async def get_idp_public_key():
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{keycloak_openid.public_key()}"
        "\n-----END PUBLIC KEY-----"
    )


async def get_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return keycloak_openid.decode_token(
            token,
            validate=True,
            check_claims={"aud": None}  # disables aud check
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_user_info(payload: dict = Depends(get_payload)) -> userPayload:
    try:
        return userPayload(
            id=payload.get("sub"),
            username=payload.get("preferred_username"),
            email=payload.get("email"),
            first_name=payload.get("given_name"),
            last_name=payload.get("family_name"),
            realm_roles=payload.get("realm_access", {}).get("roles", []),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


from fastapi import Depends, HTTPException, status
from typing import List, Callable

def has_roles(required_roles: List[str]) -> Callable:
    async def checker(user: userPayload = Depends(get_user_info)) -> userPayload:
        user_roles = user.realm_roles 

        if not any(r in user_roles for r in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role permissions. Required: {required_roles}",
            )
        return user

    return checker
