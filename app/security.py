import os
import secrets
import re
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET = os.getenv("COPILOT_JWT_SECRET", "INSECURE_DEVELOPMENT_ONLY_CHANGE_ME")
ALGORITHM = "HS256"
oauth = OAuth2PasswordBearer(tokenUrl="token")
USERS = {"analyst": {"password": "demo-analyst-password", "role": "analyst"},
         "viewer": {"password": "demo-viewer-password", "role": "viewer"}}

def issue_token(username: str, password: str) -> str:
    if os.getenv("COPILOT_AUTH_MODE", "demo") != "demo":
        raise HTTPException(status_code=403, detail="Use external OIDC authentication")
    user = USERS.get(username)
    if not user or not secrets.compare_digest(user["password"], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    payload = {"sub": username, "role": user["role"],
               "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def current_user(token: str = Depends(oauth)) -> dict:
    if os.getenv("COPILOT_AUTH_MODE", "demo") == "oidc":
        from .oidc import verify_external_token
        return verify_external_token(token)
    try:
        claims = jwt.decode(token, SECRET, algorithms=[ALGORITHM], options={"require": ["sub", "exp"]})
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = USERS.get(claims["sub"])
    if not user or claims.get("role") != user["role"]:
        raise HTTPException(status_code=401, detail="Invalid user")
    return {"username": claims["sub"], "role": user["role"]}

def require_analyst(user: dict = Depends(current_user)) -> dict:
    if user["role"] != "analyst":
        raise HTTPException(status_code=403, detail="Analyst role required")
    return user

def redact(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", text)
    return re.sub(r"\b\d{12,19}\b", "[REDACTED_ACCOUNT]", text)

def unsafe_request(text: str) -> bool:
    patterns = (r"ignore (all )?(previous|prior) instructions", r"reveal (the )?(system|developer) prompt",
                r"disable (all )?(safety|security)", r"bypass (the )?(access|authorization)")
    return any(re.search(p, text, re.I) for p in patterns)
