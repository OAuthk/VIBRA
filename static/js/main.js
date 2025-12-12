/**
 * VIBRA - Living Cloud Visualization
 * D3.js based trend visualization
 */

class VIBRAApp {
    constructor() {
        this.trends = [];
        this.currentGenre = 'all';
        this.svg = null;
        this.simulation = null;
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
            const response = await fetch('trends.json');
            if (!response.ok) throw new Error('Failed to load trends');
            this.trends = await response.json();
            console.log(`Loaded ${this.trends.length} trends`);
        } catch (error) {
            console.error('Error loading trends:', error);
            this.trends = [];
        }
    }

    setupEventListeners() {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                // Update active tab
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                // Filter by genre
                this.currentGenre = e.target.dataset.genre;
                this.renderVisualization();
            });
        });
    }

    updateTimeDisplay() {
        const timeDisplay = document.querySelector('.time-display');
        if (timeDisplay) {
            const now = new Date();
            const options = { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit', 
                minute: '2-digit',
                weekday: 'short'
            };
            timeDisplay.textContent = now.toLocaleDateString('ja-JP', options);
        }
    }

    getCategoryMapping(category) {
        // Map Japanese categories to genre filter values
        const mapping = {
            'IT': 'technology',
            'テクノロジー': 'technology',
            '総合': 'all',
            'ニュース': 'business',
            'スポーツ': 'entertainment',
            'エンタメ': 'entertainment',
            'ビジネス': 'business'
        };
        return mapping[category] || 'all';
    }

    getFilteredTrends() {
        if (this.currentGenre === 'all') {
            return this.trends;
        }
        return this.trends.filter(trend => {
            const mappedGenre = this.getCategoryMapping(trend.category);
            return mappedGenre === this.currentGenre;
        });
    }

    getHeatColor(heatLevel, score) {
        // Color palette based on heat level
        const colors = {
            high: ['#EF4444', '#F97316', '#F59E0B'],    // Red-Orange
            medium: ['#3B82F6', '#6366F1', '#8B5CF6'],  // Blue-Purple
            low: ['#6B7280', '#9CA3AF', '#D1D5DB']      // Gray
        };
        const palette = colors[heatLevel] || colors.medium;
        const index = Math.floor(Math.random() * palette.length);
        return palette[index];
    }

    renderVisualization() {
        const container = document.getElementById('visualization');
        if (!container) return;

        // Clear previous visualization
        container.innerHTML = '';

        const filteredTrends = this.getFilteredTrends();
        if (filteredTrends.length === 0) {
            container.innerHTML = '<p class="no-data">表示するトレンドがありません</p>';
            return;
        }

        const width = container.clientWidth;
        const height = container.clientHeight || 500;

        // Create SVG
        this.svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('viewBox', `0 0 ${width} ${height}`);

        // Create nodes from trends
        const nodes = filteredTrends.map((trend, i) => ({
            ...trend,
            id: i,
            radius: this.calculateRadius(trend.score),
            color: this.getHeatColor(trend.heatLevel, trend.score)
        }));

        // Create force simulation
        this.simulation = d3.forceSimulation(nodes)
            .force('charge', d3.forceManyBody().strength(5))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => d.radius + 5))
            .on('tick', () => this.ticked(nodes));

        // Create bubble groups
        const bubbles = this.svg.selectAll('.bubble')
            .data(nodes)
            .enter()
            .append('g')
            .attr('class', d => `bubble stage-${d.stage}`)
            .style('cursor', 'pointer')
            .on('click', (event, d) => this.onBubbleClick(d))
            .on('mouseenter', (event, d) => this.onBubbleHover(event, d, true))
            .on('mouseleave', (event, d) => this.onBubbleHover(event, d, false));

        // Add circles
        bubbles.append('circle')
            .attr('r', d => d.radius)
            .attr('fill', d => d.color)
            .attr('opacity', 0.85)
            .attr('stroke', '#fff')
            .attr('stroke-width', 2);

        // Add text labels
        bubbles.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.3em')
            .attr('fill', '#fff')
            .attr('font-size', d => Math.max(10, d.radius / 3))
            .attr('font-weight', '600')
            .text(d => this.truncateText(d.text, d.radius));

        // Add tooltip
        this.createTooltip();
    }

    calculateRadius(score) {
        // Scale score (0-100) to radius (20-60)
        const minRadius = 25;
        const maxRadius = 65;
        return minRadius + (score / 100) * (maxRadius - minRadius);
    }

    truncateText(text, radius) {
        const maxChars = Math.floor(radius / 6);
        if (text.length > maxChars) {
            return text.substring(0, maxChars - 1) + '…';
        }
        return text;
    }

    ticked(nodes) {
        this.svg.selectAll('.bubble')
            .attr('transform', d => `translate(${d.x}, ${d.y})`);
    }

    createTooltip() {
        // Remove existing tooltip
        d3.select('.tooltip').remove();
        
        d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
    }

    onBubbleHover(event, d, isEnter) {
        const tooltip = d3.select('.tooltip');
        
        if (isEnter) {
            tooltip.transition()
                .duration(200)
                .style('opacity', 1);
            
            tooltip.html(`
                <strong>${d.text}</strong><br>
                カテゴリ: ${d.category}<br>
                スコア: ${d.score}<br>
                ${d.related_words && d.related_words.length > 0 
                    ? `関連: ${d.related_words.join(', ')}` 
                    : ''}
            `)
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 10) + 'px');
        } else {
            tooltip.transition()
                .duration(300)
                .style('opacity', 0);
        }
    }

    onBubbleClick(d) {
        if (d.detail_url) {
            window.open(d.detail_url, '_blank');
        }
    }

    // Handle window resize
    handleResize() {
        if (this.simulation) {
            this.simulation.stop();
        }
        this.renderVisualization();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.vibraApp = new VIBRAApp();
    
    // Handle window resize with debounce
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            window.vibraApp.handleResize();
        }, 250);
    });
});
