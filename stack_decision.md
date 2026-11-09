# Stack Decision

**Primary stack:** n8n
**Helper:** LangGraph (one reasoning sub-task)

## Why n8n
The workflow is a clear sequence (trigger → collect Google, AI-answer and news data → compare → write report → deliver), which fits n8n's visual node design. n8n has built-in nodes for HTTP APIs, AI agents, Pinecone RAG, scheduling and email, so I can build a reliable end-to-end flow quickly. SEO and marketing teams already use automation tools like n8n, so it's easy for them to understand, run weekly and adapt.

## Why LangGraph is secondary
The main flow doesn't need complex custom agent loops, so LangGraph isn't the primary stack for the MVP. I use it only as a small helper, called from n8n via HTTP, to reason over the collected data and decide the top gaps and recommendations.