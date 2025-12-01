// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    // --- Global State ---
    let allTrends = [];
    let currentGenre = 'all';
    let container, svgLines, keywordsContainer;
    let width, height;

    // Color scale for clusters
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    // --- Main Initialization Function ---
    async function initializeApp() {
        try {
            // 1. Fetch data from the backend-generated JSON file
            const response = await fetch('trends.json');
            if (!response.ok) {
                throw new Error(`Failed to fetch trends.json: ${response.statusText}`);
            }
            const data = await response.json();
            allTrends = data.trends || [];

            // 2. Populate dynamic elements in the DOM
            populateMetaInfo(data.last_updated);

            // 3. Initialize UI components and visualization
            initTabs();
            initVisualization();

            window.addEventListener('resize', handleResize);
            console.log("VIBRA initialized with live data.");

        } catch (error) {
            console.error("Initialization failed:", error);
        }
    }

    function populateMetaInfo(lastUpdated) {
        const timeDisplay = document.querySelector('.time-display');
        if (timeDisplay && lastUpdated) {
            try {
                const date = new Date(lastUpdated.replace(' JST', ''));
                timeDisplay.textContent = date.toLocaleString('ja-JP', {
                    year: 'numeric', month: 'long', day: 'numeric',
                    hour: '2-digit', minute: '2-digit'
                });
            } catch {
                timeDisplay.textContent = lastUpdated;
            }
        }

        const yearSpan = document.getElementById('copyright-year');
        if (yearSpan) {
            yearSpan.textContent = new Date().getFullYear();
        }
    }

    // --- Visualization Logic ---

    function initVisualization() {
        container = document.querySelector('.trend-cloud-container');
        if (!container) return;

        svgLines = d3.select("#connection-lines");
        keywordsContainer = document.getElementById("keywords-container");

        updateDimensions();
        renderScene();
    }

    function updateDimensions() {
        if (!container) return;
        width = container.offsetWidth;
        height = container.offsetHeight;
        svgLines.attr("width", width).attr("height", height);
    }

    function renderScene() {
        // Clear previous elements
        keywordsContainer.innerHTML = '';
        svgLines.selectAll("*").remove();

        // Filter trends
        const filteredTrends = currentGenre === 'all'
            ? allTrends
            : allTrends.filter(t => t.category === currentGenre);

        if (filteredTrends.length === 0) return;

        // 1. Calculate Positions (Custom Physics Layout)
        const positionedTrends = calculatePositions(filteredTrends);

        // 2. Render Keywords
        createKeywords(positionedTrends);

        // 3. Render Connections
        drawConnections(positionedTrends);
    }

    // --- Custom Layout Algorithm ---
    function calculatePositions(trends) {
        const placedItems = [];
        // Sort by score descending to place largest items first
        const sortedTrends = [...trends].sort((a, b) => b.score - a.score);

        // Scale for font size
        const sizeScale = d3.scaleLinear()
            .domain([0, 100])
            .range([16, 48]); // Adjusted range for better fit

        sortedTrends.forEach(trend => {
            const fontSize = sizeScale(trend.score);
            // Estimate dimensions (approximate width based on char count)
            // A better way would be to create a hidden element to measure, 
            // but estimation is faster and sufficient here.
            const estimatedWidth = trend.text.length * fontSize * 1.2 + 40; // +padding
            const estimatedHeight = fontSize * 1.5 + 20;

            let x, y, overlapping;
            let attempts = 0;
            const maxAttempts = 100;

            do {
                overlapping = false;
                // Random position within container (with padding)
                x = Math.random() * (width - estimatedWidth - 40) + 20;
                y = Math.random() * (height - estimatedHeight - 40) + 20;

                // Check collision with already placed items
                for (const item of placedItems) {
                    if (isOverlapping(
                        x, y, estimatedWidth, estimatedHeight,
                        item.x, item.y, item.width, item.height
                    )) {
                        overlapping = true;
                        break;
                    }
                }
                attempts++;
            } while (overlapping && attempts < maxAttempts);

            // If we couldn't find a spot, place it anyway (or skip it, but better to show it)
            // Ideally we might push it to a list of "failed" items or try a different strategy.
            // For now, we accept the last position even if overlapping slightly.

            const item = {
                ...trend,
                x: x,
                y: y,
                width: estimatedWidth,
                height: estimatedHeight,
                fontSize: fontSize
            };
            placedItems.push(item);
        });

        return placedItems;
    }

    function isOverlapping(x1, y1, w1, h1, x2, y2, w2, h2) {
        // Add some buffer for spacing
        const buffer = 20;
        return x1 < x2 + w2 + buffer &&
            x1 + w1 + buffer > x2 &&
            y1 < y2 + h2 + buffer &&
            y1 + h1 + buffer > y2;
    }

    // --- Rendering Functions ---

    function createKeywords(trends) {
        trends.forEach((trend, index) => {
            const el = document.createElement('div');
            el.className = 'keyword';
            el.textContent = trend.text;

            // Styles
            el.style.left = `${trend.x}px`;
            el.style.top = `${trend.y}px`;
            el.style.fontSize = `${trend.fontSize}px`;
            el.style.color = colorScale(trend.cluster_id);

            // Animation delay for "organic" feel
            el.style.animation = `float ${3 + Math.random() * 2}s ease-in-out infinite`;
            el.style.animationDelay = `${Math.random() * 2}s`;

            // Data attributes for interactivity
            el.dataset.clusterId = trend.cluster_id;
            el.dataset.url = trend.detail_url;

            // Events
            el.addEventListener('click', () => {
                window.open(trend.detail_url, '_blank');
            });

            el.addEventListener('mouseenter', () => handleMouseEnter(trend.cluster_id));
            el.addEventListener('mouseleave', handleMouseLeave);

            keywordsContainer.appendChild(el);
        });
    }

    function drawConnections(trends) {
        // Create links between items in the same cluster
        // To avoid too many lines, we can link each item to the "hub" (highest score in cluster)
        // or link nearest neighbors. 
        // For visual "constellation" effect, linking to 2-3 random peers in the same cluster works well.

        const clusterGroups = {};
        trends.forEach(t => {
            if (!clusterGroups[t.cluster_id]) clusterGroups[t.cluster_id] = [];
            clusterGroups[t.cluster_id].push(t);
        });

        const links = [];

        Object.values(clusterGroups).forEach(group => {
            if (group.length < 2) return;

            // Strategy: Link each node to the next one in the list (chain) 
            // plus one random other node for triangulation
            for (let i = 0; i < group.length; i++) {
                const source = group[i];
                // Link to next (loop back to start)
                const target = group[(i + 1) % group.length];

                links.push({
                    x1: source.x + source.width / 2,
                    y1: source.y + source.height / 2,
                    x2: target.x + target.width / 2,
                    y2: target.y + target.height / 2,
                    cluster_id: source.cluster_id
                });

                // Optional: Add extra random link for density if group is large
                if (group.length > 4) {
                    const randomIdx = Math.floor(Math.random() * group.length);
                    if (randomIdx !== i && randomIdx !== (i + 1) % group.length) {
                        const target2 = group[randomIdx];
                        links.push({
                            x1: source.x + source.width / 2,
                            y1: source.y + source.height / 2,
                            x2: target2.x + target2.width / 2,
                            y2: target2.y + target2.height / 2,
                            cluster_id: source.cluster_id
                        });
                    }
                }
            }
        });

        svgLines.selectAll("line")
            .data(links)
            .enter()
            .append("line")
            .attr("class", "connection-line")
            .attr("x1", d => d.x1)
            .attr("y1", d => d.y1)
            .attr("x2", d => d.x2)
            .attr("y2", d => d.y2)
            .attr("stroke", d => colorScale(d.cluster_id)) // Use cluster color for lines too?
            // Actually, style.css sets stroke color. 
            // If we want colored lines, we override here.
            // Let's use the cluster color but with low opacity for a nice effect.
            .style("stroke", d => colorScale(d.cluster_id))
            .style("stroke-opacity", 0.3)
            .attr("data-cluster-id", d => d.cluster_id);
    }

    // --- Interaction Logic ---

    function handleMouseEnter(clusterId) {
        // Fade out everything
        const allKeywords = document.querySelectorAll('.keyword');
        const allLines = document.querySelectorAll('.connection-line');

        allKeywords.forEach(el => {
            if (parseInt(el.dataset.clusterId) === clusterId) {
                el.style.opacity = 1;
                el.style.transform = 'scale(1.1)';
                el.style.zIndex = 10;
            } else {
                el.style.opacity = 0.2;
                el.style.zIndex = 1;
            }
        });

        allLines.forEach(line => {
            if (parseInt(line.getAttribute('data-cluster-id')) === clusterId) {
                line.style.opacity = 0.8;
                line.style.strokeWidth = 2;
            } else {
                line.style.opacity = 0.05;
            }
        });
    }

    function handleMouseLeave() {
        // Reset
        const allKeywords = document.querySelectorAll('.keyword');
        const allLines = document.querySelectorAll('.connection-line');

        allKeywords.forEach(el => {
            el.style.opacity = 1;
            el.style.transform = 'scale(1)';
            el.style.zIndex = '';
        });

        allLines.forEach(line => {
            line.style.opacity = 0.3; // Default opacity
            line.style.strokeWidth = '';
        });
    }

    // --- Tabs Logic ---
    function initTabs() {
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                tabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');

                const genre = e.target.getAttribute('data-genre');
                // Simple mapping for demo:
                const genreMap = {
                    'all': 'all',
                    'technology': 'IT',
                    'entertainment': 'エンタメ',
                    'business': 'ニュース',
                    'lifestyle': '総合',
                    'sports': 'スポーツ',
                    'politics': 'ニュース'
                };

                currentGenre = genreMap[genre] || 'all';
                renderScene(); // Re-render with new filter
            });
        });
    }

    // --- Resize Logic ---
    let resizeTimeout;
    function handleResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updateDimensions();
            renderScene();
        }, 250);
    }

    // --- Entry Point ---
    initializeApp();
});
