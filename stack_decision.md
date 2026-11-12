# Stack Decision

**Primary stack:** n8n
**Helper:** LangGraph (fact-checker), deployed on Render with FastAPI

## Why n8n is the primary stack

The workflow is a clear sequence (trigger → collect Google, AI-answer and news data → compare → write report → deliver), which fits n8n's visual node design. n8n has built-in nodes for HTTP APIs, OpenAI, Pinecone RAG, file creation and email, so I could build a reliable end-to-end flow quickly, with retries and error paths on every API call. SEO and marketing teams already use automation tools like n8n, so it's easy for them to understand, run regularly and adapt (e.g. new queries or competitors) without writing code.

## Why LangGraph is a helper, not the primary stack

The main flow doesn't need complex agent loops, so LangGraph isn't needed for orchestration. But one step does need real reasoning with a loop: **fact-checking the report**. LLMs sometimes misread rankings or invent comparisons, so I built a small LangGraph agent with three nodes:

- **check_facts:** finds suspected errors; each must cite a key fact calculated in n8n
- **verify_issues:** a second check removes false alarms
- **fix_report:** fixes only verified errors, then the report is checked again (max 2 rounds)

This conditional check → verify → fix loop with shared state is exactly what LangGraph is built for, and would be hard to express cleanly in n8n. n8n calls it via HTTP and falls back to the original report if the service is unavailable, so the main flow always completes.

I deployed it on Render (instead of running it locally with ngrok) so the agent works autonomously, even when my laptop is off. The free tier sleeps when idle, so the workflow wakes it up at the start of each run.

## Trade-offs

| | n8n | LangGraph |
|---|---|---|
| Time to demo | Fast (visual, built-in nodes) | Slower (Python code + hosting) |
| Ops integration | Strong (APIs, email, scheduling) | Needs a server (Render) |
| Branching / loops | Basic | Strong (state, conditional edges, loops) |
| Control & testing | Visual debugging | Full code control, local tests |
| Used here for | Orchestration end-to-end | Fact-checking loop only |