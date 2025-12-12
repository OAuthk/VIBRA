# src/main.py
"""
VIBRAフェッチャーパイプライン
型安全なデータフローを実装
"""
import sys
import json
import os
from typing import List

import scraper
import analyzer
import enricher
from models import RawTrendItem, AnalyzedTrendItem, EnrichedTrendItem


def run_fetcher_pipeline():
    """型安全なdataclassを使用したデータパイプラインを実行"""
    print("[INFO] Starting FETCHER pipeline...")
    
    # 1. Scrape: List[RawTrendItem]を取得
    print("Fetching trends...")
    raw_trend_items: List[RawTrendItem] = scraper.fetch_raw_trends()
    if not raw_trend_items:
        print("[CRITICAL] No raw trends acquired. Halting.", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] Fetched {len(raw_trend_items)} trends.")
    
    # 2. Analyze: List[RawTrendItem] → List[AnalyzedTrendItem]
    print("Analyzing trends...")
    analyzed_trends: List[AnalyzedTrendItem] = analyzer.analyze_trends(raw_trend_items)
    
    # 3. Enrich: List[AnalyzedTrendItem] → List[EnrichedTrendItem]
    print("Enriching data...")
    enriched_trends: List[EnrichedTrendItem] = enricher.enrich_trends(analyzed_trends)
    
    # 4. Save to cache（最終シリアライズ時のみdict変換）
    output_dir = "cache"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "latest_trends.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(
            [item.to_dict() for item in enriched_trends],
            f,
            ensure_ascii=False,
            indent=2
        )
        
    print(f"[INFO] FETCHER pipeline complete. Saved data to {output_path}")


if __name__ == "__main__":
    run_fetcher_pipeline()
