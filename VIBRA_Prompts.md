# VIBRA Prompts

Based on the templates provided in `input.txt` and specifications in `AntigravityVIBRA.md`.

## 1. UI Design Prompt (Main Dashboard)

**Role**
You are a senior UI/UX Designer with a strong portfolio in minimalist and data-driven interfaces. Your primary tool is an AI-powered design generator that can create high-fidelity mockups from text descriptions.

**Task**
Generate a UI design concept for **Main Dashboard (Top Page)** for our project "VIBRA". Adhere strictly to the following design system and constraints.

**Design System & Constraints:**
*   **Project Name:** VIBRA
*   **Core Philosophy:** Ultra-minimalist, typography-driven, no images/icons.
*   **Color Palette:**
    *   Background: White (`#FFFFFF`)
    *   Primary Text: Dark Gray (`#374151`)
    *   Accent - Hot: Red (`#ef4444`)
    *   Accent - Medium: Orange (`#f59e0b`)
    *   Accent - Watermark: Extremely faint gray (`rgba(0,0,0,0.02)`)
*   **Typography:**
    *   Body/UI Font: A clean, sans-serif Japanese Gothic font.
    *   Hero/Highlight Font: An elegant, strong serif Japanese Mincho font.

**Component Specification: Main Dashboard (Top Page)**
*   **Layout:** Single-page application style. Centered focus on the top trend, with other trends floating around it.
*   **Content Elements:**
    *   Background: Large, faint "Buzz Meter" watermark text.
    *   Header: Simple text-based navigation tabs for genres ("総合", "エンタメ", etc.).
    *   Center (Hero): The #1 ranking trend keyword. Large font size.
    *   Surroundings: A tag cloud of other trend keywords. Sizes proportional to rank.
    *   Footer: Copyright year and text-only links for SNS shares (X, TikTok, Threads).
*   **Styling Details:**
    *   The Hero Trend should use the **Hero/Highlight Font** and have a subtle "pulse" animation.
    *   Tag cloud items should use the **Body/UI Font**.
    *   Tag colors should reflect "Heat Level": Red for high score, Orange for medium, Gray for low.
*   **Interactivity Hint:**
    *   Hero trend pulses rhythmically.
    *   Tags hover effect: slight opacity change or scale.

---

## 2. CI/CD Code Prompt (Fetcher Workflow)

**Role**
You are a Senior DevOps Engineer and Full-Stack Developer. Your task is to generate clean, production-ready boilerplate code based on specific technical requirements.

**Task**
Generate the complete code for the file `.github/workflows/fetcher.yml` for a **GitHub Actions** project.

**Technical Requirements:**
*   **Project Type:** GitHub Actions workflow.
*   **Functionality:**
    *   **Trigger:** Runs on a 15-minute schedule (cron `*/15 * * * *`).
    *   **Steps:**
        1.  Checkout the repository.
        2.  Set up Python 3.10.
        3.  Install dependencies from `requirements.txt`.
        4.  Run the data pipeline script `src/main.py`.
        5.  Commit the generated `cache/latest_trends.json` file.
        6.  **Crucial:** Force-push this commit to a dedicated orphan branch named `cache-branch` to keep the main history clean.
*   **Coding Standards:**
    *   Use standard GitHub Actions syntax.
    *   Include comments explaining the force-push strategy.

---

## 3. UX Design Prompt (Micro-interactions)

**Role**
You are a Principal UX Designer at Google, known for your ability to refine minimalist interfaces into delightful experiences.

**Context**
We are designing "VIBRA", a minimalist trend visualization site. The core UI is a tag cloud with a central, pulsating keyword. When a keyword is clicked, a modal appears with details like co-occurring words and a score trend graph.

**Task**
The current design is functional but static. Propose **3 subtle, yet powerful, micro-interactions or animations** that would enhance the user's perception of "liveness" and "data flow" without cluttering the interface.

For each proposal, describe:
1.  **The Interaction/Animation:** What happens visually?
2.  **The Trigger:** What user action or data change causes it?
3.  **The "Why":** How does this small detail improve the user experience or reinforce the "VIBRA Flow" concept?

---

## 4. Product Strategy Prompt (Feature & Monetization)

**Role**
You are a visionary Product Strategist at a leading data intelligence company.

**Context**
Our product, "VIBRA", successfully visualizes real-time trends from public data sources. Our current business model relies on ads and affiliate links. We operate on a zero-cost, fully automated infrastructure.

**Task**
Our goal is to evolve from a simple "visualization tool" into an indispensable "trend discovery engine".
Brainstorm **3 strategic new features** that would significantly increase VIBRA's value proposition for users and create new, non-intrusive monetization opportunities.

