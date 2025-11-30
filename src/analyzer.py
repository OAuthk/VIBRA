from janome.tokenizer import Tokenizer
from collections import Counter
import re

def analyze_trends(trends):
    """
    Analyzes trends to extract co-occurring nouns.
    Modifies the trends list in-place.
    """
    t = Tokenizer()
    
    for trend in trends:
        # We only analyze top 5 trends as per spec
        if trend['rank'] > 5:
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
