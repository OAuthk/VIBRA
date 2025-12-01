import os
import json
import shutil
import sys
from jinja2 import Environment, FileSystemLoader
from models import EnrichedTrendItem

def generate_site_from_cache():
    """Reads data from the cache and generates all static site artifacts."""
    print("[INFO] Starting DEPLOYER pipeline...")
    
    # 1. Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(base_dir, 'cache')
    dist_dir = os.path.join(base_dir, 'dist')
    templates_dir = os.path.join(base_dir, 'templates')
    
    # 2. Load and Deserialize data from cache
    cache_path = os.path.join(cache_dir, 'latest_trends.json')
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            # Deserialize JSON dicts into EnrichedTrendItem objects
            full_trends_data = [EnrichedTrendItem(**item) for item in json.load(f)]
            print(f"Loaded and deserialized {len(full_trends_data)} trends from cache.")
    except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
        print(f"[CRITICAL] Failed to load or deserialize cache file '{cache_path}'. Halting. Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Prepare dist directory
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # 4. Transform data for frontend using the single source of truth
    frontend_trends = [item.to_dict_for_frontend() for item in full_trends_data]

    # 5. Save frontend data
    trends_json_dst = os.path.join(dist_dir, 'trends.json')
    with open(trends_json_dst, 'w', encoding='utf-8') as f:
        json.dump(frontend_trends, f, ensure_ascii=False, indent=2)
    print(f"Generated frontend data at {trends_json_dst}")

    # 6. Render HTML
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('layout.html')
    
    html_content = template.render(
        ga4_tracking_id=os.environ.get('GA4_TRACKING_ID', '')
    )
    
    with open(os.path.join(dist_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"[INFO] DEPLOYER pipeline complete. Site generated in '{dist_dir}'.")

if __name__ == "__main__":
    generate_site_from_cache()
