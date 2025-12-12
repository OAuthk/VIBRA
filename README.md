# VIBRA - Living Cloud

リアルタイムトレンドを美しく可視化するダッシュボード

## 🚀 概要

VIBRAは、Yahoo!リアルタイム検索からトレンドデータを収集し、D3.jsを使ったインタラクティブなバブルチャートで可視化するWebアプリケーションです。

## ✨ 機能

- **リアルタイムトレンド取得** - 15分ごとに自動更新
- **インタラクティブ可視化** - D3.jsバブルチャート
- **カテゴリフィルタリング** - テクノロジー/エンタメ/ビジネス等
- **自動カテゴリ分類** - キーワードマッチング
- **トレンドクラスタリング** - Louvain法によるグループ化

## 🛠️ 技術スタック

- **フロントエンド**: HTML, CSS, JavaScript, D3.js
- **バックエンド**: Python (BeautifulSoup, Jinja2, NetworkX)
- **インフラ**: GitHub Actions, GitHub Pages

## 📁 構成

```
VIBRA/
├── .github/workflows/    # CI/CDパイプライン
├── src/                  # Pythonソースコード
├── static/               # CSS/JS
├── templates/            # HTMLテンプレート
└── requirements.txt
```

## 🔧 セットアップ

```bash
pip install -r requirements.txt
```

## 📝 ライセンス

MIT License
