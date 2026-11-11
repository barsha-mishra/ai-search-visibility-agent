1. n8n Form Trigger → brand, 4 competitors, 3–5 queries, country
        ↓
2. Validate input (all fields filled?)
        ↓
3. Serper: Google results per query
        ↓
4. OpenAI: ask each query, check which brands AI mentions
        ↓
5. NewsAPI: recent news per brand
        ↓
6. Combine all data into one summary
        ↓
7. Pinecone RAG: fetch matching SEO/GEO guidelines
        ↓
8. LangGraph helper (via HTTP): reason over data → gaps + recommendations
        ↓
9. OpenAI: write the report using the template
        ↓
10. Save report + send by email

Error path:
If an API fails → retry once → if it still fails, mark "data missing" in the report and continue.