# src/analyzer.py
"""
VIBRAトレンド分析モジュール
共起語抽出とクラスタリング
"""
from janome.tokenizer import Tokenizer
from collections import Counter
import networkx as nx
import community.community_louvain as community_louvain
from typing import List, Dict

from models import RawTrendItem, AnalyzedTrendItem


def analyze_trends(raw_trends: List[RawTrendItem]) -> List[AnalyzedTrendItem]:
    """
    生トレンドデータを分析し、共起語とクラスタIDを付与する。
    
    Args:
        raw_trends: スクレイパーからの生データリスト
        
    Returns:
        List[AnalyzedTrendItem]: 分析済みトレンドリスト
    """
    print(f"[INFO][analyzer] Analyzing {len(raw_trends)} trends...")
    
    # 1. 共起語抽出
    trends_with_cowords = _extract_co_occurring_words(raw_trends)
    
    # 2. クラスタリング
    cluster_mapping = _detect_clusters(trends_with_cowords)
    
    # 3. AnalyzedTrendItemを生成
    analyzed_items: List[AnalyzedTrendItem] = []
    
    for trend, co_words in trends_with_cowords:
        cluster_id = cluster_mapping.get(trend.title, 0)
        
        analyzed_items.append(AnalyzedTrendItem(
            title=trend.title,
            posts_num=trend.posts_num,
            detail_url=trend.detail_url,
            related_posts=trend.related_posts,
            co_occurring_words=co_words,
            cluster_id=cluster_id
        ))
    
    print(f"[INFO][analyzer] Analysis complete. {len(analyzed_items)} items processed.")
    return analyzed_items


def _extract_co_occurring_words(
    raw_trends: List[RawTrendItem]
) -> List[tuple[RawTrendItem, List[str]]]:
    """
    各トレンドの関連投稿から共起名詞を抽出する。
    
    Returns:
        List[(RawTrendItem, List[str])]: トレンドと共起語のタプルリスト
    """
    t = Tokenizer()
    results = []
    
    for i, trend in enumerate(raw_trends):
        co_words = []
        
        # 上位5件のみ詳細分析
        if i < 5 and trend.related_posts:
            all_text = " ".join(trend.related_posts)
            tokens = t.tokenize(all_text)
            nouns = []
            
            for token in tokens:
                part_of_speech = token.part_of_speech.split(',')
                if part_of_speech[0] == '名詞' and part_of_speech[1] in ['一般', '固有名詞']:
                    # トレンドキーワード自体は除外
                    if token.surface != trend.title:
                        nouns.append(token.surface)
            
            # 出現頻度でソートし上位3件を取得
            counter = Counter(nouns)
            co_words = [word for word, _ in counter.most_common(3)]
        
        results.append((trend, co_words))
    
    return results


def _detect_clusters(
    trends_with_cowords: List[tuple[RawTrendItem, List[str]]]
) -> Dict[str, int]:
    """
    Louvain法でクラスタを検出する。
    すべてのトレンドを孤立ノードも含めてクラスタリング対象とする。
    
    Returns:
        Dict[str, int]: トレンドタイトル → クラスタID のマッピング
    """
    G = nx.Graph()
    
    # Step 1: 全トレンドタイトルをノードとして追加
    # これにより、共起語がないトレンド（孤立ノード）も確実に含まれる
    all_trend_titles = [trend.title for trend, _ in trends_with_cowords]
    G.add_nodes_from(all_trend_titles)
    
    # Step 2: 共起関係に基づくエッジ構築
    for trend, co_words in trends_with_cowords:
        for related in co_words:
            # エッジは既存ノード間のみに作成（一貫性のため）
            if related and G.has_node(related):
                if G.has_edge(trend.title, related):
                    G[trend.title][related]['weight'] += 1
                else:
                    G.add_edge(trend.title, related, weight=1)
    
    if G.number_of_nodes() == 0:
        return {}
    
    # Step 3: Louvainアルゴリズム実行
    try:
        partition = community_louvain.best_partition(G, resolution=1.0)
        # 孤立ノードは個別のクラスタIDが割り当てられる
        print(f"[INFO][analyzer] Detected {len(set(partition.values()))} clusters, including isolated nodes.")
    except Exception as e:
        print(f"[WARNING][analyzer] Clustering failed: {e}")
        partition = {node: 0 for node in G.nodes()}
    
    return partition

