# engine/scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse

BASE_URL = "https://www.shl.com"
CATALOG_URL = BASE_URL + "/solutions/products/product-catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def get_full_url(path):
    return path if path.startswith("http") else BASE_URL + path

def scrape_assessment_detail(detail_url):
    try:
        res = requests.get(detail_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        description = soup.find("div", class_="rich-text")
        description = description.get_text(separator=" ", strip=True) if description else "N/A"

        job_level = "N/A"
        duration = "N/A"

        for h3 in soup.find_all("h3"):
            if "Job levels" in h3.text:
                job_level = h3.find_next("p").text.strip()
            if "Assessment length" in h3.text:
                p = h3.find_next("p")
                if p and "minutes" in p.text:
                    duration = p.text.split("=")[-1].strip()

        return description, job_level, duration
    except Exception as e:
        print(f"[!] Failed to parse detail page {detail_url}: {e}")
        return "N/A", "N/A", "N/A"

def scrape_section_assessments(section_title_text, output_csv):
    all_rows = []
    next_url = CATALOG_URL

    while next_url:
        print(f"🔄 Fetching: {next_url}")
        res = requests.get(next_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        # Find section
        section_heading = soup.find("th", class_="custom__table-heading__title", string=section_title_text)
        if not section_heading:
            break

        table = section_heading.find_parent("table")
        if not table:
            break

        rows = table.find_all("tr")[1:]  # Skip header
        if not rows:
            break

        for row in rows:
            try:
                a_tag = row.find("a")
                if not a_tag or not a_tag.get("href"):
                    continue

                name = a_tag.text.strip()
                detail_url = get_full_url(a_tag["href"])

                print(f"🔍 Scraping: {name}")
                description, job_level, duration = scrape_assessment_detail(detail_url)

                all_rows.append({
                    "Assessment Name": name,
                    "URL": detail_url,
                    "Description": description,
                    "Job Level": job_level,
                    "Duration": duration
                })

                time.sleep(0.5)

            except Exception as e:
                print(f"⚠️ Error processing row: {e}")

        # Move to next page
        next_btn = soup.find("a", class_="pagination__arrow", string="Next")
        if next_btn and next_btn.get("href"):
            next_url = get_full_url(next_btn["href"])
        else:
            break

    if all_rows:
        df = pd.DataFrame(all_rows)
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved {len(df)} records to {output_csv}")
    else:
        print(f"⚠️ No data found for section: {section_title_text}")


def scrape_all_assessments():
    scrape_section_assessments("Pre-packaged Job Solutions", "data/prepackaged_assessments.csv")
    scrape_section_assessments("Individual Test Solutions", "data/individual_assessments.csv")
