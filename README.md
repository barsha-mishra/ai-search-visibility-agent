# AI Search Visibility Agent 🔍

An autonomous agent that compares a brand's visibility on **Google** and in **AI assistant answers** against its competitors, and delivers a fact-checked **SEO & GEO report** with concrete recommendations by email.

**Report user:** SEO/GEO managers and marketing leads at online brands.

**What "useful" means for them:**
- See in 1 minute where the brand is visible or missing, on Google and in AI answers
- Compare the brand directly against its competitors
- Get actions they can start this week, not generic advice

---

## Why not just ask ChatGPT?

You can ask ChatGPT "Is Zalando visible online?", but you'd get a one-off opinion. This agent gives you a **measurement**:

- **Google + AI side by side:** real Google rankings (Serper) *and* what AI assistants actually answer, compared directly. ChatGPT can't tell you your live Google position.
- **Real data, not guesses:** rankings, AI mentions and news come from live APIs, with dates and sources.
- **Facts calculated in code:** brand comparisons and scores are computed by the workflow, so the AI only writes, not compares.
- **Fact-checked:** a LangGraph agent checks every claim against the data and fixes mistakes before delivery.
- **Grounded recommendations:** based on official Google and GEO guidelines (RAG with Pinecone), with sources.
- **Visibility score:** a simple score per brand (Google %, AI %, overall) shows the winner in 5 seconds.
- **Hidden competitors:** shows brands the AI recommends that you're not tracking (e.g. OTTO for Zalando).
- **Designed email report:** score bars, pie chart, color-coded tables, top 3 actions and who ranks in the Google top 3.
- **Repeatable:** same queries, competitors and format every time, so visibility can be tracked over time.
- **Automated:** one form submission → multiple queries × brands × sources → finished report in your inbox in ~2–3 minutes.

---

## Sample reports

| Report | Key insight |
|---|---|
| [Zalando vs ABOUT YOU, ASOS, Shein, H&M](reports/zalando_report_2026-11-12.md) | Zalando leads AI answers, but ABOUT YOU wins Google on most queries. ASOS is invisible on Google yet strong in AI answers, and untracked brands like OTTO show up in AI recommendations. |
| [Adidas vs Nike, Puma, New Balance](reports/adidas_report_2026-11-12.md) | No brand reaches Google's top 10 for generic queries (review sites dominate), but Adidas leads AI answers among the tracked brands. |

**The report as it arrives by email:**

![Email report part 1](docs/email_report_1.png)
![Email report part 2](docs/email_report_2.png)

---

## Architecture

![n8n workflow](docs/workflow.png)

```mermaid
flowchart TD
    A[n8n Form: brand, competitors, country, queries, email] --> B[Wake up fact-checker]
    B --> C[Clean & validate input]
    C --> D[Serper: Google rankings]
    D --> E[Extract Google positions]
    E --> F[OpenAI: AI answer check]
    F --> G[Combine Google + AI]
    G --> H[NewsAPI: brand news + relevance filter]
    H --> I[Build final dataset + hidden competitors]
    I --> J[Pinecone RAG: SEO/GEO guidelines]
    J --> K[Key facts + visibility scores calculated in code]
    K --> L[OpenAI: write report]
    L --> M[LangGraph fact-checker on Render]
    M --> N[Report file .md]
    N --> O[Designed HTML email + report attachment]
```

**LangGraph fact-checker** (`langgraph_helper/fact_checker.py`):

```mermaid
flowchart LR
    S[Report + data] --> C[check_facts]
    C --> V[verify_issues]
    V -->|real issues & < 2 fixes| F[fix_report]
    F --> C
    V -->|no issues| E[Final report ✅]
```

- **check_facts:** finds suspected errors in the text, each must cite a calculated key fact (tables are skipped, as they come straight from the data)
- **verify_issues:** a second check with the full rankings and scores removes false alarms
- **fix_report:** fixes only verified errors, max 2 rounds

---

## Stack

- **Primary: n8n** (orchestration, APIs, RAG, report, delivery). See [stack_decision.md](stack_decision.md)
- **Helper: LangGraph** (fact-checker), deployed on **Render** with FastAPI
- **LLM:** OpenAI
- **Retrieval:** Pinecone (index `seo-geo-guidelines`, OpenAI `text-embedding-3-small`)

## Tools & APIs

