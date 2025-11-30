// static/js/main.js

// --- Global state ---
let allTrends = []; // This will hold the data from trends.json
let currentGenre = 'all';
let svg, simulation;

// --- Main Fetch and Initialization Function ---
async function initializeApp() {
    try {
        const response = await fetch('trends.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        allTrends = data.trends;

        // Update time display
        const timeDisplay = document.querySelector('.time-display');
        if (timeDisplay) {
            timeDisplay.textContent = new Date(data.last_updated.replace(' JST', '')).toLocaleString('ja-JP');
        }

        initTabs();
        initVisualization();

        window.addEventListener('resize', handleResize);
        console.log("VIBRA initialized with live data.");

    } catch (error) {
        console.error("Could not initialize VIBRA:", error);
    }
}

// --- D3 Visualization Functions ---
function initVisualization() {
    svg = d3.select("#trend-cloud");
    updateVisualization();
}

function updateVisualization() {
    const container = document.querySelector('.trend-cloud-container');
    if (!container) return;

    const width = container.offsetWidth;
    const height = container.offsetHeight;

    // Filter from 'allTrends'
    const filteredTrends = currentGenre === 'all'
        ? allTrends
        : allTrends.filter(t => t.category === currentGenre);

    svg.attr("width", width).attr("height", height);
    svg.selectAll("*").remove();

    if (filteredTrends.length === 0) return;

    // Scale for font size based on score
    const sizeScale = d3.scaleLinear()
        .domain([0, 100])
        .range([16, 60]); // Font size in pixels

    simulation = d3.forceSimulation(filteredTrends)
        .force("charge", d3.forceManyBody().strength(-50))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(d => sizeScale(d.score) * 0.8))
        .stop();

    for (let i = 0; i < 250; ++i) simulation.tick();

    const trendElements = svg.selectAll(".trend")
        .data(filteredTrends, d => d.text)
        .enter()
        .append("a")
        .attr("xlink:href", d => d.detail_url)
        .attr("target", "_blank")
        .append("text")
        .attr("class", d => `trend heat-${d.heatLevel}`)
        .attr("text-anchor", "middle")
        .attr("x", d => d.x)
        .attr("y", d => d.y)
        .style("font-size", d => `${sizeScale(d.score)}px`)
        .style("fill", d => {
            if (d.heatLevel === 'high') return '#ff0000';
            if (d.heatLevel === 'medium') return '#f59e0b';
            return '#888';
        })
        .style("cursor", "pointer")
        .text(d => d.text);
}

function initTabs() {
    const tabs = document.querySelectorAll('.genre-tabs a');
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            tabs.forEach(t => t.classList.remove('active'));
            e.target.classList.add('active');

            // Assuming the text content matches the category or mapped manually
            // For simplicity, let's map the text to category
            const text = e.target.textContent;
            currentGenre = text === '総合' ? 'all' : text;

            updateVisualization();
        });
    });
}

function handleResize() {
    updateVisualization();
}

// --- Entry Point ---
document.addEventListener('DOMContentLoaded', initializeApp);
