# src/scraper.py
"""
VIBRAトレンドスクレイパー
Yahoo!リアルタイム検索からトレンドデータを取得
"""
import requests
from bs4 import BeautifulSoup
from typing import List

import config
from models import RawTrendItem


def fetch_raw_trends() -> List[RawTrendItem]:
    """
    データソースからトレンドデータを取得し、RawTrendItemのリストを返す。
    スクレイパーモジュールの単一エントリーポイント。
    
    Returns:
        List[RawTrendItem]: 取得したトレンドデータのリスト。失敗時は空リスト。
    """
    print("[INFO][scraper] Starting to fetch trend list...")
    
    try:
        response = requests.get(
            config.DATA_SOURCE_URL,
            headers=config.REQUEST_HEADERS,
            timeout=config.REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 複数のセレクターを試行
        trend_elements = []
        for selector in config.TREND_SELECTORS:
            trend_elements = soup.select(selector)
            if trend_elements:
                print(f"[INFO][scraper] Found {len(trend_elements)} elements with selector: {selector}")
                break
        
        if not trend_elements:
            print("[WARNING][scraper] No trend elements found. CSS selectors might be outdated.")
            return []

    except requests.RequestException as e:
        print(f"[ERROR][scraper] Failed to fetch trend list page: {e}")
        return []

    raw_trends: List[RawTrendItem] = []
    
    for i, element in enumerate(trend_elements):
        try:
            # タイトル抽出
            title_elem = element.select_one(config.TITLE_SELECTOR)
            if not title_elem:
                # フォールバック: 最初のリンクテキストを使用
                title_elem = element.find('a')
            
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            if not title:
                continue

            # 投稿数抽出
            posts_num = 0
            posts_elem = element.select_one(config.POSTS_COUNT_SELECTOR)
            if posts_elem:
                posts_text = posts_elem.text
                # 数値を抽出（「1,234件」「1234 posts」等に対応）
                import re
                numbers = re.findall(r'[\d,]+', posts_text)
                if numbers:
                    posts_num = int(numbers[0].replace(',', ''))

            # 詳細URL抽出
            detail_url = ""
            url_elem = element.select_one(config.DETAIL_URL_SELECTOR)
            if url_elem and url_elem.get('href'):
                detail_url = url_elem['href']
                # 相対URLを絶対URLに変換
                if detail_url.startswith('/'):
                    detail_url = f"https://search.yahoo.co.jp{detail_url}"
            
            # 上位N件のみ詳細ページから関連投稿を取得
            related_posts = []
            if i < config.ANALYZE_TREND_COUNT and detail_url:
                print(f"[INFO][scraper] Fetching details for '{title}'...")
                related_posts = _fetch_related_posts_from_detail(detail_url)

            # RawTrendItemを作成して追加
            raw_trends.append(RawTrendItem(
                title=title,
                posts_num=posts_num,
                detail_url=detail_url,
                related_posts=related_posts
            ))
            
        except (AttributeError, ValueError, TypeError) as e:
            print(f"[WARNING][scraper] Skipping item due to parsing error: {e}")
            continue
    
    print(f"[INFO][scraper] Successfully fetched {len(raw_trends)} trends.")
    return raw_trends


def _fetch_related_posts_from_detail(url: str) -> List[str]:
    """
    詳細ページから関連投稿テキストを取得するヘルパー関数。
    
    Args:
        url: 詳細ページのURL
        
    Returns:
        List[str]: 投稿テキストのリスト。失敗時は空リスト。
    """
    try:
        response = requests.get(
            url, 
            headers=config.REQUEST_HEADERS, 
            timeout=config.REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 投稿テキスト要素を取得
        post_elements = soup.select(config.POST_TEXT_SELECTOR)
        
        # テキストを抽出（上位5件まで）
        posts = []
        for elem in post_elements[:5]:
            text = elem.text.strip()
            if len(text) > 10:  # 短すぎるテキストは除外
                posts.append(text)
        
        return posts
        
    except (requests.RequestException, AttributeError) as e:
        print(f"[WARNING][scraper] Failed to fetch related posts from {url}: {e}")
        return []


# 後方互換性のためのエイリアス（非推奨）
def fetch_trends() -> List[dict]:
    """
    [DEPRECATED] 後方互換性のため維持。fetch_raw_trends()を使用してください。
    """
    print("[WARNING][scraper] fetch_trends() is deprecated. Use fetch_raw_trends() instead.")
    raw_trends = fetch_raw_trends()
    return [
        {
            "rank": i + 1,
            "keyword": item.title,
            "url": item.detail_url,
            "posts_num": item.posts_num,
            "post_texts": item.related_posts
        }
        for i, item in enumerate(raw_trends)
    ]
