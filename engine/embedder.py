# engine/embedder.py

from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import json
import os

def load_model(model_name="all-MiniLM-L6-v2"):
    return SentenceTransformer(model_name)

def build_embeddings(csv_path, output_path="data/embeddings.json"):
    df = pd.read_csv(csv_path)

    def combine_text(row):
        return f"{row['Assessment Name']}. {row.get('Description', '')}. Job Level: {row.get('Job Level', '')}. Time: {row.get('Assessment Length', '')}"

    texts = df.apply(combine_text, axis=1).fillna("No content").tolist()

    print(f"[●] Loading model and generating embeddings for {len(texts)} assessments...")
    model = load_model()
    embeddings = model.encode(texts, show_progress_bar=True)

    df["embedding"] = [embedding.tolist() for embedding in embeddings]
    df.to_json(output_path, orient="records", indent=2)
    print(f"[✔] Saved embeddings to {output_path}")
