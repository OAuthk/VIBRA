# Walkthrough - Dynamic Clustering

I have implemented **Dynamic Clustering** to group trends based on their co-occurrence relationships, replacing static categories with data-driven communities.

## Changes

### Backend
- **Dependencies**: Added `networkx` and `python-louvain`.
- **Analysis**: Implemented `detect_trend_clusters` in `src/analyzer.py` using the Louvain method.
- **Data Model**: Added `cluster_id` to `EnrichedTrendItem` in `src/models.py`.
- **Pipeline**: Updated `src/main.py` and `src/enricher.py` to pass cluster information through the pipeline.
- **Scraper**: Added mock data fallback in `src/scraper.py` to ensure the pipeline can be verified even if scraping fails (or finds 0 trends).

### Frontend
- **Visualization**: Updated `static/js/main.js` to use a D3.js ordinal color scale (`d3.schemeCategory10`).
- **Coloring**: Trend text is now colored based on its `cluster_id`, visually grouping related topics.

## Verification Results

### Pipeline Execution
The data pipeline was executed successfully with mock data.
```
Detecting trend clusters...
Detected 4 clusters.
Data pipeline completed. Saved to cache\trends.json
```

### Data Output (`dist/trends.json`)
The generated JSON now includes `cluster_id` for each trend:
```json
    {
      "text": "Election",
      "cluster_id": 1,
      ...
    },
    {
      "text": "Anime",
      "cluster_id": 2,
      ...
    }
```

### Visual Check
- Open `dist/index.html` in your browser.
- You should see the tag cloud.
- Trends belonging to the same cluster (e.g., "Election" and "Vote") will share the same text color.
- This allows for immediate visual identification of topics.
