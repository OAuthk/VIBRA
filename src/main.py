import os
import json
import time
from scraper import fetch_trends, fetch_trend_details
from analyzer import analyze_trends
from enricher import enrich_trends

def main():
    print("Starting VIBRA Data Pipeline...")
    
    # 1. Scrape
    print("Fetching trends...")
    trends = fetch_trends()
    print(f"Found {len(trends)} trends.")
    
    # Fetch details for top 5
    print("Fetching details for top 5 trends...")
    for trend in trends[:5]:
        print(f"Fetching details for: {trend['keyword']}")
        posts = fetch_trend_details(trend['url'])
        trend['post_texts'] = posts
        time.sleep(1) # Be polite to the server
        
    # 2. Analyze
    print("Analyzing trends...")
    trends = analyze_trends(trends)
    
    # 3. Enrich
    print("Enriching data...")
    enriched_trends = enrich_trends(trends)
    
    # 4. Output
    output_dir = "cache"
    os.makedirs(output_dir, exist_ok=True)
    
    # Legacy output (for reference or backup)
    # Since enriched_trends is now a list of objects, we need to convert to dict if we want to save raw
    # But for now let's just save the new format as primary 'trends.json'
    
    # Generate trends.json for Frontend
    import datetime
    last_updated_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')
    
    app_data = {
        "last_updated": last_updated_str,
        "trends": [item.to_dict_for_frontend() for item in enriched_trends]
    }
    
    trends_json_path = os.path.join(output_dir, "trends.json")
    with open(trends_json_path, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
        
    # Also save the raw latest_trends.json if needed by other processes, 
    # but we might need to serialize the objects back to dicts.
    # For simplicity, let's assume trends.json is the new standard.
    # But to keep fetcher.yml happy (it commits latest_trends.json), we should probably update fetcher.yml OR
    # just save a copy there too.
    # Let's save a copy of the frontend data as latest_trends.json for now to minimize breakage,
    # or better yet, update fetcher.yml to commit trends.json. 
    # The plan says "Modify main.py (Output trends.json)".
    # I will save as trends.json.
    # NOTE: fetcher.yml commits `cache/latest_trends.json`. I should probably update that too or save to that name.
    # Let's save the same content to latest_trends.json to be safe with existing workflow.
    
    latest_trends_path = os.path.join(output_dir, "latest_trends.json")
    with open(latest_trends_path, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, ensure_ascii=False, indent=2)
        
    print(f"Data pipeline completed. Saved to {trends_json_path}")

if __name__ == "__main__":
    main()
