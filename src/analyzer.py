from janome.tokenizer import Tokenizer
from collections import Counter
import networkx as nx
import community.community_louvain as community_louvain
from typing import List, Dict

def analyze_trends(trends: List[Dict]) -> List[Dict]:
    """
    Analyzes trends to extract co-occurring nouns.
    Modifies the trends list in-place.
    """
    t = Tokenizer()
    
    for trend in trends:
        # We only analyze top 5 trends as per spec
        if trend.get('rank', 999) > 5:
            continue
            
        all_text = " ".join(trend.get('post_texts', []))
        
        tokens = t.tokenize(all_text)
        nouns = []
        
        for token in tokens:
            part_of_speech = token.part_of_speech.split(',')
            if part_of_speech[0] == '名詞' and part_of_speech[1] in ['一般', '固有名詞']:
                # Filter out the trend keyword itself to find *co-occurring* words
                if token.surface != trend['keyword']:
                    nouns.append(token.surface)
        
        # Count frequency
        c = Counter(nouns)
        
        # Get top 3
        top_nouns = [word for word, count in c.most_common(3)]
        trend['related_nouns'] = top_nouns
        
    return trends

def detect_trend_clusters(raw_trends: List[Dict]) -> Dict[str, int]:
    """
    Detects communities using Louvain method.
    Returns: {'keyword1': 0, 'keyword2': 0, 'keyword3': 1, ...}
    """
    G = nx.Graph()
    
    # 1. Build Graph
    for trend in raw_trends:
        main_word = trend['keyword']
        G.add_node(main_word)
        
        related_words = trend.get('related_nouns', [])
        for related in related_words:
            if related: # Ensure not empty
                # Add edge with weight 1 (or increment if exists)
                if G.has_edge(main_word, related):
                    G[main_word][related]['weight'] += 1
                else:
                    G.add_edge(main_word, related, weight=1)
    
    if G.number_of_nodes() == 0:
        return {}

    # 2. Run Louvain Algorithm
    # resolution parameter controls cluster size (higher = smaller clusters)
    try:
        partition = community_louvain.best_partition(G, resolution=1.0)
    except Exception as e:
        print(f"Clustering failed: {e}")
        # Fallback: assign all to cluster 0
        partition = {node: 0 for node in G.nodes()}
    
    return partition
