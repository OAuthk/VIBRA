# src/models.py
"""
VIBRAデータモデル定義
パイプライン全体で使用するdataclass
"""
from dataclasses import dataclass, asdict, field
from typing import List, Dict


@dataclass(frozen=True)
class Link:
    """外部リンク情報"""
    type: str           # 'search', 'shop', etc.
    provider: str       # 'Google', 'Mercari', etc.
    display_text: str   # 表示テキスト
    url: str


@dataclass(frozen=True)
class RawTrendItem:
    """スクレイパーから返される生データ"""
    title: str
    posts_num: int
    detail_url: str
    related_posts: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class AnalyzedTrendItem:
    """分析済みトレンドデータ"""
    title: str
    posts_num: int
    detail_url: str
    related_posts: List[str]
    co_occurring_words: List[str]
    cluster_id: int


@dataclass(frozen=True)
class EnrichedTrendItem:
    """エンリッチメント済みトレンドデータ（最終形）"""
    title: str
    posts_num: int
    score: int
    heatLevel: str
    co_occurring_words: List[str]
    links: List[Link]
    category: str
    cluster_id: int

    def to_dict(self) -> Dict:
        """JSON保存用の辞書変換"""
        return asdict(self)
