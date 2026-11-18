"""
Kerala Gym Listings ETL

Collects gym business listings across 8 Kerala cities from Google Maps
via the SerpAPI Maps endpoint, de-duplicates them, tries to find an email
address on each gym's website, and exports an Excel file.

Set your SerpAPI key in the SERPAPI_KEY environment variable before running.
"""

import os
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

API_KEY = os.environ.get("SERPAPI_KEY")
if not API_KEY:
    raise SystemExit(
        "SERPAPI_KEY environment variable is not set. "
        "Get a key at https://serpapi.com/manage-api-key and set it first."
    )

CITIES = {
    "Kochi":      "@9.9312,76.2673,13z",
    "Kozhikode":  "@11.2588,75.7804,13z",
    "Thrissur":   "@10.5276,76.2144,13z",
    "Malappuram": "@11.0510,76.0711,13z",
    "Trivandrum": "@8.5241,76.9366,13z",
    "Kannur":     "@11.8745,75.3704,13z",
    "Kollam":     "@8.8932,76.6141,13z",
    "Ernakulam":  "@9.9816,76.2999,13z",
}
MAX_PAGES = 5  # 5 pages x 20 results = up to 100 gyms per city


def search(q, ll, start=0):
    r = requests.get(
        "https://serpapi.com/search.json",
        params={
            "engine": "google_maps",
            "type": "search",
            "q": q,
            "ll": ll,        # "@lat,lng,zoom"
            "start": start,  # 0, 20, 40...
            "hl": "en",
            "api_key": API_KEY,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def collect():
    rows = []
    for city, ll in CITIES.items():
        for page in range(MAX_PAGES):
            try:
                data = search(f"gyms in {city}", ll, start=page * 20)
            except Exception as e:
                print(f"{city} page {page + 1}: {e}")
                break
            res = data.get("local_results", [])
            if not res:
                break
            for p in res:
                rows.append({
                    "City": city,
                    "Gym Name": p.get("title"),
                    "Contact No.": p.get("phone"),
                    "Location": p.get("address"),
                    "Website URL": p.get("website"),
                    "Rating": p.get("rating"),
                    "place_id": p.get("place_id"),
                })
            print(f"{city} page {page + 1}: {len(res)} results")
            time.sleep(1)
    return pd.DataFrame(rows)


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SKIP = ("facebook.com", "instagram.com", "wa.me", "linktr.ee", "youtube.com")
BAD_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")


def find_email(url):
    if not url or any(s in url for s in SKIP):
        return None
    for path in ["", "/contact", "/contact-us"]:
        try:
            r = requests.get(
                url.rstrip("/") + path, timeout=10,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if r.status_code != 200:
                continue
            found = [e for e in EMAIL_RE.findall(r.text)
                     if not e.lower().endswith(BAD_EXT)]
            if found:
                return found[0]
        except Exception:
            continue
    return None


def main():
    df = collect()
    print(len(df), "rows before cleaning")

    # Kochi and Ernakulam overlap heavily, so the same gym appears twice.
    df = df.drop_duplicates(subset="place_id").reset_index(drop=True)
    print(len(df), "unique gyms")
    print(df["Website URL"].notna().sum(), "have a website")

    df["Email ID"] = None
    for i, row in df.iterrows():
        df.at[i, "Email ID"] = find_email(row["Website URL"])
        if i % 25 == 0:
            print(f"{i}/{len(df)} done")
    print(df["Email ID"].notna().sum(), "emails found")

    os.makedirs("data", exist_ok=True)
    final = df[["City", "Gym Name", "Contact No.", "Email ID",
                "Location", "Website URL"]]
    out = os.path.join("data", "kerala_gyms.xlsx")
    final.to_excel(out, index=False)
    print("Wrote", out)


if __name__ == "__main__":
    main()
