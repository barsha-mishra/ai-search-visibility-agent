import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

# 1. OpenAI
try:
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    reply = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in 3 words"}],
    )
    print("✅ OpenAI:", reply.choices[0].message.content)
except Exception as e:
    print("❌ OpenAI failed:", e)

# 2. Serper (Google search)
try:
    r = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
        json={"q": "best pet insurance germany"},
    )
    r.raise_for_status()
    print("✅ Serper: top result ->", r.json()["organic"][0]["title"])
except Exception as e:
    print("❌ Serper failed:", e)

# 3. NewsAPI
try:
    r = requests.get(
        "https://newsapi.org/v2/everything",
        params={"q": "idealo", "pageSize": 1, "apiKey": os.getenv("NEWS_API_KEY")},
    )
    r.raise_for_status()
    print("✅ NewsAPI: articles found ->", r.json()["totalResults"])
except Exception as e:
    print("❌ NewsAPI failed:", e)

# 4. Pinecone
try:
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    print("✅ Pinecone: indexes ->", pc.list_indexes().names())
except Exception as e:
    print("❌ Pinecone failed:", e)