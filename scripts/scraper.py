# scripts/scraper.py
"""
VIBRAトレンドスクレイパー (Playwright版)
JavaScriptで動的に生成されるコンテンツに対応し、タイムアウトエラーを防御的に処理する。
"""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List
import config  # config.pyから設定を読み込む
from models import RawTrendItem
from pydantic import BaseModel, ValidationError, HttpUrl

# Pydanticモデルを使い、スクレイピングデータの型と構造を保証する
class ScrapedItem(BaseModel):
    title: str
    posts_num: int
    detail_url: HttpUrl

async def _fetch_page_content(url: str, wait_selector: str) -> str:
    """
    Playwrightを使って指定されたURLにアクセスし、
    特定の要素が表示されるのを待ってからHTMLコンテンツを返す。
    セレクタが見つからない場合は、タイムアウト後に警告を出し、空文字を返す。
    """
    html_content = ""
    async with async_playwright() as p:
        # ヘッドレスモードでChromiumブラウザを起動
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(user_agent=config.REQUEST_HEADERS.get("User-Agent"))
        try:
            print(f"[INFO][scraper:playwright] Navigating to {url}...")
            await page.goto(url, timeout=config.REQUEST_TIMEOUT_SECONDS * 1000)
            
            print(f"[INFO][scraper:playwright] Waiting for selector '{wait_selector}'...")
            # ★ 変更点: タイムアウトを短くし、エラーを握りつぶす
            await page.wait_for_selector(wait_selector, timeout=5000) # 5秒に短縮
            
            print("[INFO][scraper:playwright] Page rendered. Getting content...")
            html_content = await page.content()
        except Exception as e:
            # ★ 変更点: タイムアウトエラーが発生しても、単に警告を出し、処理を続行する
            print(f"[WARNING][scraper:playwright] Selector '{wait_selector}' not found on {url}. It might not have this element. Error: {e}")
        finally:
            await browser.close()
    return html_content # ★ 失敗した場合は空文字が返る

def fetch_raw_trends() -> List[RawTrendItem]:
    """
    PlaywrightでJavaScriptレンダリング後のHTMLを取得し、
    トレンドデータを抽出してRawTrendItemのリストを返す。
    """
    print("[INFO][scraper] Starting fetch_raw_trends with Playwright...")
    
    # 非同期関数を実行し、HTMLコンテンツを取得
    html = asyncio.run(_fetch_page_content(
        url=config.DATA_SOURCE_URL,
        wait_selector=config.TREND_SELECTORS[0]
    ))

    if not html:
        print("[CRITICAL][scraper] Failed to get HTML content from Playwright. Exiting.")
        return []

    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html, "html.parser")

    # config.pyで定義された正確なセレクタでトレンド要素のリストを取得
    trend_elements = soup.select(config.TREND_SELECTORS[0])
    
    if not trend_elements:
        print("[WARNING][scraper] No trend elements found in Playwright-rendered HTML. CSS selector might be outdated.")
        return []

    raw_trends: List[RawTrendItem] = []
    
    for i, element in enumerate(trend_elements):
        try:
            # 各トレンド要素から情報を抽出
            title = element.select_one(config.TITLE_SELECTOR).text.strip()
            posts_num_text = element.select_one(config.POSTS_COUNT_SELECTOR).text
            posts_num = int(posts_num_text.replace("件のポスト", "").replace(",", "").strip())
            
            # URLを絶対パスに変換
            raw_url = element.select_one(config.DETAIL_URL_SELECTOR)['href']
            if raw_url.startswith('/'):
                detail_url = f"https://search.yahoo.co.jp{raw_url}"
            else:
                detail_url = raw_url

            # Pydanticでバリデーション
            ScrapedItem(title=title, posts_num=posts_num, detail_url=detail_url)

            # 上位N件のみ詳細ページから関連投稿を取得
            related_posts = []
            if i < config.ANALYZE_TREND_COUNT and detail_url:
                print(f"[INFO][scraper] Fetching details for '{title}'...")
                detail_html = asyncio.run(_fetch_page_content(
                    url=detail_url,
                    wait_selector=config.POST_TEXT_SELECTOR
                ))
                if detail_html:
                    detail_soup = BeautifulSoup(detail_html, "html.parser")
                    post_elements = detail_soup.select(config.POST_TEXT_SELECTOR)
                    related_posts = [p.text.strip() for p in post_elements[:5]]

            # 最終的なデータオブジェクトを作成
            raw_trends.append(RawTrendItem(
                title=title,
                posts_num=posts_num,
                detail_url=detail_url,
                related_posts=related_posts
            ))
            
        except (AttributeError, ValueError, TypeError, ValidationError) as e:
            print(f"[WARNING][scraper] Skipping an item due to a parsing error: {e}")
            continue
    
    print(f"[INFO][scraper] Successfully scraped {len(raw_trends)} trends.")
    return raw_trends

# このファイルが直接実行された場合のテスト用
if __name__ == '__main__':
    trends = fetch_raw_trends()
    if trends:
        print("\n--- Scraping Test Result ---")
        for trend in trends[:3]:
            print(f"Title: {trend.title}")
            print(f"Posts: {trend.posts_num}")
            print(f"URL: {trend.detail_url}")
            print(f"Related Posts Count: {len(trend.related_posts)}")
            print("-" * 20)
    else:
        print("\n--- Scraping Test Failed ---")