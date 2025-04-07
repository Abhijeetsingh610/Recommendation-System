# 📦 Install dependencies
!pip install beautifulsoup4 requests

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin, urlparse, parse_qs

BASE_URL = "https://www.shl.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_full_url(path):
    return path if path.startswith("http") else urljoin(BASE_URL, path)

def scrape_individual():
    print("🔍 Scraping: Individual Test Solutions")
    start_index = 0
    records = []

    while True:
        page_url = f"https://www.shl.com/solutions/products/product-catalog/?start={start_index}&type=1&type=1"
        print(f"🌐 Visiting: {page_url}")
        res = requests.get(page_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        section = soup.find("th", class_="custom__table-heading__title", string="Individual Test Solutions")
        if not section:
            print("⚠️ Individual Test Solutions section not found, stopping.")
            break

        table = section.find_parent("table")
        if not table:
            print("⚠️ Table not found, stopping.")
            break

        rows = table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            a_tag = cols[0].find("a")
            name = a_tag.text.strip() if a_tag else "N/A"
            url = get_full_url(a_tag["href"]) if a_tag else "N/A"

            remote = "Yes" if cols[1].find("span", class_="-yes") else "No"
            adaptive = "Yes" if cols[2].find("span", class_="-yes") else "No"

            records.append({
                "Assessment Name": name,
                "Remote Testing": remote,
                "Adaptive/IRT": adaptive,
                "URL": url
            })

        next_btn = soup.find("a", class_="pagination__arrow", string="Next")
        if next_btn and next_btn.get("href"):
            next_url = get_full_url(next_btn["href"])
            parsed = urlparse(next_url)
            qs = parse_qs(parsed.query)
            start_index = int(qs.get("start", [0])[0])
            time.sleep(1)
        else:
            break

    df = pd.DataFrame(records)
    df.to_csv("individual_assessments.csv", index=False)
    print(f"✅ Saved {len(df)} records to individual_assessments.csv")

# 🚀 Run the scraper
scrape_individual()


# THen the second step is to scrape the details of each assessment


# 📦 Install dependencies
!pip install beautifulsoup4 requests

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from google.colab import files  # Only for Colab download

# 📂 Load the CSV file
df = pd.read_csv("individual_assessments.csv")
print(f"✅ Loaded {len(df)} individual assessments")

# ⛏️ Extract detail page info
def extract_details(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        def get_text(header_name):
            tag = soup.find("h4", string=header_name)
            if tag:
                p = tag.find_next_sibling("p")
                return p.get_text(strip=True) if p else "N/A"
            return "N/A"

        description = get_text("Description")
        job_level = get_text("Job levels")
        duration = get_text("Assessment length")

        # ✅ Extract Test Type using spans in the special <p> block
        test_type_codes = []
        test_type_block = soup.find("p", class_="d-flex align-items-center me-5 || product-catalogue__small-text")
        if test_type_block and "Test Type" in test_type_block.text:
            type_spans = test_type_block.find_all("span", class_="product-catalogue__key")
            test_type_codes = [span.text.strip() for span in type_spans]

        test_type = ", ".join(test_type_codes) if test_type_codes else "N/A"

        return description, job_level, duration, test_type
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return "N/A", "N/A", "N/A", "N/A"

# 🚀 Scrape details for all assessments
descriptions = []
job_levels = []
durations = []
test_types = []

for i, row in df.iterrows():
    print(f"🔍 {i+1}/{len(df)}: {row['Assessment Name']}")
    desc, job, time_needed, ttype = extract_details(row['URL'])
    descriptions.append(desc)
    job_levels.append(job)
    durations.append(time_needed)
    test_types.append(ttype)
    time.sleep(0.5)

# 🧾 Append new columns
df["Description"] = descriptions
df["Job Level"] = job_levels
df["Assessment Length"] = durations
df["Test Type"] = test_types

# 💾 Save updated file
output_file = "individual_assessments_detailed.csv"
df.to_csv(output_file, index=False, columns=[
    "Assessment Name",
    "Remote Testing",
    "Adaptive/IRT",
    "Test Type",
    "Description",
    "Job Level",
    "Assessment Length",
    "URL"
])
print(f"✅ Saved enriched file: {output_file}")

# 📥 Download (Colab only)
files.download(output_file)
