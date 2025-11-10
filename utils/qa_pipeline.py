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

    def _retrieve(self, question, k=8):
        q_emb = self.embedder.encode([question])[0]
        res = self.collection.query(query_embeddings=[q_emb], n_results=k)
        docs = res.get('documents', [[]])[0]
        ids = res.get('ids', [[]])[0]
        return docs, ids

   def answer(self, question):
    docs, ids = self._retrieve(question)
    if not docs:
        return "No relevant info found.", []

    # Combine top docs into one context
    context = "\n---\n".join(d[:1000] for d in docs)

    # ✅ Optional step: Summarize context first (makes answers sharper)
    context_summary_prompt = f"Summarize these texts briefly, capturing all factual details:\n{context}"

    try:
        summary_resp = self.client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[{'role': 'user', 'content': context_summary_prompt}],
            temperature=0.1
        )
        context_summary = summary_resp.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ Summarization failed, fallback to raw context:", e)
        context_summary = context

    # ✅ Now build a structured final prompt
    prompt = f"""
You are a financial analyst preparing an IPO insights report for Lenskart.

Use only the context below and the summary to answer.
If the answer is missing, say: "The available sources do not mention this."

### Response Format:
1️⃣ Short summary (2–3 lines)
2️⃣ Supporting facts (numbers, data, or quotes)
3️⃣ Analytical takeaway (why it matters for investors)

Question: {question}

Context Summary:
{context_summary}
"""

    # Generate answer
    resp = self.client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.2
    )
    answer = resp.choices[0].message.content.strip()

    used = [self.urls[int(i.split('-')[0])] for i in ids if int(i.split('-')[0]) < len(self.urls)]
    return answer, used

