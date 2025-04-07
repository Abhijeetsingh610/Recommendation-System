# SHL Assessment Recommendation System - Main Entry Point


import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.scraper import scrape_all_assessments
from engine.embedder import build_embeddings


# Entry point for CLI setup
def setup():
    #print("[1] Scraping SHL assessments...")
    #scrape_all_assessments()

    print("[2] Building embeddings for Pre-packaged Job Solutions...")
    if os.path.exists("data/prepackaged_assessments.csv"):
        build_embeddings("data/prepackaged_assessments.csv", output_path="data/prepackaged_embeddings.json")

    print("[2] Building embeddings for Individual Test Solutions...")
    if os.path.exists("data/individual_assessments.csv"):
        build_embeddings("data/individual_assessments.csv", output_path="data/individual_embeddings.json")

    print("✅ Setup complete. You can now run the UI or API server.")

if __name__ == "__main__":
    setup()
