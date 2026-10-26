from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Synthetic policy excerpts, not official NACHA/Oracle procedures.
DOCS = [
    {"id": "DEMO-ACH-001", "title": "ACH file validation", "text": "When an ACH file fails format validation, review the error report, correct invalid records and revalidate before resubmission."},
    {"id": "DEMO-ACH-002", "title": "ACH processing cutoff", "text": "If a file misses the configured processing cutoff, check the next eligible processing window and follow the institution's approved escalation procedure."},
    {"id": "DEMO-OPS-003", "title": "Exception investigation", "text": "For payment exceptions, inspect the exception code, trace processing events, review the permitted repair action and retain an audit trail."},
    {"id": "DEMO-REC-004", "title": "Reconciliation", "text": "For reconciliation mismatches, compare settlement totals against the payment ledger and investigate unmatched transactions."}
]
VECTORIZER = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
MATRIX = VECTORIZER.fit_transform([d["text"] + " " + d["title"] for d in DOCS])

def retrieve(question: str, k: int = 3) -> list[dict]:
    scores = cosine_similarity(VECTORIZER.transform([question]), MATRIX)[0]
    matches = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    return [{**DOCS[i], "score": round(float(score), 4)} for i, score in matches[:k] if score > 0]

def answer(question: str) -> dict:
    docs = retrieve(question)
    if not docs:
        return {"answer": "I could not find supporting information in the available synthetic runbooks.", "citations": []}
    return {"answer": "Relevant runbook guidance: " + " ".join(d["text"] for d in docs),
            "citations": [{"id": d["id"], "title": d["title"], "score": d["score"]} for d in docs]}