For each feature, explain:
1.  **Feature Concept:** What is the core idea?
2.  **Target User:** Who would benefit most from this feature? (e.g., marketers, journalists, casual users)
3.  **Data Requirements:** What new data would we need to acquire or analyze?
4.  **Monetization Angle:** How can we monetize this feature without resorting to intrusive banner ads? (e.g., premium data export, sponsored trend analysis)

---

## 5. Red Team Analysis Prompt (Critical Review)

**Role**
You are a highly critical but fair Principal Software Architect and a competing product's lead. You have just analyzed our project, "VIBRA".

**Context**
"VIBRA" is a fully automated, GitHub-native trend visualization site. It scrapes public data, performs co-occurrence analysis, and displays it in a minimalist tag cloud. Its strengths are its zero cost and simple, clean UI.

**Task**
Perform a critical "Red Team" analysis.
1.  Identify the **top 2 potential weaknesses or blind spots** in VIBRA's current architecture and user experience. What fundamental aspect are we overlooking?
2.  For each weakness you identified, propose a **creative and technically feasible solution** that not only mitigates the weakness but also turns it into a unique, competitive advantage.

---

## 6. Technical Prompt (Personalization w/o Login)

**Role**
You are a Lead AI/ML Engineer at Spotify, specializing in content personalization and recommendation engines.

**Context**
Our product, "VIBRA", is a minimalist trend visualization site. It currently shows the same global trends to all users. Our architecture is serverless and we want to avoid complex user account systems if possible.

**Task**
Propose **2 technically feasible ideas** to introduce **"Personalization"** to VIBRA without requiring a full-blown user login system. The goal is to make the experience more relevant to each individual user.

For each idea, explain:
1.  **Concept:** How does it work from the user's perspective?
2.  **Technical Implementation:** How can we achieve this using lightweight, client-side technologies like **LocalStorage** or browser fingerprinting?
3.  **User Benefit:** Why is a personalized trend feed more valuable?
4.  **Privacy Consideration:** What are the privacy implications, and how can we mitigate them?

---

## 7. Product Feature Prompt (Community Context)

**Role**
You are the Head of Product for Reddit. You are an expert in fostering community engagement and user-generated content while maintaining a simple interface.

**Context**
"VIBRA" visualizes trends, but it doesn't explain *why* they are trending. The "co-occurring words" feature helps, but it lacks a human touch.

**Task**
Brainstorm **2 minimalist, non-intrusive features** that would allow the community to add context or "social proof" to the trends. We want to avoid a full-fledged comment section.

For each feature, describe:
1.  **Feature Name & Concept:** What is it and how does it work?
2.  **UI Implementation:** How would this look on our minimalist UI without cluttering it?
3.  **Moderation Strategy:** How do we prevent spam or low-quality contributions in an automated, zero-cost environment?

---

## 8. Data Strategy Prompt (Historical Data Monetization)

**Role**
You are a Data Monetization Strategist and the founder of Google Trends.

**Context**
Our project, "VIBRA", generates a new `latest_trends.json` file every hour, overwriting the old one. We are essentially throwing away valuable historical data. Our infrastructure is zero-cost.

**Task**
Propose **2 creative and feasible strategies** to leverage this historical trend data to create new value for users or generate revenue, without incurring significant server costs.

For each strategy, explain:
1.  **Concept:** What new product or feature can we build from the historical data?
2.  **Technical Feasibility (on GitHub):** How can we store and access potentially large amounts of historical data within the constraints of a GitHub repository? (Think about yearly archives, Git LFS, etc.)
3.  **Value Proposition:** Who would find this valuable and why?

---

## 9. Technical Task Prompt (Trend Scoring Implementation)

**Role**
You are a Senior Data Scientist and Python Developer. You specialize in creating robust, maintainable, and well-tested data processing logic.

**Task**
Implement the trend scoring algorithm for the "VIBRA" project. This involves modifying the `enricher.py` script and the `.github/workflows/fetcher.yml` file to calculate a dynamic Score and velocity-based heatLevel for each trend.

The `fetcher.yml` workflow needs two new steps using the `actions/cache@v4` action.

### .github/workflows/fetcher.yml

```yaml
# ... (name, on, jobs, steps...)
      - name: Setup Python
        # ...

      - name: 📥 Restore previous scores cache
        id: scores-cache-restore
        uses: actions/cache/restore@v4
        with:
          path: cache/previous_scores.json
          key: scores-cache-v1

      - name: 🐍 Run Data Pipeline
        run: python scripts/main.py
      
      - name: 💾 Save current scores to cache
        id: scores-cache-save
        uses: actions/cache/save@v4
        with:
          path: cache/scores_to_cache.json # The Python script will generate this file
          key: ${{ steps.scores-cache-restore.outputs.cache-key || format('scores-cache-v1-{0}', github.run_id) }}
      
      - name: 🚀 Commit and Push Trend Data
        # ... (Commit cache/latest_trends.json to cache-branch)
```

