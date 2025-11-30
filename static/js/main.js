// static/js/main.js
document.addEventListener('DOMContentLoaded', function () {
    // --- Global State ---
    let allTrends = [];
    let currentGenre = 'all';
    let svg, simulation;

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
            // You can display an error message to the user here
        }
    }

    function populateMetaInfo(lastUpdated) {
        const timeDisplay = document.querySelector('.time-display');
        if (timeDisplay && lastUpdated) {
            // Format the date/time nicely (optional, but good practice)
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

    // --- Visualization & UI Logic ---

    function initVisualization() {
        const container = document.querySelector('.trend-cloud-container');
        if (!container) return;

        svg = d3.select("#trend-cloud");

        // Set initial size
        const width = container.offsetWidth;
        const height = container.offsetHeight;
        svg.attr("width", width).attr("height", height);

        updateVisualization();
    }

    function updateVisualization() {
        const container = document.querySelector('.trend-cloud-container');
        if (!container) return;

        const width = container.offsetWidth;
        const height = container.offsetHeight;

        const filteredTrends = currentGenre === 'all'
            ? allTrends
            : allTrends.filter(t => t.category === currentGenre);

        svg.attr("width", width).attr("height", height);
        svg.selectAll("*").remove();

        if (filteredTrends.length === 0) return;

        // Scale for font size based on score
        const sizeScale = d3.scaleLinear()
            .domain([0, 100])
            .range([16, 64]);

        simulation = d3.forceSimulation(filteredTrends)
            .force("charge", d3.forceManyBody().strength(-30))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => sizeScale(d.score) * 0.7))
            .stop();

        // Run simulation
        for (let i = 0; i < 300; ++i) simulation.tick();

        const trendElements = svg.selectAll(".trend-group")
            .data(filteredTrends, d => d.text)
            .enter()
            .append("g")
            .attr("class", "trend-group")
            .attr("transform", d => `translate(${d.x},${d.y})`);

        trendElements.append("a")
            .attr("xlink:href", d => d.detail_url)
            .attr("target", "_blank")
            .append("text")
            .attr("class", d => `trend-text heat-${d.heatLevel} stage-${d.stage}`)
            .attr("text-anchor", "middle")
            .style("font-size", d => `${sizeScale(d.score)}px`)
            .text(d => d.text)
            .on("mouseover", function (event, d) {
                d3.select(this).transition().duration(200).style("opacity", 0.7);
            })
            .on("mouseout", function (event, d) {
                d3.select(this).transition().duration(200).style("opacity", 1);
            });
    }

    function initTabs() {
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                tabs.forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');

                // Map genre
                const genre = e.target.getAttribute('data-genre');

                // Map frontend genre to backend category if needed
                // Backend categories: '総合', 'エンタメ', 'ニュース', 'スポーツ', 'IT'
                // Frontend genres: 'all', 'technology', 'entertainment', 'business', 'lifestyle', 'sports', 'politics'
                // Simple mapping for demo:
                const genreMap = {
                    'all': 'all',
                    'technology': 'IT',
                    'entertainment': 'エンタメ',
                    'business': 'ニュース', // Approximation
                    'lifestyle': '総合', // Approximation
                    'sports': 'スポーツ',
                    'politics': 'ニュース'
                };

                currentGenre = genreMap[genre] || 'all';
                updateVisualization();
            });
        });
    }

    let resizeTimeout;
    function handleResize() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const container = document.querySelector('.trend-cloud-container');
            if (container) {
                const width = container.offsetWidth;
                const height = container.offsetHeight;
                svg.attr("width", width).attr("height", height);
                updateVisualization();
            }
        }, 250);
    }

    // --- Entry Point ---
    initializeApp();
});
