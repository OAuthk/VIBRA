import os
import json
import time
import datetime
from scraper import fetch_trends, fetch_trend_details
from analyzer import analyze_trends, detect_trend_clusters
from enricher import enrich_trends

def main():
    print("Starting VIBRA Data Pipeline...")
    
    # 1. Scrape
    print("Fetching trends...")
    trends = fetch_trends()
    print(f"Found {len(trends)} trends.")
    
    if not trends:
        print("No trends found. Exiting.")
        return

    # Fetch details for top 5
    print("Fetching details for top 5 trends...")
    # For demo, limit details fetching to top 5 to save time/requests
    trends_with_details = []
    for trend in trends[:5]:
        # Mock logic in scraper expects the URL string
        posts = fetch_trend_details(trend['url'])
        trend['post_texts'] = posts
        trends_with_details.append(trend)
    
    # Combine with the rest (which won't have details but that's fine for now)
    all_trends = trends_with_details + trends[5:]
    
    # 2. Analyze
    print("Analyzing trends...")
    # Basic analysis
    analyzed_trends = analyze_trends(all_trends)
    
    # Community Detection (Clustering)
    print("Detecting trend clusters...")
    cluster_mapping = detect_trend_clusters(analyzed_trends)
    print(f"Detected {len(set(cluster_mapping.values()))} clusters.")
    
    # 3. Enrich
    print("Enriching data...")
    enriched_trends = enrich_trends(analyzed_trends, cluster_mapping)
    
    # 4. Output
    output_dir = "cache"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate trends.json for Frontend
    last_updated_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')
    
    app_data = {
        "last_updated": last_updated_str,
        "trends": [item.to_dict_for_frontend() for item in enriched_trends]
    }
    
    trends_json_path = os.path.join(output_dir, "trends.json")
    with open(trends_json_path, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
        
    # Save the same content to latest_trends.json for compatibility
    latest_trends_path = os.path.join(output_dir, "latest_trends.json")
    with open(latest_trends_path, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
        
    print(f"Data pipeline completed. Saved to {trends_json_path}")

if __name__ == "__main__":
    main()
