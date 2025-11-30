import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader

def generate_site():
    # 1. Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    cache_dir = os.path.join(base_dir, 'cache')
    dist_dir = os.path.join(base_dir, 'dist')
    
    # 2. Prepare dist directory
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # 3. Copy static assets
    shutil.copytree(static_dir, os.path.join(dist_dir, 'static'))
    
    # 4. Copy trends.json for CSR
    trends_json_src = os.path.join(cache_dir, 'trends.json')
    trends_json_dst = os.path.join(dist_dir, 'trends.json')
    
    if os.path.exists(trends_json_src):
        shutil.copy2(trends_json_src, trends_json_dst)
        print(f"Copied trends.json to {trends_json_dst}")
    else:
        print("Warning: cache/trends.json not found. Site will be empty.")

    # 5. Render HTML (Static Shell)
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('layout.html')
    
    # We no longer pass 'trends' data to the template
    # The template will fetch 'trends.json' via JS
    html_content = template.render(
        ga4_tracking_id=os.environ.get('GA4_TRACKING_ID', '')
    )
    
    with open(os.path.join(dist_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Site generated in {dist_dir}")

if __name__ == "__main__":
    generate_site()
