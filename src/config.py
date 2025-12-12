# src/config.py
"""
VIBRA スクレイピング設定
CSSセレクターは実際のDOM構造に応じて調整が必要です
"""

# データソース設定
DATA_SOURCE_URL = "https://search.yahoo.co.jp/realtime/search/matome"
REQUEST_TIMEOUT_SECONDS = 10
ANALYZE_TREND_COUNT = 10  # 詳細取得する上位トレンド数

# リクエストヘッダー
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

# CSSセレクター（仮設定 - 実際のDOM構造に応じて要調整）
# Yahoo!リアルタイム検索のトレンド一覧ページ用
TREND_SELECTORS = [
    "li[class*='Trend']",           # トレンドアイテムのリスト要素
    "div[class*='TrendItem']",      # 代替セレクター
]

TITLE_SELECTOR = "a[class*='title'], span[class*='keyword']"
POSTS_COUNT_SELECTOR = "span[class*='count'], span[class*='post']"
DETAIL_URL_SELECTOR = "a[href*='realtime']"

# 詳細ページの投稿テキスト用セレクター
POST_TEXT_SELECTOR = "p[class*='Post'], div[class*='tweet'], p[class*='content']"
