# app/web_ui.py

import streamlit as st
import requests
import pandas as pd

# 🔗 Your FastAPI endpoint
API_URL = "https://shl-assessment-api.onrender.com/recommend"

st.set_page_config(page_title="SHL Assessment Recommender", layout="centered")

st.title("🔍 SHL Assessment Recommendation System")
st.markdown("""
Type in a job description, query, or skill set, and get personalized SHL assessments recommended by AI.
""")

query = st.text_area("📝 Paste your query or JD here", height=200)
top_k = st.slider("🔢 Number of recommendations", min_value=1, max_value=20, value=10)

if st.button("🚀 Recommend Assessments"):
    if not query.strip():
        st.warning("Please enter a valid query.")
    else:
        with st.spinner("Analyzing and retrieving best assessments..."):
            try:
                response = requests.post(API_URL, json={"query": query, "top_k": top_k})
                if response.status_code == 200:
                    results = pd.DataFrame(response.json())
                    
                    st.success(f"Top {len(results)} assessments recommended:")

                    # Make assessment names clickable
                    def make_clickable(url, name):
                        return f"[{name}]({url})"

                    results["Assessment Name"] = results.apply(
                        lambda row: make_clickable(row["URL"], row["Assessment Name"]),
                        axis=1
                    )

                    # Hide columns you don't want to show
                    if "URL" in results.columns:
                        results = results.drop(columns=["URL"])
                    if "score" in results.columns:
                        results = results.drop(columns=["score"])

                    st.markdown(results.to_markdown(index=False), unsafe_allow_html=True)
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"⚠️ Failed to connect to API: {e}")
