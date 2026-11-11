import json
import os
import sys
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

load_dotenv()

# Stronger model for checking; change here if it gives an error (e.g. "gpt-4o-mini")
MODEL = "gpt-5.4-mini"
llm = ChatOpenAI(model=MODEL, api_key=os.getenv("OPEN_API_KEY"))

MAX_FIXES = 2


# ---------- State: what the graph remembers between steps ----------
class State(TypedDict):
    data: dict      # research data from n8n
    report: str     # the report being checked
    issues: list    # verified mistakes found
    attempts: int   # how many times we fixed the report


def parse_json(text: str) -> dict:
    """Read JSON from the LLM answer, even if it is wrapped in ```json fences."""
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"issues": []}


# ---------- Node 1: check the report against the key facts ----------
def check_facts(state: State) -> dict:
    key_facts = state["data"].get("key_facts", [])
    prompt = f"""You are a strict fact-checker for an SEO/GEO report.

IMPORTANT:
- Google position 1 is the BEST. A lower number means a better ranking.
- KEY FACTS are calculated by code and are ALWAYS correct.
- Only flag a claim if it clearly contradicts one specific key fact.
- If a claim agrees with the key facts, it is correct. Do not flag it.

For each error, quote the exact key fact it contradicts (copy it word for word).
Return ONLY JSON: {{"issues": [{{"claim": "the wrong sentence", "fact": "exact key fact"}}]}}
If everything is correct, return {{"issues": []}}

KEY FACTS:
{json.dumps(key_facts, indent=2)}

REPORT:
{state["report"]}"""
    result = parse_json(llm.invoke(prompt).content)

    # Keep only issues that point to a real key fact (filters out hallucinated issues)
    issues = [
        i for i in result.get("issues", [])
        if isinstance(i, dict) and i.get("fact") in key_facts
    ]
    print(f"🔍 Check {state['attempts'] + 1}: {len(issues)} verified issue(s)")
    for i in issues:
        print("   - Wrong:", i["claim"])
        print("     Fact: ", i["fact"])
    return {"issues": issues}


# ---------- Node 2: fix only the verified mistakes ----------
def fix_report(state: State) -> dict:
    prompt = f"""Fix ONLY these factual errors in the report. Each error shows the wrong claim
and the correct fact. Keep the same structure, headings, tables and tone.
Change nothing else. Return only the corrected Markdown report.

Remember: Google position 1 is the best; a lower number means a better ranking.

ERRORS TO FIX:
{json.dumps(state["issues"], indent=2)}

REPORT:
{state["report"]}"""
    fixed = llm.invoke(prompt).content.strip()
    print("🛠️  Report fixed")
    return {"report": fixed, "attempts": state["attempts"] + 1}


# ---------- Decision: fix again or finish? ----------
def route(state: State) -> str:
    if state["issues"] and state["attempts"] < MAX_FIXES:
        return "fix"
    return "done"


# ---------- Build the graph ----------
graph = StateGraph(State)
graph.add_node("check_facts", check_facts)
graph.add_node("fix_report", fix_report)
graph.set_entry_point("check_facts")
graph.add_conditional_edges("check_facts", route, {"fix": "fix_report", "done": END})
graph.add_edge("fix_report", "check_facts")
app = graph.compile()


def run_fact_check(data: dict, report: str) -> dict:
    final = app.invoke({"data": data, "report": report, "issues": [], "attempts": 0})
    status = "passed" if not final["issues"] else "issues remaining"
    return {
        "report": final["report"],
        "status": status,
        "fixes": final["attempts"],
        "remaining_issues": final["issues"],
    }


# ---------- Run from the terminal ----------
if __name__ == "__main__":
    data_path, report_path = sys.argv[1], sys.argv[2]
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):  # n8n output is a list with one item
        data = data[0]
    with open(report_path, encoding="utf-8") as f:
        report = f.read()

    result = run_fact_check(data, report)

    out_path = report_path.replace(".md", "_checked.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result["report"])
        f.write(f"\n\n---\n*Fact-check: {result['status']} after {result['fixes']} fix(es).*\n")

    print(f"\n✅ Fact-check {result['status']} ({result['fixes']} fix(es)) → saved to {out_path}")