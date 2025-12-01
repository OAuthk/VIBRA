import os
import json
import shutil
import sys
from jinja2 import Environment, FileSystemLoader

def generate_site_from_cache():
    """Reads data from the cache and generates all static site artifacts."""
    print("[INFO] Starting DEPLOYER pipeline...")
    
    # 1. Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(base_dir, 'cache')
    dist_dir = os.path.join(base_dir, 'dist')
    templates_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    # 2. Load data from cache
    cache_path = os.path.join(cache_dir, 'latest_trends.json')
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            full_trends_data = json.load(f)
            print(f"Loaded {len(full_trends_data)} trends from cache.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[CRITICAL] Failed to load cache file '{cache_path}'. Halting. Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Prepare dist directory
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # 4. Transform data for frontend
    # We replicate the logic from models.py's to_dict_for_frontend here
    # or we could import models.py if we wanted to deserialize.
    # Working with dicts is sufficient here.
    frontend_trends = []
    for item in full_trends_data:
        # Determine 'stage' based on heatLevel and score
        heatLevel = item.get('heatLevel', 'low')
        score = item.get('score', 0)
        
        if heatLevel == 'high' and score > 80:
            stage = 'peak'
        elif score < 30:
            stage = 'fading'
        else:
            stage = 'newborn'

        frontend_item = {
            "text": item.get('title'),
            "category": item.get('category'),
            "stage": stage,
            "score": score,
            "heatLevel": heatLevel,
            "detail_url": item.get('google_search_url'),
            "related_words": item.get('co_occurring_words', []),
            "cluster_id": item.get('cluster_id', 0)
        }
        frontend_trends.append(frontend_item)

    # 5. Save frontend data
    trends_json_dst = os.path.join(dist_dir, 'trends.json')
    with open(trends_json_dst, 'w', encoding='utf-8') as f:
        json.dump(frontend_trends, f, ensure_ascii=False, indent=2)
    print(f"Generated frontend data at {trends_json_dst}")

    # 6. Copy static assets
    if os.path.exists(static_dir):
        shutil.copytree(static_dir, os.path.join(dist_dir, 'static'))
        print("Copied static assets.")
    else:
        print("Warning: static directory not found.")

    # 7. Render HTML
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
