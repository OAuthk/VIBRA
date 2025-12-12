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
    
    # 4. フロントエンド用データに変換
    frontend_trends = [_transform_for_frontend(item) for item in trends_data]

    # 5. フロントエンドデータ保存
    trends_json_dst = os.path.join(dist_dir, 'trends.json')
    with open(trends_json_dst, 'w', encoding='utf-8') as f:
        json.dump(frontend_trends, f, ensure_ascii=False, indent=2)
    print(f"Generated frontend data at {trends_json_dst}")

    # 6. HTMLレンダリング
    env = Environment(loader=FileSystemLoader(templates_dir))
    template_vars = {
        'ga4_tracking_id': os.environ.get('GA4_TRACKING_ID', ''),
        'current_year': datetime.now().year
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
            cluster_id=data.get('cluster_id', 0)
        ))
    return items


def _transform_for_frontend(item: EnrichedTrendItem) -> Dict[str, Any]:
    """EnrichedTrendItemをフロントエンド用形式に変換"""
    # ステージ判定
    if item.heatLevel == 'high' and item.score > 80:
        stage = 'peak'
    elif item.score < 30:
        stage = 'fading'
    else:
        stage = 'newborn'
    
    # カテゴリ正規化
    normalized_category = CATEGORY_MAPPING.get(item.category, 'all')
    
    # Google検索URLを取得（Googleリンクを探す）
    detail_url = ""
    for link in item.links:
        if link.provider == 'Google':
            detail_url = link.url
            break
    
    return {
        "text": item.title,
        "category": normalized_category,
        "stage": stage,
        "score": item.score,
        "heatLevel": item.heatLevel,
        "detail_url": detail_url,
        "related_words": item.co_occurring_words,
        "cluster_id": item.cluster_id
    }


if __name__ == "__main__":
    generate_site_from_cache()
