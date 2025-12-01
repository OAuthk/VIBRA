# Data-Driven Visualization Strategies for VIBRA

This document outlines two distinct technical strategies for implementing data-driven connection visualization in VIBRA, moving away from static categories to objective, calculated relationships.

---

## Strategy 1: The Weighted Graph Strategy (PMI)

This strategy visualizes the strength of the relationship between individual keyword pairs using **Pointwise Mutual Information (PMI)**.

### Backend (`src/analyzer.py`)

**Algorithm Choice:**
We will use **PMI** to calculate a "connection score". PMI measures how much more likely two words are to co-occur than if they were independent.
Formula: `PMI(x, y) = log2( p(x, y) / (p(x) * p(y)) )`

**Implementation Steps:**
1.  **Calculate Probabilities:**
    *   `p(word)`: Frequency of `word` appearing in the total set of trends / Total number of trends.
    *   `p(word1, word2)`: Frequency of `word1` and `word2` appearing together (e.g., in `related_queries` or `related_nouns`) / Total number of trends.
2.  **Sparsity Handling:**
    *   If `p(x, y)` is 0 (never co-occur), PMI is undefined (-infinity). We will treat this as a score of 0 or exclude the connection.
    *   We will use **Positive PMI (PPMI)**, where `max(PMI, 0)`, to focus only on positive associations.

**Code Snippet:**

```python
import math
from collections import defaultdict
from typing import List, Dict, Tuple

def calculate_pmi_scores(raw_trends: List[Dict]) -> List[Dict]:
    """
    Calculates PPMI scores for co-occurring words.
    Returns a list of connections: [{'source': 'word1', 'target': 'word2', 'score': 1.5}, ...]
    """
    word_counts = defaultdict(int)
    co_occurrence_counts = defaultdict(int)
    total_docs = len(raw_trends)
    
    # 1. Count occurrences
    for trend in raw_trends:
        main_word = trend['keyword']
        word_counts[main_word] += 1
        
        # Assuming 'related_nouns' is a list of co-occurring words
        related_words = trend.get('related_nouns', [])
        for related in related_words:
            word_counts[related] += 1
            # Sort to ensure (A, B) is same as (B, A)
            pair = tuple(sorted((main_word, related)))
            co_occurrence_counts[pair] += 1

    connections = []
    
    # 2. Calculate PMI
    for (w1, w2), count in co_occurrence_counts.items():
        p_x_y = count / total_docs
        p_x = word_counts[w1] / total_docs
        p_y = word_counts[w2] / total_docs
        
        if p_x * p_y > 0:
            pmi = math.log2(p_x_y / (p_x * p_y))
            ppmi = max(pmi, 0) # Use Positive PMI
            
            # Threshold to reduce noise (optional)
            if ppmi > 0.5:
                connections.append({
                    "source": w1,
                    "target": w2,
                    "score": round(ppmi, 3)
                })
                
    return connections
```

### Frontend (`static/js/main.js`)

**Data Mapping:**
*   **PMI Score** -> **Stroke Width** & **Opacity**
*   Higher score = Thicker, darker line.

**Implementation Steps:**
1.  **Scale Function:** Use `d3.scaleLinear` to map the PMI score range (e.g., 0.5 to 5.0) to visual properties.
2.  **Filtering:**
    *   **Approach:** Draw *all* lines with positive scores but use opacity to fade out weak ones. This creates a "web" effect where strong connections pop out naturally without a harsh cutoff.

**Code Snippet:**

```javascript
function drawConnections(connections) {
    // 1. Define Scales
    const maxScore = d3.max(connections, d => d.score) || 1;
    
    const opacityScale = d3.scaleLinear()
        .domain([0.5, maxScore])
        .range([0.1, 0.8]) // Weak lines are faint, strong are clear
        .clamp(true);

    const widthScale = d3.scaleLinear()
        .domain([0.5, maxScore])
        .range([0.5, 3]) // Thickness from 0.5px to 3px
        .clamp(true);

    // 2. Draw Lines (Insert before nodes so they are behind text)
    const linkElements = svg.append("g")
        .attr("class", "connections")
        .selectAll("line")
        .data(connections)
        .enter()
        .append("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", d => opacityScale(d.score))
        .attr("stroke-width", d => widthScale(d.score));
        
    // Note: You'll need to update x1, y1, x2, y2 in the simulation 'tick' handler
    // by looking up the source/target node coordinates.
}
```

---

## Strategy 2: The Clustering Strategy (Community Detection)

This strategy treats the trends as a network and automatically groups them into "communities" or clusters based on their density of connections.

