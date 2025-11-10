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
            if len(txt) > 200:
                texts.append(txt)
                ids.append(str(i))
        if not texts:
            raise ValueError('No usable articles found.')
        embs = self.embedder.encode(texts)
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
You are a financial analyst preparing an IPO insight report.
Use only the information in the provided context. 
If the context doesn’t contain an answer, say “The available sources do not specify this detail.”

Format your response in 3 parts:
1️⃣ Short summary (2–3 lines)
2️⃣ Key figures or facts (if mentioned)
3️⃣ Analytical takeaway (why it matters for investors)

Question: {question}
Context:
{context}
"""

