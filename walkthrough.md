# VIBRA Implementation Walkthrough

## Overview
We have successfully built the core infrastructure for **VIBRA**, a serverless trend visualization website. The system is designed to run entirely on GitHub Actions and GitHub Pages.

## Components Implemented

### 1. Backend Data Pipeline (`src/`)
- **`scraper.py`**: Fetches trend data. *Note: Currently uses a mock selector. Needs adjustment for the actual Yahoo! Realtime Search HTML structure.*
- **`analyzer.py`**: Uses `janome` to extract co-occurring nouns from post texts.
- **`enricher.py`**: Calculates scores, heat levels, and generates affiliate links.
- **`main.py`**: Orchestrates the pipeline and saves `cache/latest_trends.json`.

### 2. Automation (`.github/workflows/`)
- **`fetcher.yml`**: Scheduled every 15 minutes to run the pipeline and update the `cache-branch`.
- **`deploy.yml`**: Scheduled hourly to build the static site from the cache and deploy to GitHub Pages.

### 3. Frontend (`templates/`, `static/`)
- **`layout.html`**: Jinja2 template with a minimalist, typography-driven design ("Buzz Meter").
- **`style.css`**: Responsive CSS with pulse animations and dynamic tag cloud styling.
- **`generate_site.py`**: Renders the HTML using the JSON data.

### 4. Dynamic Scoring (`src/enricher.py`)
- **Velocity Calculation**: Implemented logic to calculate score based on Rank (40%), Post Volume (30%), and Velocity (30%).
- **State Persistence**: Added caching to `fetcher.yml` to persist scores between runs, enabling velocity calculation.

## Verification Results

### Local Dry Run
We executed the pipeline locally:
1.  **Dependencies**: Installed successfully via `requirements.txt`.
2.  **Pipeline Execution**: `python src/main.py` ran without crashing.
    - *Result*: `Found 0 trends`. This confirms the script runs, but the scraper selectors need to be matched to the live website's DOM.
    - *Cache Verification*: `cache/scores_to_cache.json` was successfully generated (empty due to 0 trends, but file exists).
3.  **Site Generation**: `python src/generate_site.py` successfully created `dist/index.html`.

### Next Steps
1.  **Adjust Scraper**: Inspect `https://search.yahoo.co.jp/realtime/search/matome` and update the CSS selectors in `src/scraper.py`.
2.  **Configure Secrets**: Add `GA4_TRACKING_ID` and `MERCARI_AFFILIATE_ID` to GitHub Repository Secrets.
3.  **Push to GitHub**: Push the code to the `main` branch to trigger the initial deployment.