### Backend (`src/analyzer.py`)

**Algorithm Choice:**
We will use the **Louvain Method** for community detection. It is fast, efficient, and works well for finding modular structures in graphs.

**Implementation Steps:**
1.  **Library:** `networkx` is excellent for graph manipulation, and `python-louvain` (imported as `community`) is the standard for Louvain clustering.
2.  **Graph Construction:** Create a graph where nodes are keywords and edges are weighted by co-occurrence count (or PMI).
3.  **Detection:** Run `community.best_partition(G)`.

**Code Snippet:**

```python
import networkx as nx
import community.community_louvain as community_louvain # pip install python-louvain
from collections import defaultdict

def detect_trend_clusters(raw_trends: List[Dict]) -> Dict[str, int]:
    """
    Detects communities using Louvain method.
    Returns: {'keyword1': 0, 'keyword2': 0, 'keyword3': 1, ...}
    """
    G = nx.Graph()
    
    # 1. Build Graph
    for trend in raw_trends:
        main_word = trend['keyword']
        G.add_node(main_word)
        
        related_words = trend.get('related_nouns', [])
        for related in related_words:
            if related: # Ensure not empty
                # Add edge with weight 1 (or increment if exists)
                if G.has_edge(main_word, related):
                    G[main_word][related]['weight'] += 1
                else:
                    G.add_edge(main_word, related, weight=1)
    
    # 2. Run Louvain Algorithm
    # resolution parameter controls cluster size (higher = smaller clusters)
    partition = community_louvain.best_partition(G, resolution=1.0)
    
    return partition # {node: cluster_id}
```

### Frontend (`static/js/main.js`)

**Data Mapping:**
*   **Cluster ID** -> **Color**
*   Keywords in the same cluster share the same color.
*   Lines are drawn between all nodes in the same cluster (or just the MST/strongest links within the cluster).

**Implementation Steps:**
1.  **Color Scale:** Use `d3.scaleOrdinal(d3.schemeCategory10)` (or a custom palette) to map Cluster IDs to colors.
2.  **Visual Grouping:**
    *   **Text Color:** Apply the cluster color to the text itself.
    *   **Lines:** Draw faint lines connecting nodes of the same cluster to reinforce the grouping visually.

**Code Snippet:**

```javascript
// Global Color Scale
const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

function createKeywords(trends) {
    // ... inside your d3 enter() selection ...
    
    // Apply Color based on Cluster ID
    trendElements.append("text")
        .style("fill", d => colorScale(d.cluster_id)) // e.g., 0 -> Blue, 1 -> Orange
        .text(d => d.text);
}

function drawConnections(trends) {
    // Generate links between all nodes in the same cluster
    // (For performance, might want to limit to nearest neighbors or backend-provided edges)
    const links = [];
    
    // Simple approach: Link nodes to the "hub" (highest score node) of their cluster
    // Or just draw the edges provided by backend that are "intra-cluster"
    
    // Visualizing the cluster edges provided by backend is best.
    // Assuming 'connections' passed from backend includes cluster info or we filter:
    
    const clusterLinks = svg.append("g")
        .selectAll("line")
        .data(backendConnections.filter(d => d.is_same_cluster)) 
        .enter()
        .append("line")
        .attr("stroke", d => colorScale(d.cluster_id)) // Line matches cluster color
        .attr("stroke-opacity", 0.3)
        .attr("stroke-width", 1);
}
```

---

## Final Recommendation

**I recommend Strategy 2: The Clustering Strategy.**

**Reasoning:**

1.  **User Insight:** Clustering provides immediate, "at-a-glance" understanding of the *topics* driving the trends (e.g., "This group is all about the Election," "That group is about the new Anime"). Weighted graphs (Strategy 1) show relationships but can look like a "hairball" without clear semantic grouping.
2.  **Visual Clarity:** Color-coding by cluster is a powerful pre-attentive attribute. It makes the visualization much easier to parse than varying line thicknesses alone.
3.  **Performance:** Calculating clusters on the backend (using `python-louvain`) is very fast for the scale of data we have (< 1000 nodes). On the frontend, simply coloring nodes is cheaper than rendering hundreds of individual opacity-weighted lines.

**Next Step:**
If you agree, I will proceed with implementing the **Clustering Strategy**. This will involve:
1.  Adding `python-louvain` and `networkx` to `requirements.txt`.
2.  Implementing `detect_trend_clusters` in `src/analyzer.py`.
3.  Updating `src/main.py` to include `cluster_id` in `trends.json`.
4.  Updating `static/js/main.js` to color-code the tag cloud.
