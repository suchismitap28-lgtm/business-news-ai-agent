import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

class QAPipeline:
    def __init__(self, model="llama-3.1-8b-instant"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection("business_docs")
        self.urls = []

    def add_documents(self, texts, urls):
        embeddings = self.embedder.encode(texts)
        ids = [str(i) for i in range(len(texts))]
        self.collection.add(documents=texts, embeddings=embeddings, ids=ids)
        self.urls.extend(urls)


st.set_page_config(page_title='Business News AI Analyst', page_icon='🧠', layout='wide')
st.title('🧠 Business News AI Analyst')

st.subheader("📰 Auto-Fetch Latest Business Articles")

topic = st.text_input("Enter a topic or company name (e.g. Lenskart IPO):")
if st.button("Fetch Articles"):
    if not topic.strip():
        st.warning("Please enter a topic name.")
    else:
        with st.spinner("Fetching latest news..."):
            articles = fetch_latest_articles(topic, max_results=5)
            if not articles:
                st.error("No news found. Try another topic.")
            else:
                st.success(f"Fetched {len(articles)} articles:")
                for art in articles:
                    st.markdown(f"- [{art['title']}]({art['url']}) — {art.get('source','Unknown')}")

                # Auto-fill URLs into the next text box
                urls_text = "\n".join([a["url"] for a in articles if a["url"]])
                st.session_state["auto_urls"] = urls_text

urls_input = st.text_area("Paste News URLs (one per line):", 
                          height=150, 
                          value=st.session_state.get("auto_urls", ""))
qs_input = st.text_area('Enter Questions (one per line):', height=150)

if st.button('Generate Report'):
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    qs = [q.strip() for q in qs_input.splitlines() if q.strip()]
    if not urls or not qs:
        st.error('Please add both URLs and questions.')
    else:
        try:
            pipe = QAPipeline()
            pipe.build_embeddings(urls)
            results = []
            for q in qs:
                ans, used = pipe.answer(q)
                results.append({'Question': q, 'Answer': ans, 'Sources': ' | '.join(used)})
            df = pd.DataFrame(results)
            st.dataframe(df)
            st.download_button('📄 Download CSV', dataframe_to_csv_bytes(df), 'business_ai_report.csv', 'text/csv')
            st.download_button('📘 Download PDF', dataframe_to_pdf_bytes(df), 'business_ai_report.pdf', 'application/pdf')
        except Exception as e:
            st.error(f'Error: {e}')
