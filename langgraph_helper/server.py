from fastapi import FastAPI
from pydantic import BaseModel

from fact_checker import run_fact_check

app = FastAPI(title="AI Search Visibility - Fact-checker")


class FactCheckRequest(BaseModel):
    data: dict      # research data from n8n (with key_facts)
    report: str     # the report written by n8n


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/fact-check")
def fact_check(req: FactCheckRequest):
    return run_fact_check(req.data, req.report)