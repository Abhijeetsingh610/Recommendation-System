# app/web_ui.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from engine.recommender import get_top_recommendations

st.set_page_config(page_title="SHL Assessment Recommender", layout="centered")

st.title("🔍 SHL Assessment Recommendation System")
st.markdown("""
Type in a job description, query, or skill set, and get personalized SHL assessments recommended by AI.
""")

query = st.text_area("📝 Paste your query or JD here", height=200)

if st.button("🚀 Recommend Assessments"):
    if not query.strip():
        st.warning("Please enter a valid query.")
    else:
        with st.spinner("Analyzing and retrieving best assessments..."):
            results = get_top_recommendations(query)
            st.success(f"Top {len(results)} assessments recommended:")

            def make_clickable(url, name):
                return f"[{name}]({url})"

            results["Assessment Name"] = results.apply(
                lambda row: make_clickable(row["URL"], row["Assessment Name"]),
                axis=1
            )
            results = results.drop(columns=["URL", "score"])
            st.markdown(results.to_markdown(index=False), unsafe_allow_html=True)
