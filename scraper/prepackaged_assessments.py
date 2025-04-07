import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

# 🔗 Base settings
BASE_URL = "https://www.shl.com"
CATALOG_URL = BASE_URL + "/solutions/products/product-catalog/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_full_url(path):
    return path if path.startswith("http") else urljoin(BASE_URL, path)

def scrape_prepackaged():
    print("🔍 Scraping: Pre-packaged Job Solutions")
    next_url = CATALOG_URL
    links = []

    while next_url:
        print(f"🌐 Visiting: {next_url}")
        res = requests.get(next_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        section = soup.find("th", class_="custom__table-heading__title", string="Pre-packaged Job Solutions")
        if not section:
            break

        table = section.find_parent("table")
        rows = table.find_all("tr")[1:]  # Skip header row

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:  # We now expect only up to the Adaptive column
                continue

            a_tag = cols[0].find("a")
            name = a_tag.text.strip() if a_tag else "N/A"
            url = get_full_url(a_tag["href"]) if a_tag else "N/A"

            # ✅ New logic using span class "-yes"
            remote_td = cols[1]
            adaptive_td = cols[2]

            remote = "Yes" if remote_td.find("span", class_="-yes") else "No"
            adaptive = "Yes" if adaptive_td.find("span", class_="-yes") else "No"

            links.append({
                "Assessment Name": name,
                "Remote Testing": remote,
                "Adaptive/IRT": adaptive,
                "URL": url
            })

        next_btn = soup.find("a", class_="pagination__arrow", string="Next")
        next_url = get_full_url(next_btn["href"]) if next_btn and next_btn.get("href") else None
        time.sleep(1)

    df = pd.DataFrame(links)
    df.to_csv("prepackaged_assessments.csv", index=False)
    print(f"✅ Saved {len(df)} assessments to prepackaged_assessments.csv")

# 🚀 Run only for Pre-packaged
scrape_prepackaged()



#Then extracted the description of the first assessment from the CSV file and printed it out.


# 📦 Install dependencies
!pip install beautifulsoup4 requests

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from google.colab import files  # Only needed for Colab

# 📂 Load the CSV file
df = pd.read_csv("prepackaged_assessments.csv")
print(f"✅ Loaded {len(df)} assessment links")

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

        # ✅ NEW: Extract Test Type from custom <p> structure
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

# 🚀 Scrape details for all URLs
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

# 💾 Save updated CSV
output_file = "prepackaged_assessments_detailed.csv"
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
print(f"✅ Saved with details: {output_file}")

# 📥 Download (for Colab)
files.download(output_file)
