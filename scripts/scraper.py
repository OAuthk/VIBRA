# scripts/scraper.py
"""
VIBRAトレンドスクレイパー (Selenium版)
JavaScriptで動的に生成されるコンテンツに対応する、安定志向の実装。
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import List
import config
from models import RawTrendItem
from pydantic import BaseModel, ValidationError, HttpUrl
import requests # 詳細ページ取得用にrequestsもインポート

# Pydanticモデルを使い、スクレイピングデータの型と構造を保証する
class ScrapedItem(BaseModel):
    title: str
    posts_num: int
    detail_url: HttpUrl

def fetch_raw_trends() -> List[RawTrendItem]:
    """
    SeleniumでJavaScriptレンダリング後のHTMLを取得し、
    トレンドデータを抽出してRawTrendItemのリストを返す。
    """
    print("[INFO][scraper] Starting fetch_raw_trends with Selenium...")
    
    # --- Selenium WebDriverのセットアップ ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # ブラウザUIを表示しないヘッドレスモード
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f'user-agent={config.REQUEST_HEADERS["User-Agent"]}')
    
    html = ""
    driver = None
    try:
        # webdriver-managerが、実行環境に適したChromeドライバを自動でダウンロード・管理してくれる
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print(f"[INFO][scraper:selenium] Navigating to {config.DATA_SOURCE_URL}...")
        driver.get(config.DATA_SOURCE_URL)

        # ★ 核心部分: 指定されたCSSセレクタの要素が表示されるまで最大20秒待機
        print(f"[INFO][scraper:selenium] Waiting for selector '{config.TREND_SELECTORS[0]}'...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, config.TREND_SELECTORS[0]))
        )
        
        print("[INFO][scraper:selenium] Page rendered. Getting content...")
        html = driver.page_source

    except Exception as e:
        print(f"[CRITICAL][scraper] Failed to get HTML content with Selenium. Error: {e}")
        return []
    finally:
        # 必ずブラウザを閉じる
        if driver:
            driver.quit()

    if not html:
        print("[CRITICAL][scraper] HTML content is empty after Selenium run. Exiting.")
        return []

    # --- BeautifulSoupを使ったHTML解析 ---
    soup = BeautifulSoup(html, "html.parser")
    trend_elements = soup.select(config.TREND_SELECTORS[0])
    
    if not trend_elements:
        print("[WARNING][scraper] No trend elements found in Selenium-rendered HTML. CSS selector might be outdated.")
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
                related_posts = _fetch_related_posts_with_requests(detail_url)

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


def _fetch_related_posts_with_requests(url: str) -> List[str]:
    """【暫定対応】詳細ページはrequestsで取得を試みるヘルパー関数。"""
    try:
        print(f"[INFO][scraper:requests] Fetching details for {url}...")
        response = requests.get(url, headers=config.REQUEST_HEADERS, timeout=config.REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        post_elements = soup.select(config.POST_TEXT_SELECTOR)
        return [p.text.strip() for p in post_elements[:5]]
    except Exception as e:
        print(f"[WARNING][scraper:requests] Failed to fetch related posts with requests from {url}: {e}")
        return []

if __name__ == '__main__':
    # このファイルが直接実行された場合のテスト用ロジック
    trends = fetch_raw_trends()
    if trends:
        print("\n--- Scraping Test Result (Selenium) ---")
        for trend in trends[:3]:
            print(f"Title: {trend.title}")
            print(f"Posts: {trend.posts_num}")
            print(f"URL: {trend.detail_url}")
            print(f"Related Posts Count: {len(trend.related_posts)}")
            print("-" * 20)
    else:
        print("\n--- Scraping Test Failed ---")