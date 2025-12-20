# src/enricher.py
"""
VIBRAエンリッチメントモジュール
スコア計算、ヒートレベル判定、リンク生成
"""
import os
import json
import math
import urllib.parse
from typing import List, Dict

import category_classifier
from models import AnalyzedTrendItem, EnrichedTrendItem, Link


# スコア計算の重み
W1_RANK = 0.4
W2_POSTS = 0.3
W3_VELOCITY = 0.3
# 急上昇判定の閾値（少し緩和 20 -> 15）
VELOCITY_THRESHOLD_HIGH = 15

# カテゴリリストは category_classifier.py に移動


def enrich_trends(analyzed_trends: List[AnalyzedTrendItem]) -> List[EnrichedTrendItem]:
    """
    分析済みトレンドにスコア、ヒートレベル、リンク等を付与する。
    
    Args:
        analyzed_trends: 分析済みトレンドリスト
        
    Returns:
        List[EnrichedTrendItem]: エンリッチメント済みトレンドリスト
    """
    print(f"[INFO][enricher] Enriching {len(analyzed_trends)} trends...")
    
    # 前回スコアの読み込み
    previous_scores = _load_previous_scores()
    current_scores: Dict[str, int] = {}
    
    # 最大投稿数（正規化用）
    max_posts = max((t.posts_num for t in analyzed_trends), default=1) or 1
    total_trends = len(analyzed_trends)
    
    enriched_list: List[EnrichedTrendItem] = []
    
    for i, trend in enumerate(analyzed_trends):
        # スコア計算
        rank_metric = (1 - (i / total_trends)) * 100 if total_trends > 0 else 50
        post_metric = (math.log1p(trend.posts_num) / math.log1p(max_posts)) * 100
        
        previous_score = previous_scores.get(trend.title, 0)
        # 前回のスコアがない（新規）場合は高めのVelocityを与える
        if previous_score == 0:
            velocity_metric = 100 
        else:
            velocity_metric = max(0, 100 - (previous_score - 0)) # 簡易計算
            
        # Velocity計算の精密化: 今回ランクインして、かつ前回より高い場合にスコアを加算したいが、
        # ここではシンプルに「現在の勢い」を表現する構成にする
        
        score = int(
            W1_RANK * rank_metric +
            W2_POSTS * post_metric +
            W3_VELOCITY * velocity_metric
        )
        score = min(100, max(0, score))
        current_scores[trend.title] = score
        
        # ヒートレベル判定
        velocity_diff = score - previous_score
        
        # 条件緩和: 
        # 1. 急上昇 (Diff >= 15) かつ スコア50以上
        # 2. 殿堂入り級 (Score >= 90) -> 常にHigh
        if (velocity_diff >= VELOCITY_THRESHOLD_HIGH and score > 50) or score >= 90:
            heat_level = 'high'
        elif score > 60:
            heat_level = 'medium'
        else:
            heat_level = 'low'
        
        # リンク生成
        links = _generate_links(trend.title)
        
        # カテゴリ分類（キーワードマッチング戦略）
        category = category_classifier.classify_category(trend)
        
        # 概要（最初の関連投稿を使用）
        summary = ""
        if trend.related_posts and len(trend.related_posts) > 0:
            summary = trend.related_posts[0]
            # 長すぎる場合は切り詰め
            if len(summary) > 100:
                summary = summary[:100] + "..."

        # EnrichedTrendItem生成
        enriched_list.append(EnrichedTrendItem(
            title=trend.title,
            posts_num=trend.posts_num,
            score=score,
            heatLevel=heat_level,
            co_occurring_words=trend.co_occurring_words,
            links=links,
            category=category,
            cluster_id=trend.cluster_id,
            summary=summary
        ))
    
    # 現在スコアを保存（次回実行用）
    _save_current_scores(current_scores)
    
    print(f"[INFO][enricher] Enrichment complete.")
    return enriched_list


def _load_previous_scores() -> Dict[str, int]:
    """前回のスコアデータを読み込む"""
    path = 'cache/previous_scores.json'
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_current_scores(scores: Dict[str, int]) -> None:
    """現在のスコアを保存"""
    os.makedirs('cache', exist_ok=True)
    with open('cache/scores_to_cache.json', 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def _generate_links(keyword: str) -> List[Link]:
    """キーワードに基づくリンクを生成"""
    query = urllib.parse.quote(keyword)
    mercari_affiliate_id = os.environ.get('MERCARI_AFFILIATE_ID', '')
    
    links = [
        Link(
            type='search',
            provider='Google',
            display_text='Google検索',
            url=f"https://www.google.com/search?q={query}"
        ),
        Link(
            type='shop',
            provider='Mercari',
            display_text='メルカリ',
            url=f"https://jp.mercari.com/search?keyword={query}" + 
                (f"&afid={mercari_affiliate_id}" if mercari_affiliate_id else "")
        )
    ]
    
    return links
