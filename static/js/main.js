/*
 * VIBRA - Frontend Main Logic
 *
 * This script handles:
 * - Fetching trend data from the backend.
 * - Rendering the interactive bubble chart using D3.js.
 * - Handling user interactions like tab switching, clicks, and hovers.
 * - Ensuring the visualization is responsive.
 */
document.addEventListener('DOMContentLoaded', function() {
    
    class VIBRAApp {
        constructor() {
            this.allTrends = [];
            this.currentGenre = 'all';
            this.svg = null;
            this.simulation = null;
            this.init();
        }

        async init() {
            try {
                // 1. Fetch data from the backend-generated JSON file
                const response = await fetch('trends.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                this.allTrends = data.trends || [];

                // 2. Populate dynamic elements in the DOM
                this.populateMetaInfo(data.last_updated);
                
                // 3. Initialize UI components and visualization
                this.initTabs();
                this.renderVisualization();
                
                window.addEventListener('resize', this.handleResize.bind(this));
                console.log("VIBRA initialized with live data.");

            } catch (error) {
                console.error("Could not initialize VIBRA:", error);
                const container = document.getElementById('visualization');
                if(container) container.innerHTML = '<p class="no-data">トレンドの読み込みに失敗しました</p>';
            }
        }
        
        populateMetaInfo(lastUpdated) {
            const timeDisplay = document.querySelector('.time-display');
            if (timeDisplay && lastUpdated) {
                timeDisplay.textContent = lastUpdated;
            }
            const yearSpan = document.getElementById('current-year');
            if (yearSpan) {
                yearSpan.textContent = new Date().getFullYear();
            }
        }

        initTabs() {
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    tabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    this.currentGenre = tab.dataset.genre;
                    this.renderVisualization();
                });
            });
        }

        renderVisualization() {
            const container = document.getElementById('visualization');
            if (!container) return;

            container.innerHTML = '';

            const filteredTrends = this.currentGenre === 'all' 
                ? this.allTrends 
                : this.allTrends.filter(t => t.category === this.currentGenre);
            
            if (filteredTrends.length === 0) {
                container.innerHTML = '<p class="no-data">表示するトレンドがありません</p>';
                return;
            }

            const width = container.clientWidth;
            const height = container.clientHeight || 500;

            this.svg = d3.select(container).append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('viewBox', `0 0 ${width} ${height}`);

            const nodes = filteredTrends.map((trend, i) => ({
                ...trend,
                id: i,
                radius: this.calculateRadius(trend.score),
                color: this.getHeatColor(trend.heatLevel)
            }));
            
            this.simulation = d3.forceSimulation(nodes)
                .force('charge', d3.forceManyBody().strength(10))
                .force('center', d3.forceCenter(width / 2, height / 2).strength(0.05))
                .force('collision', d3.forceCollide().radius(d => d.radius + 8))
                .on('tick', () => {
                    // Update bubble positions on each simulation tick
                    this.svg.selectAll('.bubble')
                        .attr('transform', d => `translate(${d.x}, ${d.y})`);
                });

            // Create bubble groups
            const bubbles = this.svg.selectAll('.bubble')
                .data(nodes, d => d.title) // Use title as key for object constancy
                .join('g')
                .attr('class', d => `bubble stage-${d.stage}`)
                .style('cursor', d => (d.links && d.links.find(link => link.provider === 'Google')) ? 'pointer' : 'default')
                .on('click', (event, d) => this.onBubbleClick(d))
                .on('mouseenter', (event, d) => this.onBubbleHover(event, d, true))
                .on('mouseleave', (event, d) => this.onBubbleHover(event, d, false));

            // Add circles to bubbles
            bubbles.append('circle')
                .attr('r', d => d.radius)
                .attr('fill', d => d.color)
                .attr('opacity', 0.85)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);

            // Add text labels to bubbles
            bubbles.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '0.3em')
                .attr('fill', '#fff')
                .attr('font-size', d => Math.max(10, d.radius / 3.5))
                .attr('font-weight', '600')
                .text(d => this.truncateText(d.title, d.radius));
                
            this.createTooltip();
        }

        onBubbleClick(d) {
            // Find the Google search link from the links array
            const googleLink = d.links.find(link => link.provider === 'Google');
            if (googleLink && googleLink.url) {
                window.open(googleLink.url, '_blank');
            }
        }

        onBubbleHover(event, d, isEnter) {
            const tooltip = d3.select('.tooltip');
            if (isEnter) {
                tooltip.transition().duration(200).style('opacity', 1);
                
                const relatedWordsText = d.co_occurring_words && d.co_occurring_words.length > 0
                    ? `<strong>関連ワード:</strong> ${d.co_occurring_words.join(', ')}`
                    : '詳細情報なし';

                tooltip.html(`
                    <strong>${d.title}</strong>
                    <p>カテゴリ: ${d.category}</p>
                    <p>スコア: ${d.score}</p>
                    <p>${relatedWordsText}</p>
                `)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px');
            } else {
                tooltip.transition().duration(300).style('opacity', 0);
            }
        }
        
        createTooltip() {
            if (d3.select('.tooltip').empty()) {
                d3.select('body').append('div')
                    .attr('class', 'tooltip')
                    .style('opacity', 0);
            }
        }

        calculateRadius(score) {
            const minRadius = 25;
            const maxRadius = 65;
            return minRadius + (score / 100) * (maxRadius - minRadius);
        }

        truncateText(text, radius) {
            // Adjust character limit based on radius for better fit
            const maxChars = Math.floor(radius / 7);
            if (text && text.length > maxChars) {
                return text.substring(0, maxChars - 1) + '…';
            }
            return text;
        }
        
        getHeatColor(heatLevel) {
            const colors = {
                high: ['#EF4444', '#F97316', '#DC2626'],   // Reds
                medium: ['#F59E0B', '#FBBF24', '#F9A825'], // Oranges/Yellows
                low: ['#6B7280', '#9CA3AF', '#4B5563']     // Grays
            };
            const palette = colors[heatLevel] || colors.low;
            return palette[Math.floor(Math.random() * palette.length)];
        }

        handleResize() {
            if (this.simulation) this.simulation.stop();
            // Debounce resize event to avoid excessive re-rendering
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.renderVisualization();
            }, 250);
        }
    }

    // Initialize the application
    new VIBRAApp();
});