import os, time
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from .fetch_news import extract_article

class QAPipeline:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError('Missing GROQ_API_KEY.')
        self.client = Groq(api_key=api_key)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.db = chromadb.Client()
        self.collection = self.db.create_collection(f'news_{int(time.time())}')
        self.urls = []

    def build_embeddings(self, urls):
        self.urls = urls
        texts, ids = [], []
        for i, url in enumerate(urls):
            txt = extract_article(url)
            if len(txt) > 50:
                texts.append(txt)
                ids.append(str(i))
        if not texts:
            raise ValueError('No usable articles found.')
        embs = self.embedder.encode(texts)
        chunk_size = 800
for i, url in enumerate(urls):
    txt = extract_article(url)
    if len(txt) > 100:
        for j in range(0, len(txt), chunk_size):
            chunk = txt[j:j + chunk_size]
            texts.append(chunk)
            ids.append(f"{i}-{j}")

        self.collection.add(documents=texts, embeddings=embs, ids=ids)
        return urls

    def _retrieve(self, question, k=4):
        q_emb = self.embedder.encode([question])[0]
        res = self.collection.query(query_embeddings=[q_emb], n_results=k)
        docs = res.get('documents', [[]])[0]
        ids = res.get('ids', [[]])[0]
        return docs, ids

    def answer(self, question):
        docs, ids = self._retrieve(question)
        if not docs:
            return 'No relevant info found.', []
        context = '\n---\n'.join(d[:900] for d in docs)
        prompt = f"""
You are an equity research analyst preparing an IPO insights summary for Lenskart.

Using ONLY the information below, craft a well-structured answer.
If information is missing, say “The available sources do not mention this.”

### Response Structure:
1. **Summary Insight (2–3 sentences)** — Concise answer to the question.
2. **Supporting Facts** — Key data points, numbers, or quotes from context.
3. **Analytical Commentary** — What this means for investors or market trends.

Question: {question}
Context:
{context}
"""
