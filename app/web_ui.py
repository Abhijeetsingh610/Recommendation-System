# app/web_ui.py

import streamlit as st
import requests
import pandas as pd

# 🔗 Your FastAPI endpoint
API_URL = "https://fastapi-qbrg.onrender.com"

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
                response = requests.post(f"{API_URL}/recommend", json={"query": query, "top_k": top_k})
                response_data = response.json()

                # Check if response is a list (expected result), or dict (probably error)
                if isinstance(response_data, list):
                    results = pd.DataFrame(response_data)

                    st.success(f"Top {len(results)} assessments recommended:")

                    # Make assessment names clickable
                    def make_clickable(url, name):
                        return f"[{name}]({url})"

                    results["Assessment Name"] = results.apply(
                        lambda row: make_clickable(row["URL"], row["Assessment Name"]),
                        axis=1
                    )
                    # Reorder and filter the exact columns to show
                    display_cols = [
                        "Assessment Name",
                        "Source",
                        "Job Level",
                        "Duration",
                        "Test Type",
                        "Remote Testing Support",
                        "Adaptive/IRT Support"
                    ]
                    
                    # Ensure those columns exist before slicing
                    available_cols = [col for col in display_cols if col in results.columns]
                    results = results[available_cols]
                    
                    st.markdown(results.to_markdown(index=False), unsafe_allow_html=True)


                else:
                    st.error(f"❌ API Error: {response_data.get('error', 'Unexpected response')}")

            except Exception as e:
                st.error(f"⚠️ Failed to connect to API: {e}")

