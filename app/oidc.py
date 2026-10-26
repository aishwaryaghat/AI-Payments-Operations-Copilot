"""Validate externally issued RS256 JWT access tokens against an issuer JWKS."""
import os
from functools import lru_cache
import jwt
from fastapi import HTTPException

@lru_cache(maxsize=2)
def _client(url: str):
    return jwt.PyJWKClient(url, timeout=5, lifespan=300)

def verify_external_token(token: str) -> dict:
    try:
        key = _client(os.environ["OIDC_JWKS_URL"]).get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token, key.key, algorithms=["RS256"],
            issuer=os.environ["OIDC_ISSUER"], audience=os.environ["OIDC_AUDIENCE"],
            options={"require": ["exp", "sub", "iss", "aud"]}
        )
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid access token")
    roles = claims.get("roles", [])
    if isinstance(roles, str):
        roles = [roles]
    role = "analyst" if "analyst" in roles else "viewer"
    return {"username": claims["sub"], "role": role}
