import sys
import json
import os
import scraper
import analyzer
import enricher

def run_fetcher_pipeline():
    """Executes the complete data pipeline from scraping to saving cache files."""
    print("[INFO] Starting FETCHER pipeline...")
    
    # 1. Scrape
    print("Fetching trends...")
    raw_trends = scraper.fetch_trends()
    if not raw_trends:
        print("[CRITICAL] No raw trends acquired. Halting.", file=sys.stderr)
        sys.exit(1)
    
    # 2. Analyze
    print("Analyzing trends...")
    analyzed_trends = analyzer.analyze_trends(raw_trends)
    
    # 2.5 Detect Clusters (Added step to match previous logic)
    print("Detecting trend clusters...")
    cluster_mapping = analyzer.detect_trend_clusters(analyzed_trends)
    print(f"Detected {len(set(cluster_mapping.values()))} clusters.")

    # 3. Enrich
    # This function must also generate 'scores_to_cache.json' internally
    print("Enriching data...")
    enriched_trends = enricher.enrich_trends(analyzed_trends, cluster_mapping)
    
    # 4. Save final data to cache file
    output_dir = "cache"
    os.makedirs(output_dir, exist_ok=True)
    
    # This is the primary artifact of this workflow
    output_path = os.path.join(output_dir, "latest_trends.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        # Note: We are not calling the to_dict_for_frontend() method here,
        # as the generator will handle that. We save the full enriched data.
        json.dump([item.to_dict() for item in enriched_trends], f, ensure_ascii=False, indent=2)
        
    print(f"[INFO] FETCHER pipeline complete. Saved data to {output_path}")

if __name__ == "__main__":
    run_fetcher_pipeline()
