"""Payment operations copilot API, permission checks and durable audits."""
from datetime import date
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from .security import issue_token, current_user, require_analyst, redact, unsafe_request
from .retrieval import answer
from .analytics import run_analytics
from .audit import audit_event
from .llm_rag import router as rag_router

app = FastAPI(title="AI Payments Operations Copilot", version="0.2.0")
app.include_router(rag_router)

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
        audit_event(user["username"], "knowledge_query", "blocked")
        raise HTTPException(status_code=400, detail="Request blocked by safety policy")
    result = answer(redact(request.question))
    audit_event(user["username"], "knowledge_query", "success")
    return result

@app.post("/analytics")
def analytics(request: AnalyticsRequest, user: dict = Depends(require_analyst)):
    try:
        result = run_analytics(request.intent, request.business_date)
    except ValueError as exc:
        audit_event(user["username"], "analytics_query", "rejected", request.intent[:80])
        raise HTTPException(status_code=400, detail=str(exc))
    audit_event(user["username"], "analytics_query", "success", request.intent)
    return result
