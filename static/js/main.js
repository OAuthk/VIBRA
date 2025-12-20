/**
 * VIBRA - Living Cloud Visualization
 * Refactored: Vanilla JS + Phyllotaxis Layout (No D3)
 * Provides stable, deterministic positioning with organic "cloud" aesthetics.
 */

class VIBRAApp {
    constructor() {
        this.trends = [];
        this.currentGenre = 'all';
        this.container = document.getElementById('visualization');
        this.tooltip = null;
        this.width = 0;
        this.height = 0;
        this.init();
    }

    async init() {
        this.tooltip = this.createTooltip();
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
            if (this.container) {
                this.container.innerHTML = '<p class="no-data">トレンドの読み込みに失敗しました</p>';
            }
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

        // Window resize handler with debounce
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.renderVisualization();
            }, 250);
        });
    }

    updateTimeDisplay() {
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
        if (!this.container) return;
        this.container.innerHTML = ''; // Clear previous

        // Prevent 0 dimension issues
        this.width = this.container.clientWidth || window.innerWidth;
        this.height = this.container.clientHeight || (window.innerHeight - 100);
        if (this.width === 0) this.width = 800;
        if (this.height === 0) this.height = 600;

        const filteredTrends = this.getFilteredTrends();
        if (filteredTrends.length === 0) {
            this.container.innerHTML = '<p class="no-data">表示するトレンドがありません</p>';
            return;
        }

        // Algo: Sort by score descending (Highest score in center)
        filteredTrends.sort((a, b) => b.score - a.score);

        const centerX = this.width / 2;
        const centerY = this.height / 2;

        // Spacing constant: Determines how spread out the cloud is
        // Adjust this if bubbles overlap too much or are too sparse
        const spacing = 55;

        filteredTrends.forEach((trend, i) => {
            // Phyllotaxis Formula
            // theta = index * 137.5 degrees (Golden Angle)
            // r = c * sqrt(index)
            const angle = i * 137.508 * (Math.PI / 180);
            const radius = spacing * Math.sqrt(i);

            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);

            this.createBubbleElement(trend, x, y);
        });
    }

    createBubbleElement(trend, x, y) {
        const size = this.calculateSize(trend.score);
        const color = this.getHeatColor(trend.heatLevel);

        // 1. Container Item (Position)
        const item = document.createElement('div');
        item.className = `trend-item stage-${trend.stage}`;
        item.style.left = `${x}px`;
        item.style.top = `${y}px`;

        // 2. Floater (Animation)
        const floater = document.createElement('div');
        floater.className = 'trend-floater';
        // Randomize start time to avoid synchronized bobbing
        floater.style.animationDelay = `-${Math.random() * 5}s`;

        // 3. Bubble (Visuals)
        const bubble = document.createElement('div');
        bubble.className = 'trend-bubble';
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        bubble.style.background = color;

        // Text
        const textSpan = document.createElement('span');
        textSpan.textContent = this.truncateText(trend.text, size);
        textSpan.style.fontSize = `${Math.max(11, size / 4.5)}px`; // Dynamic font sizing

        // Assemble
        bubble.appendChild(textSpan);
        floater.appendChild(bubble);
        item.appendChild(floater);

        // Interactions
        item.addEventListener('mouseenter', (e) => this.showTooltip(e, trend));
        item.addEventListener('mousemove', (e) => this.moveTooltip(e));
        item.addEventListener('mouseleave', () => this.hideTooltip());
        item.addEventListener('click', () => {
            if (trend.detail_url) window.open(trend.detail_url, '_blank');
        });

        this.container.appendChild(item);
    }

    calculateSize(score) {
        // Output Diameter
        const minD = 60;
        const maxD = 130;
        return minD + (score / 100) * (maxD - minD);
    }

    truncateText(text, diameter) {
        if (!text) return '';
        const t = String(text);
        const lower = t.toLowerCase().trim();
        // Robust check for invalid strings
        if (lower === 'undefined' || lower === 'null' || lower === 'none' || lower === '' || lower.includes('undefined')) return '';

        // Approx character limit based on diameter
        const limit = Math.floor(diameter / 5);
        return t.length > limit ? t.substring(0, limit) + '..' : t;
    }

    // --- Tooltip Logic ---
    createTooltip() {
        let tt = document.querySelector('.tooltip');
        if (!tt) {
            tt = document.createElement('div');
            tt.className = 'tooltip';
            document.body.appendChild(tt);
        }
        return tt;
    }

    showTooltip(e, d) {
        if (!this.tooltip) return;
        this.tooltip.style.opacity = '1';
        this.tooltip.innerHTML = `
            <div class="tt-header">${d.text || 'No Title'}</div>
            <div class="tt-body">${d.summary || '詳細情報なし'}</div>
            <div class="tt-meta">
                <span class="badg">${d.heatLevel ? d.heatLevel.toUpperCase() : 'N/A'}</span>
                <span>Score: ${d.score}</span>
            </div>
            <div class="tt-related">関連: ${d.related_words && d.related_words.length > 0 ? d.related_words.join(', ') : '-'}</div>
        `;
        this.moveTooltip(e);
    }

    moveTooltip(e) {
        if (!this.tooltip) return;
        // Offset
        const x = e.pageX + 15;
        const y = e.pageY - 15;
        this.tooltip.style.left = `${x}px`;
        this.tooltip.style.top = `${y}px`;
    }

    hideTooltip() {
        if (this.tooltip) {
            this.tooltip.style.opacity = '0';
        }
    }
}

// Start App
document.addEventListener('DOMContentLoaded', () => {
    window.vibraApp = new VIBRAApp();
});
