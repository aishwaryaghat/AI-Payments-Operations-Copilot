import logging
from datetime import date
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from .security import issue_token, current_user, require_analyst, redact, unsafe_request
from .retrieval import answer
from .analytics import run_analytics

app = FastAPI(title="AI Payments Operations Copilot", version="0.1.0")
logger = logging.getLogger("copilot.audit")

class Question(BaseModel):
    question: str = Field(min_length=3, max_length=2000)

class AnalyticsRequest(BaseModel):
    intent: str
    business_date: date

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/token")
def token(form: OAuth2PasswordRequestForm = Depends()):
    return {"access_token": issue_token(form.username, form.password), "token_type": "bearer"}

@app.post("/ask")
def ask(request: Question, user: dict = Depends(current_user)):
    if unsafe_request(request.question):
        logger.warning("blocked_request user=%s", user["username"])
        raise HTTPException(status_code=400, detail="Request blocked by safety policy")
    logger.info("knowledge_query user=%s", user["username"])
    return answer(redact(request.question))

@app.post("/analytics")
def analytics(request: AnalyticsRequest, user: dict = Depends(require_analyst)):
    logger.info("analytics_query user=%s intent=%s", user["username"], request.intent)
    try:
        return run_analytics(request.intent, request.business_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
