import streamlit as st
from streamlit_searchbox import st_searchbox
import wikipedia
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

try:
    import google.generativeai as genai
    import json

    with open("gemini_key.json") as f:
        key = json.load(f)["api_key"]
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        GEMINI_ENABLED = True
except:
    GEMINI_ENABLED = False


def search_wikipedia(query: str):
    return wikipedia.search(query)


def fetch_summary_and_url(topic):
    try:
        summary = wikipedia.summary(topic, sentences=5, auto_suggest=False)
        page = wikipedia.page(topic, auto_suggest=False)
        return summary, page.url
    except Exception as e:
        return None, None


def fetch_images(topic):
    try:
        page = wikipedia.page(topic, auto_suggest=False)
        images = [img for img in page.images if img.lower().endswith(('jpg', 'jpeg', 'png'))]
        return images[:6]
    except:
        return []


def fetch_tables(topic):
    try:
        page = wikipedia.page(topic, auto_suggest=False)
        html = requests.get(page.url).text
        soup = BeautifulSoup(html, 'html.parser')
        tables = pd.read_html(str(soup))
        return tables[:2] if tables else []
    except Exception as e:
        return []


st.set_page_config(page_title="Wikipedia Scrapper Search", layout="wide")
st.markdown("""
    <style>
        .stApp {
            background-color: #f8fafc;
            color: #1c1e21;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3 {
            color: #0a2540;
        }
        .stButton>button {
            background-color: #0a2540;
            color: white;
            border-radius: 5px;
            padding: 0.5em 1em;
        }
    </style>
""", unsafe_allow_html=True)


st.title("📘 Wikipedia Semantic Scraper")

selected_topic = st_searchbox(search_wikipedia, key="wiki_search")

if selected_topic:
    st.subheader(f"🔍 {selected_topic}")
    
    with st.spinner("Fetching summary and data..."):
        summary, url = fetch_summary_and_url(selected_topic)
        if not summary:
            st.error("Could not extract information. Try a different topic.")
        else:
            st.markdown(f"<p style='font-size: 17px; line-height: 1.6;'>{summary}</p>", unsafe_allow_html=True)
            if url:
                st.markdown(f"[📖 View full article on Wikipedia]({url})")

            # Images
            st.subheader("🖼️ Related Media")
            images = fetch_images(selected_topic)
            if images:
                cols = st.columns(3)
                for idx, img_url in enumerate(images):
                    with cols[idx % 3]:
                        st.image(img_url, use_column_width=True)
            else:
                st.info("No relevant images found.")

            # Tables
            st.subheader("📊 Data Tables")
            tables = fetch_tables(selected_topic)
            if tables:
                for i, table in enumerate(tables):
                    try:
                        st.markdown(f"**Table {i+1}:**")
                        st.dataframe(table)
                    except Exception as e:
                        st.warning(f"⚠️ Skipped Table {i+1} due to a rendering issue.")
            else:
                st.info("No tables found.")

            # Gemini AI Insight
            if GEMINI_ENABLED:
                st.markdown("---")
                st.subheader("🤖 AI-Generated Insight")

                with st.spinner("Thinking..."):
                    try:
                        prompt = f"""Give a brief but insightful explanation, fun fact, or real-world application related to the topic "{selected_topic}".
                        Keep it concise and helpful. Avoid repeating the Wikipedia summary."""
                        response = model.generate_content(prompt)
                        insight = response.text.strip()
                        st.markdown(f"<p style='font-size: 16px; color: #333; line-height: 1.6;'>{insight}</p>", unsafe_allow_html=True)
                    except:
                        st.info("AI failed to generate insight.")