Modify the `enrich_trends` function in `enricher.py`.

### scripts/enricher.py

```python
import json
import math
import os
from typing import List, Dict
# ... (other imports)

# --- 1. 定数と重みの定義 ---
# これらの値は、今後チューニングする可能性がある
W1_RANK = 0.4
W2_POSTS = 0.3
W3_VELOCITY = 0.3
VELOCITY_THRESHOLD_HIGH = 20 # スコアが20以上増加したら 'high'

# --- 2. 前回のスコアを読み込むヘルパー関数 ---
def _load_previous_scores() -> Dict[str, int]:
    """GitHub Actions Cacheから復元された前回のスコアデータを読み込む"""
    path = 'cache/previous_scores.json'
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

# --- 3. enrich_trends 関数の改修 ---
def enrich_trends(analyzed_trends: List[AnalyzedTrendItem]) -> List[EnrichedTrendItem]:
    """分析済みデータに、動的なスコアとheatLevelを付与する"""
    if not analyzed_trends:
        return []

    previous_scores = _load_previous_scores()
    current_scores: Dict[str, int] = {}
    enriched_list: List[EnrichedTrendItem] = []
    
    max_posts_num = max([t.posts_num for t in analyzed_trends] or [1])
    total_trends = len(analyzed_trends)

    for i, trend in enumerate(analyzed_trends):
        # --- 各指標の正規化 (0-100) ---
        rank_metric = (1 - (i / total_trends)) * 100
        post_volume_metric = (math.log1p(trend.posts_num) / math.log1p(max_posts_num)) * 100
        
        previous_score = previous_scores.get(trend.title, 0)
        # velocityはスコアの単純な差分とする
        velocity_metric = max(0, 100 - previous_score) # 新規トレンドは高いvelocityを持つ

        # --- 最終スコアの計算 ---
        score = int(
            W1_RANK * rank_metric +
            W2_POSTS * post_volume_metric +
            W3_VELOCITY * velocity_metric
        )
        score = min(100, max(0, score))
        current_scores[trend.title] = score

        # --- velocityに基づくheatLevelの決定 ---
        velocity = score - previous_score
        if velocity >= VELOCITY_THRESHOLD_HIGH and score > 50:
            heatLevel = 'high'
        elif score > 60:
            heatLevel = 'medium'
        else:
            heatLevel = 'low'
            
        # ... (リンク生成ロジックは変更なし) ...
        
        enriched_list.append(EnrichedTrendItem(
            title=trend.title,
            posts_num=trend.posts_num,
            score=score,
            heatLevel=heatLevel,
            # ... (他のフィールド)
        ))

    # --- 4. 次回実行のために現在のスコアをファイルに保存 ---
    if not os.path.exists('cache'):
        os.makedirs('cache')
    with open('cache/scores_to_cache.json', 'w', encoding='utf-8') as f:
        json.dump(current_scores, f, ensure_ascii=False, indent=2)

    return enriched_list
```

---

## 10. Creative Prompt (Data Visualization)

**Role**
You are an award-winning Data Artist and Interactive Designer, famous for turning cold data into emotional, narrative experiences.

**Context**
Our project, "VIBRA", visualizes trends in a minimalist tag cloud. We have a "score" (importance) and a "heatLevel" (momentum). The UI is clean, but perhaps too sterile.

**Task**
Propose **2 innovative data visualization ideas** that can be implemented in a minimalist, text-only environment to add an "emotional" or "narrative" layer to the user experience.

For each idea, describe:
1.  **Visualization Concept:** What is the core visual idea?
2.  **Data Mapping:** Which data points (`score`, `heatLevel`, `co-occurring_words`, `historical_data`) does it use?
3.  **User Insight:** What new story or insight does this visualization tell the user that the current design cannot? (e.g., "It shows the 'before and after' of a trend," "It reveals the controversy behind a topic.")
4.  **Technical Feasibility:** Can this be achieved with CSS animations and/or lightweight JavaScript (like D3.js)?

---

## 11. Strategy Prompt (Ecosystem & API)

**Role**
You are a Head of Platform and API Strategy at a major tech company like Twitter or Google.

**Context**
"VIBRA" is a fully automated system that generates a `trends.json` file every hour. This JSON file is currently only used to build our own website.

**Task**
This `trends.json` is a valuable asset. Brainstorm **2 strategic ways** to leverage this data asset to create an "ecosystem" around VIBRA, generating new revenue streams beyond our own website's ads.

For each strategy, describe:
1.  **Product Concept:** What is the new product or service? (e.g., "A public API," "A browser extension," "A newsletter").
2.  **Target Audience:** Who would pay for or use this new product?
3.  **Business Model:** How does it generate revenue? (e.g., API subscription, one-time purchase, referral fees).
4.  **Technical Architecture:** How can we build this on top of our existing zero-cost, GitHub-native infrastructure?
