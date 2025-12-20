/**
 * VIBRA - Living Cloud Visualization
 * Refactored for Stability & Performance
 */

class VIBRAApp {
    constructor() {
        this.trends = [];
        this.currentGenre = 'all';
        this.svg = null;
        this.simulation = null;
        this.width = 0;
        this.height = 0;
        this.init();
    }

    async init() {
        await this.loadTrends();
        this.setupEventListeners();
        this.updateTimeDisplay();
        this.renderVisualization();

        // Update time every minute
        setInterval(() => this.updateTimeDisplay(), 60000);
    }

    async loadTrends() {
        try {
            // Cache busting for data
            const response = await fetch(`trends.json?v=${new Date().getTime()}`);
            if (!response.ok) throw new Error('Failed to load trends');
            const data = await response.json();
            this.trends = data.trends || [];

            // Update timestamp if available
            if (data.last_updated) {
                const timeDisplay = document.querySelector('.time-display');
                if (timeDisplay) timeDisplay.textContent = data.last_updated;
            }

            console.log(`Loaded ${this.trends.length} trends`);
        } catch (error) {
            console.error('Error loading trends:', error);
            this.trends = [];
            document.getElementById('visualization').innerHTML = '<p class="no-data">トレンドの読み込みに失敗しました</p>';
        }
    }

    setupEventListeners() {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                this.currentGenre = e.target.dataset.genre;
                this.renderVisualization();
            });
        });

        // Window resize handler with debounce in class
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.renderVisualization();
            }, 250);
        });
    }

    updateTimeDisplay() {
        // Fallback if not updated by JSON
        const timeDisplay = document.querySelector('.time-display');
        if (timeDisplay && !timeDisplay.textContent) {
            const now = new Date();
            timeDisplay.textContent = now.toLocaleString('ja-JP');
        }
    }

    getFilteredTrends() {
        if (this.currentGenre === 'all') {
            return this.trends;
        }
        return this.trends.filter(trend => trend.category === this.currentGenre);
    }

    // Heatmap color with random variance for organic look
    getHeatColor(heatLevel) {
        const colors = {
            high: ['#EF4444', '#F97316', '#F59E0B'],    // Red-Orange
            medium: ['#3B82F6', '#6366F1', '#8B5CF6'],  // Blue-Purple
            low: ['#6B7280', '#9CA3AF', '#D1D5DB']      // Gray
        };
        const palette = colors[heatLevel] || colors.medium;
        return palette[Math.floor(Math.random() * palette.length)];
    }

    renderVisualization() {
        const container = document.getElementById('visualization');
        if (!container) return;

        // Use container size or Window fallback to PREVENT DIAGONAL FLIGHT (0,0 coordinate issue)
        this.width = container.clientWidth || window.innerWidth;
        this.height = container.clientHeight || (window.innerHeight - 100);

        // Ensure we never have 0 dimensions
        if (this.width === 0) this.width = 800;
        if (this.height === 0) this.height = 600;

        // Stop existing simulation
        if (this.simulation) this.simulation.stop();
        container.innerHTML = '';

        const filteredTrends = this.getFilteredTrends();
        if (filteredTrends.length === 0) {
            container.innerHTML = '<p class="no-data">表示するトレンドがありません</p>';
            return;
        }

        // --- D3 Initialization ---
        this.svg = d3.select(container)
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`);

        // Prepare Nodes
        const nodes = filteredTrends.map((d, i) => ({
            ...d,
            id: i,
            radius: this.calculateRadius(d.score),
            fillColor: this.getHeatColor(d.heatLevel),
            // Start AT CENTER to prevent flying in from corner
            x: this.width / 2 + (Math.random() - 0.5) * 50,
            y: this.height / 2 + (Math.random() - 0.5) * 50
        }));

        // Force Simulation
        // Force Simulation - Tuned for stability and gentle floating
        this.simulation = d3.forceSimulation(nodes)
            .velocityDecay(0.6) // Higher friction = less jitter, more "floating" feel
            .force('charge', d3.forceManyBody().strength(-15))
            .force('center', d3.forceCenter(this.width / 2, this.height / 2).strength(0.06))
            .force('x', d3.forceX(this.width / 2).strength(0.1))
            .force('y', d3.forceY(this.height / 2).strength(0.1))
            .force('collision', d3.forceCollide().radius(d => d.radius + 5).strength(0.7));

        // Tooltip
        const tooltip = this.createTooltip();

        // --- Render Groups (The VisualWrapper Pattern) ---

        // 1. Outer Group: Positioned by D3 (Translate)
        const nodeGroups = this.svg.selectAll('.node')
            .data(nodes)
            .join('g')
            .attr('class', 'node')
            .style('cursor', 'pointer')
            .on('click', (e, d) => {
                if (d.detail_url) window.open(d.detail_url, '_blank');
            });

        // 2. Inner Wrapper: ANIMATED by CSS (Float) and Scaled on Hover
        // Split into two groups to avoid 'transform' property conflict
        const floaters = nodeGroups.append('g')
            .attr('class', 'floater')
            .style('animation-delay', () => `-${Math.random() * 5}s`);

        const scalers = floaters.append('g')
            .attr('class', d => `scaler stage-${d.stage}`);

        // 3. Visuals: Circle & Text (Attached to Scaler)
        scalers.append('circle')
            .attr('r', d => d.radius)
            .attr('fill', d => d.fillColor)
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .attr('stroke-opacity', 0.8);

        scalers.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .attr('fill', '#fff')
            .attr('font-weight', '700')
            .attr('font-size', d => Math.max(12, d.radius / 3.5))
            .style('pointer-events', 'none')
            .text(d => this.truncateText(d.text, d.radius));

        // --- Interaction (Hover for Tooltip) ---
        nodeGroups
            .on('mouseenter', (event, d) => {
                tooltip.style('opacity', 1)
                    .html(`
                        <div class="tt-header">${d.text || 'No Title'}</div>
                        <div class="tt-body">${d.summary || '詳細情報なし'}</div>
                        <div class="tt-meta">
                            <span class="badg">${d.heatLevel ? d.heatLevel.toUpperCase() : 'N/A'}</span>
                            <span>Score: ${d.score}</span>
                        </div>
                        <div class="tt-related">関連: ${d.related_words && d.related_words.length > 0 ? d.related_words.join(', ') : '-'}</div>
                    `)
                    .style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 15) + 'px');
            })
            .on('mousemove', (event) => {
                tooltip
                    .style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 15) + 'px');
            })
            .on('mouseleave', () => {
                tooltip.style('opacity', 0);
            });

        // --- Tick Update ---
        this.simulation.on('tick', () => {
            nodeGroups.attr('transform', d => `translate(${d.x}, ${d.y})`);
        });
    }

    calculateRadius(score) {
        const minR = 30;
        const maxR = 80;
        return minR + (score / 100) * (maxR - minR);
    }

    truncateText(text, radius) {
        if (!text) return '';
        const t = String(text); // Ensure string
        const lower = t.toLowerCase().trim();
        if (lower === 'undefined' || lower === 'null' || lower === 'none' || lower === '') return '';

        const limit = Math.floor(radius / 4); // Adjusted limit
        return t.length > limit ? t.substring(0, limit) + '..' : t;
    }

    createTooltip() {
        let tt = d3.select('.tooltip');
        if (tt.empty()) {
            tt = d3.select('body').append('div').attr('class', 'tooltip');
        }
        return tt;
    }
}

// Start
document.addEventListener('DOMContentLoaded', () => {
    window.vibraApp = new VIBRAApp();
});
