Antigravity用 マスタープロンプト：プロジェクトVIBRAの完全構築
タスク名:
Create a fully automated, serverless trend visualization website: "VIBRA"
タスク説明 (Instructions):
You are an expert full-stack development team composed of multiple AI agents. Your mission is to build a complete web application named "VIBRA" based on the following detailed specifications. The project must be fully automated and operate at zero cost, leveraging a GitHub-native architecture.
Phase 1: Backend Data Pipeline (Python)
Objective: Create a Python-based data pipeline that runs automatically on a schedule using GitHub Actions.
Architecture:
Data Source: Scrape the trend summary page at https://search.yahoo.co.jp/realtime/search/matome.
Technology: Use requests for HTTP calls and BeautifulSoup4 for HTML parsing.
Data Flow: Implement a Scraper -> Analyzer -> Enricher pipeline.
Module Specifications:
scraper.py:
Fetch the list of trends from the data source URL.
For the top 5 trends, also fetch their respective detail pages to extract related post texts for analysis.
analyzer.py:
Implement a co-occurrence analysis function.
Use the janome library for Japanese morphological analysis.
Extract the top 3 co-occurring nouns from the related post texts for each of the top trends.
enricher.py:
Calculate a score (0-100) and heatLevel ('high', 'medium', 'low') for each trend.
Generate a google_search_url for each trend to mask the data source.
Generate a Mercari affiliate link for each trend using an environment variable MERCARI_AFFILIATE_ID.
Output:
The final output of this pipeline is a single JSON file named latest_trends.json.
This JSON file must be saved to a cache/ directory within the repository.
Phase 2: CI/CD and Automation (GitHub Actions)
Objective: Automate the entire process from data fetching to deployment.
Workflow 1: fetcher.yml
Trigger: Runs on a 15-minute schedule (cron).
Steps:
Execute the Python data pipeline from Phase 1.
Commit the generated cache/latest_trends.json file.
Crucially, push this commit to a dedicated, orphaned branch named cache-branch using --force. This is to keep the main branch history clean.
Workflow 2: deploy.yml
Trigger: Runs on a 1-hour schedule (cron) and on push to the main branch.
Steps:
Check out the main branch.
Separately, check out the latest_trends.json file from the cache-branch.
Using Python with the Jinja2 library, generate a static index.html file by rendering the JSON data into the templates/layout.html template.
Deploy the generated dist/ directory (containing index.html, css, js) to GitHub Pages.
Phase 3: Frontend (Static HTML & CSS)
Objective: Create a minimalist, typography-driven UI based on the provided design concept.
Design Principles:
No images or icons. The entire UI must be constructed with text and CSS only.
The background is white.
A very faint "Buzz Meter" watermark text should be in the background.
templates/layout.html Specification:
The page must be rendered using data from the latest_trends.json.
The trend with the highest score should be displayed in the center with a large serif font and a "pulse" animation.
Other trends should be displayed around it in a tag cloud format. Font size should be proportional to the score, and color should be determined by the heatLevel.
Implement genre tabs ("総合", "エンタメ", etc.). For this initial task, the tabs can be static UI elements; filtering logic is not required yet.
The footer must contain automatically updated copyright year and SNS share buttons (X, TikTok, Threads) styled with CSS.
Secret Management:
The pipeline must use GitHub Actions Secrets for GA4_TRACKING_ID and MERCARI_AFFILIATE_ID. The Python scripts should read these values from environment variables.
Please generate an implementation_plan.md first. I will review it before you proceed with the coding.