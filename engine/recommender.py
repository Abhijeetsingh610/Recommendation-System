import json
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_embedding_file(path, source_label):
    with open(path, "r") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    df["embedding"] = df["embedding"].apply(np.array)
    df["Source"] = source_label

    # ✅ Rename columns to match UI display expectations
    df.rename(columns={
        "Assessment Length": "Duration",
        "Remote Testing": "Remote Testing Support",
        "Adaptive/IRT": "Adaptive/IRT Support"
    }, inplace=True)

    # ✅ Ensure all required columns exist
    required_cols = [
        "Assessment Name", "Duration", "Test Type", "Job Level",
        "Remote Testing Support", "Adaptive/IRT Support", "URL"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = "N/A"

    return df



def load_combined_data():
    prepackaged = load_embedding_file("data/prepackaged_embeddings.json", "Prepackaged")
    individual = load_embedding_file("data/individual_embeddings.json", "Individual")
    return pd.concat([prepackaged, individual], ignore_index=True)

def get_query_embedding(query: str):
    return model.encode(query)

def get_top_recommendations(query: str, k: int = 10):
    df = load_combined_data()
    query_vec = get_query_embedding(query)

    embeddings = np.stack(df["embedding"].values)
    sims = cosine_similarity([query_vec], embeddings)[0]

    df["score"] = sims
    df_sorted = df.sort_values("score", ascending=False).head(k)

    columns = [
        "Assessment Name",
        "Source",
        "URL",
        "Job Level",
        "Duration",
        "Test Type",
        "Remote Testing Support",
        "Adaptive/IRT Support",
        "score"
    ]

    return df_sorted[columns].reset_index(drop=True)
