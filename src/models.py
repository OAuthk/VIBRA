from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass(frozen=True)
class Link:
    provider: str
    url: str

@dataclass(frozen=True)
class EnrichedTrendItem:
    title: str
    posts_num: int
    score: int
    heatLevel: str
    co_occurring_words: List[str]
    links: List[Link]
    category: str
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass(frozen=True)
class Link:
    provider: str
    url: str

@dataclass(frozen=True)
class EnrichedTrendItem:
    title: str
    posts_num: int
    score: int
    heatLevel: str
    co_occurring_words: List[str]
    links: List[Link]
    category: str
    rank: int
    google_search_url: str
    mercari_url: str
    cluster_id: int = 0  # Default to 0

    def to_dict_for_frontend(self) -> Dict:
        """
        Generates a dictionary specifically for the frontend JavaScript,
        mapping our backend names to the expected frontend names.
        """
        # Determine 'stage' based on heatLevel and score
        if self.heatLevel == 'high' and self.score > 80:
            stage = 'peak'
        elif self.score < 30:
            stage = 'fading'
        else:
            stage = 'newborn' # Default for medium or new items

        return {
            "text": self.title,
            "category": self.category,
            "stage": stage,
            "score": self.score,
            "heatLevel": self.heatLevel,
            "detail_url": self.google_search_url, # Using Google Search as detail URL for now
            "related_words": self.co_occurring_words,
            "cluster_id": self.cluster_id
        }
