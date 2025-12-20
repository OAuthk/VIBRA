# src/generator.py
"""
VIBRAサイトジェネレーター
キャッシュからデータを読み込み、静的サイトを生成
"""
import os
import json
import shutil
import sys
from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader

from models import EnrichedTrendItem, Link


# カテゴリマッピング（日本語 → フロントエンド用）
CATEGORY_MAPPING = {
    'IT': 'technology',
    'テクノロジー': 'technology',
    '総合': 'all',
    'ニュース': 'business',
    'ビジネス': 'business',
    'スポーツ': 'entertainment',
    'エンタメ': 'entertainment',
    'politics': 'business',   # フロントエンドにpoliticsがないためbusinessに寄せる
    'social': 'all'
}


def generate_site_from_cache():
    """キャッシュからデータを読み込み、静的サイトを生成する"""
    print("[INFO] Starting DEPLOYER pipeline...")
    
    # 1. パス設定
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(base_dir, 'cache')
    dist_dir = os.path.join(base_dir, 'dist')
    templates_dir = os.path.join(base_dir, 'templates')
    
    # 2. キャッシュからデータ読み込み
    cache_path = os.path.join(cache_dir, 'latest_trends.json')
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            # JSONからEnrichedTrendItemを復元
            trends_data = _deserialize_trends(raw_data)
            print(f"Loaded and deserialized {len(trends_data)} trends from cache.")
    except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
        print(f"[CRITICAL] Failed to load cache file '{cache_path}'. Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. distディレクトリ準備
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # 3.5 静的ファイルのコピー
    static_src = os.path.join(base_dir, 'static')
    if os.path.exists(static_src):
        # dist直下に static の中身を展開するのではなく、dist/static または dist/css, dist/js として配置されるようにする
        # layout.htmlでは "css/style.css", "js/main.js" となっているので
        # static/css -> dist/css, static/js -> dist/js となるようにコピーする
        # shutil.copytreeはディレクトリごとコピーするので、
        # dist/css 等が存在しないことを確認してコピー
        
        # Simple copy: static/* -> dist/*
        # walk and copy or just copytree the whole static dir contents?
        # Typically one wants dist/css, dist/js.
        # If static has css/ and js/ inside it:
        # copytree(static, dist, dirs_exist_ok=True) (Python 3.8+)
        
        try:
            # Python 3.8+ support dirs_exist_ok
            shutil.copytree(static_src, dist_dir, dirs_exist_ok=True)
            print(f"[INFO] Copied static assets from {static_src} to {dist_dir}")
        except TypeError:
            # Fallback for older python if needed, but 3.8 is likely.
            # If dirs_exist_ok not supported, we have to iterate
             for item in os.listdir(static_src):
                s = os.path.join(static_src, item)
                d = os.path.join(dist_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
             print(f"[INFO] Copied static assets (fallback) to {dist_dir}")
    
    # 4. フロントエンド用データに変換
    frontend_trends = [_transform_for_frontend(item) for item in trends_data]

    # 5. フロントエンドデータ保存
    trends_json_dst = os.path.join(dist_dir, 'trends.json')
    output_data = {
        "trends": frontend_trends,
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    with open(trends_json_dst, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Generated frontend data at {trends_json_dst}")

    # 6. HTMLレンダリング
    env = Environment(loader=FileSystemLoader(templates_dir))
    template_vars = {
        'ga4_tracking_id': os.environ.get('GA4_TRACKING_ID', ''),
        'current_year': datetime.now().year,
        'cache_bust_version': int(datetime.now().timestamp())
    }
    
    # index.html
    template = env.get_template('layout.html')
    html_content = template.render(**template_vars)
    with open(os.path.join(dist_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Generated index.html")
    
    # guidelines.html
    try:
        guidelines_template = env.get_template('guidelines.html')
        guidelines_content = guidelines_template.render(**template_vars)
        with open(os.path.join(dist_dir, 'guidelines.html'), 'w', encoding='utf-8') as f:
            f.write(guidelines_content)
        print("Generated guidelines.html")
    except Exception as e:
        print(f"[WARN] Could not generate guidelines.html: {e}")
        
    print(f"[INFO] DEPLOYER pipeline complete. Site generated in '{dist_dir}'.")


def _deserialize_trends(raw_data: List[Dict[str, Any]]) -> List[EnrichedTrendItem]:
    """JSONデータからEnrichedTrendItemを復元"""
    items = []
    for data in raw_data:
        # linksをLinkオブジェクトに変換
        links = []
        for link_data in data.get('links', []):
            links.append(Link(**link_data))
        
        items.append(EnrichedTrendItem(
            title=data['title'],
            posts_num=data['posts_num'],
            score=data['score'],
            heatLevel=data['heatLevel'],
            co_occurring_words=data.get('co_occurring_words', []),
            links=links,
            category=data['category'],
            cluster_id=data.get('cluster_id', 0),
            summary=data.get('summary', "")
        ))
    return items


def _transform_for_frontend(item: EnrichedTrendItem) -> Dict[str, Any]:
    """EnrichedTrendItemをフロントエンド用形式に変換"""
    # ステージ判定（緩和）
    # High heat OR high score triggers peak visuals
    if item.heatLevel == 'high' or item.score > 85:
        stage = 'peak'
    elif item.score < 30:
        stage = 'fading'
    else:
        stage = 'newborn'
    
    # カテゴリ正規化
    normalized_category = CATEGORY_MAPPING.get(item.category, 'all')
    
    # Detail URL extraction (Priority: Google -> Mercari -> First Link)
    detail_url = ""
    if item.links:
        for link in item.links:
            if link.provider == 'Google':
                detail_url = link.url
                break
        if not detail_url:
            detail_url = item.links[0].url

    # Title Sanitization
    title = item.title
    # Check for None, empty, or specific keywords (case-insensitive)
    # Check for None, empty, or specific keywords (case-insensitive)
    title_str = str(title).strip() if title else ""
    if not title_str or title_str.upper() in ["UNDEFINED", "NULL", "NONE"] or "undefined" in title_str.lower():
        title = "注目トピック"


    return {
        "text": title,
        "category": normalized_category,
        "stage": stage,
        "score": item.score,
        "heatLevel": item.heatLevel,
        "detail_url": detail_url,
        "related_words": item.co_occurring_words if item.co_occurring_words else [], 
        "cluster_id": item.cluster_id,
        "summary": item.summary if item.summary else "詳細情報なし"
    }


if __name__ == "__main__":
    generate_site_from_cache()
