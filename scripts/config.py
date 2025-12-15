# scripts/config.py
"""
VIBRA プロジェクト設定ファイル
このファイルは、スクレイピング、分析、エンリッチメント、サイト生成など、
プロジェクト全体の挙動を制御する全ての定数を一元管理します。
"""
import os

# ================================================
# データソース設定 (Scraper用)
# ================================================
DATA_SOURCE_URL = "https://search.yahoo.co.jp/realtime/search/matome"
REQUEST_TIMEOUT_SECONDS = 30  # Playwrightは時間がかかるため延長
ANALYZE_TREND_COUNT = 5

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

# --- CSSセレクター (人間による最終調査済み・本番用) ---
# 1. トレンド一覧ページで、各トレンドを囲む親要素
TREND_SELECTORS = [
    "div[class*='MatomeListItem_MatomeListItem__']"
]

# 2. 上記の親要素の"中"から、各情報を見つけるためのセレクタ
TITLE_SELECTOR = "h2 > span"
POSTS_COUNT_SELECTOR = "p[class*='MatomeListItem_post__'] > span"
DETAIL_URL_SELECTOR = "a" # 親要素の中の最初のaタグ

# 3. 詳細ページ内で、関連ポストの本文を見つけるためのセレクタ
# (これは別途、詳細ページのHTMLを調査して確定させる必要があるが、一旦推測値を入れておく)
POST_TEXT_SELECTOR = "p[class*='Post_body__']"

# ================================================
# テキストマイニング設定 (Analyzer用)
# ================================================
CO_OCCURRING_WORD_COUNT = 3

# ================================================
# エンリッチメント設定 (Enricher用)
# ================================================
GENERATE_GOOGLE_LINK = True
GENERATE_MERCARI_LINK = True
MERCARI_AFFILIATE_ID = os.environ.get('MERCARI_AFFILIATE_ID', '')
W1_RANK = 0.4
W2_POSTS = 0.3
W3_VELOCITY = 0.3
VELOCITY_THRESHOLD_HIGH = 20

# ================================================
# アクセス解析設定 (Generator用)
# ================================================
GA4_TRACKING_ID = os.environ.get('GA4_TRACKING_ID', 'G-DEFAULTXXXXXXXX')

# ================================================
# サイト生成設定 (Generator用)
# ================================================
TEMPLATE_DIR = "templates"
TEMPLATE_NAME = "layout.html"
OUTPUT_DIR = "dist"
TIMEZONE = "Asia/Tokyo"