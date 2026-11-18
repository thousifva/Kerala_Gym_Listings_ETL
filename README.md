# Kerala Gym Listings ETL

A training project that builds a deduplicated dataset of gym business listings across 8 Kerala cities from public Google Maps data, using Python and the SerpAPI Maps endpoint.

## What it does

- **Business question:** map the gym market across Kochi, Kozhikode, Thrissur, Malappuram, Trivandrum, Kannur, Kollam and Ernakulam, capturing name, phone, email, location and website for each operator.
- **Data and method:** pulls Google Maps listings through the SerpAPI Maps endpoint, paginating up to 5 pages per city (40 requests maximum); removes cross-city duplicates on place ID (Kochi and Ernakulam overlap heavily); visits each gym's website and contact pages to extract an email address with requests, BeautifulSoup and regex.
- **Output:** an Excel dataset of unique gyms with six fields each (city, name, phone, email, location, website), plus printed data-quality counts (how many listings have a website and a recoverable email).

## Privacy note

The scraped contact dataset (phone numbers, emails, addresses of real businesses) is private and is not part of this repository. The `.gitignore` excludes the `data/` folder and Excel/CSV exports so they are left out of commits by default; check before committing anything new.

## Repository contents

| File | Purpose |
| --- | --- |
| `gym_pipeline.py` | Full pipeline: collect listings, deduplicate, find emails, export Excel |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Keeps the scraped dataset and exports out of commits by default |

## Setup

1. Install Python 3.9+ and the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Get a SerpAPI key at https://serpapi.com/manage-api-key. SerpAPI's free plan is 250 searches/month (checked November 2026); this pipeline uses at most 40 searches per run.

3. Set the key as an environment variable:

   ```
   # Linux/macOS
   export SERPAPI_KEY="your-key-here"

   # Windows (PowerShell)
   $env:SERPAPI_KEY="your-key-here"
   ```

## Run

```
python gym_pipeline.py
```

The email pass visits each gym's website one by one, so allow time for a full run. The Excel file is written to `data/kerala_gyms.xlsx` (not committed).

## Notes and provenance

- Reconstructed from the training conversation in which this project was built. The only change made for publication: the API key, which was typed into the code during the session, now comes from the `SERPAPI_KEY` environment variable, and the script prints its progress instead of using notebook-only helpers. The published code has been syntax-checked but not run end-to-end since reconstruction.
- Google Maps listings do not include email addresses; the email pass finds one only when a gym's own website publishes it, so many rows will have no email. That is expected.
- SerpAPI's terms and the target websites' terms apply to any use of this code.
