# src/category_classifier.py
"""
VIBRAトレンドカテゴリ分類モジュール
初期実装はキーワード辞書マッチング戦略を採用
将来的にMLモデルへの置き換えを想定した設計
"""
from typing import Dict, List

from models import AnalyzedTrendItem


# カテゴリごとのキーワード辞書
# キーワードを追加することで分類精度を向上可能
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    'entertainment': [
        'アニメ', '映画', 'ドラマ', 'ゲーム', '声優', 'YouTube', 'VTuber',
        '配信', 'コラボ', 'グッズ', 'ライブ', 'コンサート', 'アイドル',
        '漫画', 'マンガ', 'ジャンプ', 'Netflix', 'ディズニー', '歌手',
        '舞台', '放送', '上映', 'PV', '解禁', '新作', '連載', '最終回',
        'ポケモン', 'ウマ娘', 'プリキュア', 'ガンダム', '特撮', 'ライダー',
        'バンド', 'アルバム', 'MV', 'フェス', 'コミケ', 'コスプレ'
    ],
    'business': [
        '株', '円安', '日銀', '決算', '投資', '経済', '上場', '買収',
        '業績', 'IPO', 'スタートアップ', '企業', '倒産', '株価', '利益',
        '市場', '金融', '為替', 'ドル', '銀行', 'インフレ', '賃上げ',
        '増税', 'GDP', '景気', 'マーケティング', '広告', '発売',
        '価格', '値上げ', '値下げ', 'キャンペーン', 'NISA'
    ],
    'sports': [
        '野球', 'サッカー', 'オリンピック', '大谷', '優勝', '試合',
        '選手', 'J1', 'プロ野球', 'WBC', 'ワールドカップ', 'NBA',
        'テニス', 'ゴルフ', 'ボクシング', '格闘', '相撲', 'マラソン',
        '代表', 'ゴール', 'ホームラン', 'ドラフト', '移籍', '監督',
        '甲子園', '高校野球', 'フィギュア', '駅伝', 'ラグビー'
    ],
    'technology': [
        'AI', 'プログラミング', 'Python', 'アプリ', 'iPhone', 'Google',
        'サーバー', 'クラウド', 'API', 'ChatGPT', 'OpenAI', 'Meta',
        'Microsoft', 'Amazon', 'スマホ', 'Android', 'PC', 'パソコン',
        'エンジニア', 'ソフトウェア', 'データ', 'セキュリティ',
        'Apple', 'Mac', 'Windows', 'Linux', '開発', '実装', 'バグ',
        'X', 'Twitter', 'イーロン', 'SNS', '脆弱性', 'サイバー'
    ],
    'politics': [
        '政治', '選挙', '事件', '地震', '速報', '逮捕', '首相', '大臣',
        '裁判', '判決', '法案', '国会', '与党', '野党', '政府', '外交',
        '条例', '自民党', '立憲', '総理', '内閣', '支持率', '知事',
        '県警', '容疑', '事故', '火事', '災害', '警報', '震度',
        'ミサイル', '防衛', '外交'
    ]
}


def classify_category(trend: AnalyzedTrendItem) -> str:
    """
    キーワードマッチングでトレンドのカテゴリを判定する。
    
    Args:
        trend: 分析済みのトレンドデータオブジェクト
        
    Returns:
        str: 分類されたカテゴリ名（例: 'entertainment'）。
             合致しない場合は 'all'（総合）。
    """
    # タイトルと共起語を分析対象のテキストとする
    # 共起語がある場合は重みを増やす
    text_features = [trend.title * 2] + list(trend.co_occurring_words)
    text_to_check = ' '.join(text_features).lower()
    
    # 各カテゴリのスコアを計算
    scores: Dict[str, int] = {category: 0 for category in CATEGORY_KEYWORDS}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_to_check:
                scores[category] += 1
    
    # 最もスコアが高かったカテゴリを返す
    if any(s > 0 for s in scores.values()):
        max_score_category = max(scores, key=scores.get)
        # フロントエンドの互換性のため、politicsなどはbusiness(ニュース)かallにマッピング
        # ここでは単純に文字列を帰すが、後段のマッピングで処理されることを期待
        return max_score_category
    
    # どのカテゴリにもマッチしなかった場合は 'all' (総合) とする
    return 'all'
