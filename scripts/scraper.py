# scripts/scraper.py
"""
VIBRAトレンドスクレイパー (Full Selenium版)
一覧ページだけでなく詳細ページもSeleniumで取得することで、
JavaScript生成コンテンツ（関連ポスト等）を確実に取得する。
"""
import time
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

# Pydanticモデルを使い、スクレイピングデータの型と構造を保証する
class ScrapedItem(BaseModel):
    title: str
    posts_num: int
    detail_url: HttpUrl

def fetch_raw_trends() -> List[RawTrendItem]:
    """
    SeleniumでJavaScriptレンダリング後のHTMLを取得し、
    トレンドデータを抽出してRawTrendItemのリストを返す。
    詳細ページもSeleniumで巡回する。
    """
    print("[INFO][scraper] Starting fetch_raw_trends with Full Selenium...")
    
    # --- Selenium WebDriverのセットアップ ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # ブラウザUIを表示しないヘッドレスモード
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f'user-agent={config.REQUEST_HEADERS["User-Agent"]}')
    
    driver = None
    raw_trends: List[RawTrendItem] = []

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 1. 一覧ページ取得
        print(f"[INFO][scraper] Navigating to List Page: {config.DATA_SOURCE_URL}...")
        driver.get(config.DATA_SOURCE_URL)

        print(f"[INFO][scraper] Waiting for selector '{config.TREND_SELECTORS[0]}'...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, config.TREND_SELECTORS[0]))
        )
        
        # 一覧ページの解析
        list_html = driver.page_source
        soup = BeautifulSoup(list_html, "html.parser")
        trend_elements = soup.select(config.TREND_SELECTORS[0])
        
        if not trend_elements:
            print("[WARNING][scraper] No trend elements found. CSS selector might be outdated.")
            return []

        # 一時リスト作成（詳細URL取得のため）
        temp_items = []
        for element in trend_elements:
            try:
                title = element.select_one(config.TITLE_SELECTOR).text.strip()
                posts_num_text = element.select_one(config.POSTS_COUNT_SELECTOR).text
                posts_num = int(posts_num_text.replace("件のポスト", "").replace(",", "").strip())
                
                raw_url = element.select_one(config.DETAIL_URL_SELECTOR)['href']
                detail_url = f"https://search.yahoo.co.jp{raw_url}" if raw_url.startswith('/') else raw_url
                
                temp_items.append({
                    "title": title,
                    "posts_num": posts_num,
                    "detail_url": detail_url
                })
            except Exception as e:
                continue

        # 2. 詳細ページ巡回 (上位N件のみ)
        print(f"[INFO][scraper] Found {len(temp_items)} items. Fetching details for top {config.ANALYZE_TREND_COUNT}...")
        
        for i, item in enumerate(temp_items):
            related_posts = []
            
            # 上位件数のみ詳細取得
            if i < config.ANALYZE_TREND_COUNT:
                try:
                    print(f"  [{i+1}/{config.ANALYZE_TREND_COUNT}] Visiting {item['title']}...")
                    driver.get(item['detail_url'])
                    
                    # 投稿本文が表示されるまで待機 (少し短めのタイムアウトで)
                    try:
                        WebDriverWait(driver, 8).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, config.POST_TEXT_SELECTOR))
                        )
                    except:
                        # タイムアウトしてもHTMLは解析してみる
                        pass
                    
                    detail_soup = BeautifulSoup(driver.page_source, "html.parser")
                    post_elements = detail_soup.select(config.POST_TEXT_SELECTOR)
                    related_posts = [p.text.strip() for p in post_elements[:5]]
                    
                except Exception as e:
                    print(f"  [WARN] Failed to fetch details for {item['title']}: {e}")
            
            # RawTrendItem生成
            raw_trends.append(RawTrendItem(
                title=item['title'],
                posts_num=item['posts_num'],
                detail_url=item['detail_url'],
                related_posts=related_posts
            ))
            
            # サーバー負荷軽減のため少し待つ
            time.sleep(1)

    except Exception as e:
        print(f"[CRITICAL][scraper] Selenium Error: {e}")
    finally:
        if driver:
            driver.quit()

    print(f"[INFO][scraper] Successfully scraped {len(raw_trends)} trends with details.")
    return raw_trends

if __name__ == '__main__':
    # Test run
    trends = fetch_raw_trends()
    for t in trends[:3]:
        print(f"Title: {t.title}")
        print(f"Related Posts: {len(t.related_posts)}")