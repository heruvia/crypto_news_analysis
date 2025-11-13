import requests
from openai import OpenAI
from datetime import datetime
from enum import Enum
from typing import Optional
import streamlit as st
from dotenv import load_dotenv
import os

# ===============================
# ENUMS
# ===============================
class Language(Enum):
    EN = "en"
    ZH = "zh"

# ===============================
# MODEL PARAMETER
# ===============================
class NewsQuery:
    def __init__(
        self,
        language: Optional[Language] = Language.EN,
        limit: Optional[int] = 5,
        page: Optional[int] = 1
    ):
        self.language = language
        self.limit = limit
        self.page = page


# ===============================
# CONFIGURATION
# ===============================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not OPENAI_API_KEY or not NEWS_API_KEY:
    st.error("⚠️ API keys are missing. Please add them to Streamlit Secrets or a local .env file.")
    st.stop()

NEWS_API_URL = "https://cryptonewsapi.online/api/v1/news"

client = OpenAI(api_key=OPENAI_API_KEY)

# ===============================
# FETCH NEWS FUNCTION
# ===============================
def fetch_crypto_news(query: NewsQuery):
    headers = {"X-API-Key": NEWS_API_KEY}
    params = {
        "items": query.limit,
        "page": query.page,
        "language": query.language.value if query.language else None
    }

    try:
        response = requests.get(NEWS_API_URL, headers=headers, params=params)
        data = response.json()
    except Exception as e:
        st.error(f"❌ Error fetching news: {e}")
        return get_mock_articles()

    articles = []
    if isinstance(data, dict):
        articles = (
            data.get("data", {}).get("articles", [])
            if isinstance(data.get("data"), dict)
            else []
        )

    if not articles or not isinstance(articles, list):
        st.warning("No articles found, using mock data instead.")
        return get_mock_articles()

    return articles[:query.limit]

# ===============================
# MOCK ARTICLE FUNCTION
# ===============================
def get_mock_articles():
    return [
        {
            "title": "Bitcoin Reaches New High",
            "description": "Bitcoin price surged 5% today as market sentiment turns bullish...",
            "pubDate": "2025-11-13T12:00:00.000Z",
            "source": {"name": "CryptoNews"},
            "link": "https://example.com/bitcoin"
        },
        {
            "title": "Ethereum Merge Update",
            "description": "Ethereum upgrade drives adoption and network efficiency...",
            "pubDate": "2025-11-12T09:30:00.000Z",
            "source": {"name": "CoinTelegraph"},
            "link": "https://example.com/ethereum"
        }
    ]

# ===============================
# ANALYZE NEWS FUNCTION (Prompt tetap Bahasa Indonesia)
# ===============================
def analyze_market(articles):
    combined_text = ""
    for art in articles:
        combined_text += f"{art.get('title','')}\n{art.get('description','')}\n\n"

    prompt = f"""
    Berdasarkan berita crypto terbaru berikut, berikan analisis singkat untuk market crypto:
    - Sentimen pasar (Bullish / Bearish / Netral)
    - Tren umum (naik / turun / stabil)
    - Saran singkat (Buy / Hold / Watch)
    Jawab dengan jelas, mudah dipahami, dan tampilkan dengan format yang rapi dan profesional.

    Berita:
    {combined_text}
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# ===============================
# STREAMLIT UI
# ===============================
st.set_page_config(page_title="Crypto Market Insight", page_icon="💹", layout="wide")

# ========== STYLE ==========
st.markdown(
    """
    <style>
        body {
            background: linear-gradient(160deg, #0f0f0f 0%, #1a1a1a 40%, #0b0b0b 100%);
            color: #e5e5e5;
            font-family: 'Inter', sans-serif;
        }

        .main {
            background: transparent;
        }

        h1, h2, h3 {
            color: #f2f2f2;
        }

        .header-section {
            text-align: center;
            background: linear-gradient(135deg, #1b1f1b 0%, #0f1410 50%, #1a2a1a 100%);
            color: #e8f5e9;
            padding: 2.5rem 2rem 3rem 2rem;
            border-radius: 18px;
            box-shadow: 0 6px 25px rgba(0,0,0,0.5);
            margin-bottom: 2.5rem;
        }

        .header-title {
            font-size: 2.3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            color: #d1fae5;
        }

        .header-subtitle {
            font-size: 1.1rem;
            opacity: 0.85;
            color: #a7f3d0;
            margin-bottom: 1.5rem;
        }

        .stButton>button {
            background-color: #16a34a;
            color: white;
            border-radius: 10px;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1.2rem;
        }

        .stButton>button:hover {
            background-color: #22c55e;
            transform: scale(1.03);
        }

        .news-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            background: #141414;
            box-shadow: 0 3px 8px rgba(0,0,0,0.3);
            transition: transform 0.25s ease, box-shadow 0.3s ease;
        }

        .news-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.4);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# HEADER + FILTER
# ===============================
st.markdown(
    """
    <div class="header-section">
        <div class="header-title">💹 Crypto Market Insight</div>
        <div class="header-subtitle">Latest crypto news and AI-powered market analysis</div>
    </div>
    """,
    unsafe_allow_html=True
)

col_empty1, col_center, col_empty2 = st.columns([1, 3, 1])
with col_center:
    col1, col2 = st.columns([2, 1])
    with col1:
        lang = st.selectbox("News Language", ["English", "Chinese"], key="lang_select")
    with col2:
        limit = st.text_input("Number of News Articles", "5", key="limit_input")

try:
    limit = int(limit)
    if limit < 1:
        limit = 5
except ValueError:
    limit = 5

query = NewsQuery(limit=limit, language=Language.EN if lang == "English" else Language.ZH)

st.markdown("<hr>", unsafe_allow_html=True)

# ===============================
# FETCH NEWS & DISPLAY
# ===============================
articles = fetch_crypto_news(query)

if articles:
    top = articles[0]
    pub_date = top.get("pubDate", "")
    if pub_date:
        try:
            pub_date = datetime.strptime(pub_date[:19], "%Y-%m-%dT%H:%M:%S").strftime("%d %b %Y, %H:%M")
        except:
            pass

    st.markdown(f"""
        <div class="highlight-card">
            <div class="highlight-meta">🕓 {pub_date} | 📰 {top.get('source', {}).get('name', 'Unknown')}</div>
            <div class="highlight-title">{top.get('title', 'No Title')}</div>
            <div class="highlight-desc">{top.get('description', '')}</div>
            <div class="highlight-link">
                <a href="{top.get('link', '#')}" target="_blank">🔗 Read More</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("🗞️ More News")

    for art in articles[1:]:
        title = art.get("title", "No Title")
        desc = art.get("description", "")
        link = art.get("link", "#")
        pub_date = art.get("pubDate", "")
        source = art.get("source", {}).get("name", "Unknown Source")

        if pub_date:
            try:
                pub_date = datetime.strptime(pub_date[:19], "%Y-%m-%dT%H:%M:%S").strftime("%d %b %Y, %H:%M")
            except:
                pass

        st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{title}</div>
                <div class="news-date">🕓 {pub_date} | 📰 {source}</div>
                <div class="news-desc">{desc}</div>
                <div class="news-link"><a href="{link}" target="_blank">🔗 Read Article</a></div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ===============================
    # ANALYSIS OUTPUT
    # ===============================
    st.subheader("📊 Market Analysis Summary")
    with st.spinner("Analyzing news..."):
        summary = analyze_market(articles)
        st.success(summary)
else:
    st.error("No news available at the moment.")
