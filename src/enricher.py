import os
import json
import math
import random
import urllib.parse
from typing import List, Dict
from models import EnrichedTrendItem, Link

# --- 1. 定数と重みの定義 ---
W1_RANK = 0.4
W2_POSTS = 0.3
W3_VELOCITY = 0.3
VELOCITY_THRESHOLD_HIGH = 20

# --- 2. 前回のスコアを読み込むヘルパー関数 ---
def _load_previous_scores() -> Dict[str, int]:
    """GitHub Actions Cacheから復元された前回のスコアデータを読み込む"""
    path = 'cache/previous_scores.json'
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def enrich_trends(trends: List[Dict]) -> List[EnrichedTrendItem]:
    """
    Adds score, heatLevel, google_search_url, and affiliate links.
    Returns a list of EnrichedTrendItem objects.
    """
    mercari_affiliate_id = os.environ.get('MERCARI_AFFILIATE_ID', '')
    
    previous_scores = _load_previous_scores()
    current_scores: Dict[str, int] = {}
    enriched_list: List[EnrichedTrendItem] = []
    
    # Mock categories for now since scraper doesn't provide them
    CATEGORIES = ['総合', 'エンタメ', 'ニュース', 'スポーツ', 'IT']
    
    # Calculate max posts for normalization
    for i, trend in enumerate(trends):
        if 'posts_num' not in trend:
             # Mock post volume: Rank 1 has ~10000, Rank 20 has ~100
             trend['posts_num'] = int(10000 / (i + 1))

    max_posts_num = max([t.get('posts_num', 1) for t in trends] or [1])
    total_trends = len(trends)
    
    for i, trend in enumerate(trends):
        # --- 各指標の正規化 (0-100) ---
        rank_metric = (1 - (i / total_trends)) * 100
        post_volume_metric = (math.log1p(trend.get('posts_num', 0)) / math.log1p(max_posts_num)) * 100
        
        keyword = trend['keyword']
        previous_score = previous_scores.get(keyword, 0)
        velocity_metric = max(0, 100 - previous_score)

        # --- 最終スコアの計算 ---
        score = int(
            W1_RANK * rank_metric +
            W2_POSTS * post_volume_metric +
            W3_VELOCITY * velocity_metric
        )
        score = min(100, max(0, score))
        current_scores[keyword] = score
        
        # --- velocityに基づくheatLevelの決定 ---
        velocity_diff = score - previous_score
        
        if velocity_diff >= VELOCITY_THRESHOLD_HIGH and score > 50:
            heatLevel = 'high'
        elif score > 60:
            heatLevel = 'medium'
        else:
            heatLevel = 'low'
            
        # URLs
        query = urllib.parse.quote(keyword)
        google_search_url = f"https://www.google.com/search?q={query}"
        mercari_url = f"https://jp.mercari.com/search?keyword={query}"
        if mercari_affiliate_id:
             mercari_url += f"&afid={mercari_affiliate_id}"
        
        # Create Link objects
        links = [
            Link(provider='Google', url=google_search_url),
            Link(provider='Mercari', url=mercari_url)
        ]
        
        # Assign random category for demo
        category = random.choice(CATEGORIES)
        
        item = EnrichedTrendItem(
            title=keyword,
            posts_num=trend.get('posts_num', 0),
            score=score,
            heatLevel=heatLevel,
            co_occurring_words=trend.get('related_nouns', []),
            links=links,
            category=category,
            rank=trend.get('rank', i+1),
            google_search_url=google_search_url,
            mercari_url=mercari_url
        )
        enriched_list.append(item)
             
    # --- 4. 次回実行のために現在のスコアをファイルに保存 ---
    if not os.path.exists('cache'):
        os.makedirs('cache')
    with open('cache/scores_to_cache.json', 'w', encoding='utf-8') as f:
        json.dump(current_scores, f, ensure_ascii=False, indent=2)
             
    return enriched_list