| Tool | Purpose |
|---|---|
| Serper | Google search results (Germany) |
| OpenAI | AI answer check, report writing, fact-checking |
| NewsAPI | Recent brand news |
| Pinecone | RAG over SEO/GEO guidelines ([sources](rag_docs/sources.md)) |
| Gmail (SMTP) | Report delivery |
| Render | Hosts the LangGraph fact-checker API |
| QuickChart | Pie chart image in the email |

---

## Error handling

- **Input validation:** stops with a clear message if required fields are missing
- **Input limits:** max 4 competitors and 6 queries; the brand can't also be listed as a competitor
- **Retries:** all API calls retry automatically
- **Continue on error:** failed APIs don't crash the run; missing data is flagged and listed in report section 7
- **Fact-checker fallback:** if the LangGraph service is unavailable, the original report is used and marked
- **Wake-up step:** wakes the Render service at the start of each run
- **Safety limits:** max 2 fix rounds, safe JSON parsing, verify step against false alarms

---

## Setup & run

**1. Clone and configure**
```bash
git clone https://github.com/barsha-mishra/ai-search-visibility-agent.git
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and add your API keys. Check them with:
```bash
python test_keys.py
```

**2. RAG (one time)**
- Create the Pinecone index: `python create_index.py`
- Import `n8n/rag_load_docs.json` into n8n and upload the PDFs listed in `rag_docs/sources.md`

**3. LangGraph fact-checker**
- Deployed on Render: https://ai-search-visibility-agent.onrender.com
- Local test:
```bash
pip install -r langgraph_helper/requirements.txt
python langgraph_helper/fact_checker.py langgraph_helper/sample_data.json reports/zalando_report_2026-11-12.md
```

**4. Main workflow**
- Import `n8n/ai_search_visibility_agent.json` into n8n, add credentials (OpenAI, Serper, NewsAPI, Pinecone, SMTP)
- Click **Execute workflow**, fill in the form, and the report arrives by email in ~2–3 minutes

---

## Environment variables

Set these in `.env` (see `.env.example`; real keys are never committed):

| Variable | Used for |
|---|---|
| `OPEN_API_KEY` | OpenAI (tests, index script, fact-checker on Render) |
| `SERPER_API_KEY` | Serper Google search (test script) |
| `NEWS_API_KEY` | NewsAPI (test script) |
| `PINECONE_API_KEY` | Pinecone index creation (test + index scripts) |

In n8n, the same keys are stored as **n8n credentials** (OpenAI, Header Auth for Serper and NewsAPI, Pinecone, SMTP). On Render, `OPEN_API_KEY` is set as an environment variable.

---

## File map

```
├── n8n/
│   ├── ai_search_visibility_agent.json   # main workflow
│   └── rag_load_docs.json                # loads PDFs into Pinecone
├── langgraph_helper/
│   ├── fact_checker.py                   # LangGraph check → verify → fix
│   ├── server.py                         # FastAPI endpoint for n8n
│   ├── requirements.txt
│   ├── sample_data.json                  # test data
│   └── test_cases/                       # deliberately wrong report + fixed result
├── reports/                              # sample reports + report template
├── docs/                                 # workflow + email screenshots
├── rag_docs/sources.md                   # RAG document sources
├── stack_decision.md
├── gtm_future_sprints.md
├── create_index.py                       # creates the Pinecone index
├── test_keys.py                          # tests all API keys
├── requirements.txt
└── .env.example
```

---

## Limitations

- AI visibility is measured via the OpenAI API, not the ChatGPT app (no live web browsing, no personalization)
- AI mention ranks (#1, #2…) are the order among **tracked brands only**
- Brand matching is name-based (e.g. "H&M" / hm.com can be missed)
- Hidden competitors are detected from brand names in bold in the AI answers, so some may be missed
- Search results and AI answers change daily, so each report is a snapshot
- The pie chart uses QuickChart (external image service); some email apps hide images until you click "Display images"
- Render free tier sleeps when idle (handled by the wake-up step)

## Next steps

See [gtm_future_sprints.md](gtm_future_sprints.md). Planned improvements: weekly scheduled runs, results history in Google Sheets, more AI assistants (Claude, Perplexity, Gemini), report language choice (English/German).

---

## Demo
   🎥 [Watch the demo recording](https://www.loom.com/share/9eb2b0b047a647e69a766991eb19f6fa)

---

## Presentation

📊 [Project 3 slides (PDF)](https://docs.google.com/presentation/d/1p4rRECPS00pic_pMXKWv_8_ZZ7LwkRo2/edit?usp=sharing&ouid=108020012516012995498&rtpof=true&sd=true)

---

Built by **Barsha Mishra** as Project 3 of the Ironhack AI Consulting & Integration Bootcamp.