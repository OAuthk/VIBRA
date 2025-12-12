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

        // Create force simulation - バブルを中央に強く密集させる
        this.simulation = d3.forceSimulation(nodes)
            .force('charge', d3.forceManyBody().strength(150))  // さらに強い引力
            .force('center', d3.forceCenter(width / 2, height / 2).strength(0.5))  // 中央への引力
            .force('collision', d3.forceCollide().radius(d => d.radius + 1).strength(0.9))  // 最小マージン
            .force('x', d3.forceX(width / 2).strength(0.3))   // X方向中央へ
            .force('y', d3.forceY(height / 2).strength(0.3))  // Y方向中央へ
            .on('tick', () => this.ticked(nodes))
            .on('end', () => {
                console.log('Simulation ended');
            });

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

    isMobile() {
        return window.innerWidth <= 768;
    }

    calculateRadius(score) {
        // Scale score (0-100) to radius
        const isMobile = this.isMobile();
        const minRadius = isMobile ? 35 : 25; // モバイルは大きく
        const maxRadius = isMobile ? 75 : 65;
        return minRadius + (score / 100) * (maxRadius - minRadius);
    }

    truncateText(text, radius) {
        const maxChars = Math.floor(radius / (this.isMobile() ? 5 : 6));
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
        if (this.isMobile()) return;

        // 以下PC用レガシー実装継続（showTooltipへの移行はonBubbleClickでのみ実施）
        const tooltip = d3.select('.tooltip');
        const bubble = d3.select(event.currentTarget);

        if (isEnter) {
            // バブルを浮かび上がらせる（サイズ拡大 + 影強調）
            bubble.select('circle')
                .transition()
                .duration(200)
                .attr('r', d.radius * 1.1)
                .attr('opacity', 1)
                .style('filter', 'drop-shadow(0 6px 16px rgba(0, 0, 0, 0.3))');

            // テキストも少し大きく
            bubble.select('text')
                .transition()
                .duration(200)
                .attr('font-size', Math.max(12, d.radius / 2.5));

            tooltip.transition()
                .duration(200)
                .style('opacity', 1);

            tooltip.html(`
                <strong>${d.text}</strong><br>
                <div style="font-size:0.85em; color:#ddd; margin:4px 0; max-width:200px; white-space:normal; line-height:1.4;">${d.summary || '詳細情報なし'}</div>
                <div style="font-size:0.8em; opacity:0.8; margin-top:4px;">
                    カテゴリ: ${d.category}<br>
                    スコア: ${d.score}
                </div>
            `)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        } else {
            // 元のサイズに戻す
            bubble.select('circle')
                .transition()
                .duration(300)
                .attr('r', d.radius)
                .attr('opacity', 0.85)
                .style('filter', null);

            // テキストも元に戻す
            bubble.select('text')
                .transition()
                .duration(300)
                .attr('font-size', Math.max(10, d.radius / 3));

            tooltip.transition()
                .duration(300)
                .style('opacity', 0);
        }
    }

    onBubbleClick(event, d) {
        if (this.isMobile()) {
            // モバイル: ボトムシート表示のトグル
            this.showTooltip(event, d, true, true);
        } else {
            // PC: 直接遷移
            if (d.detail_url) {
                window.open(d.detail_url, '_blank');
            }
        }
    }

    showTooltip(event, d, show, isClick = false) {
        const tooltip = d3.select('.tooltip');
        // event.currentTargetが使えない場合（click時など）のフォールバック
        const target = event.currentTarget || event.target;
        const bubble = d3.select(target).closest('.bubble').size() ? d3.select(target).closest('.bubble') : d3.select(target);

        if (show) {
            // バブル強調エフェクト
            bubble.select('circle')
                .transition()
                .duration(200)
                .attr('r', d.radius * 1.1)
                .attr('opacity', 1)
                .style('filter', 'drop-shadow(0 6px 16px rgba(0, 0, 0, 0.3))');

            bubble.select('text')
                .transition()
                .duration(200)
                .attr('font-size', Math.max(12, d.radius / 2.5));

            // ツールチップ表示
            if (this.isMobile()) {
                tooltip.classed('visible', true); // CSSでボトムシートアニメーション
                tooltip.style('opacity', 1);      // 確実に表示
            } else {
                tooltip.transition().duration(200).style('opacity', 1);
            }

            // コンテンツ生成
            const linkHtml = d.detail_url ? `<br><a href="${d.detail_url}" class="tooltip-link" target="_blank" style="color:#60a5fa; display:inline-block; margin-top:8px; padding:8px 0; width:100%; text-align:center; border:1px solid #60a5fa; border-radius:4px;">詳しく見る &rarr;</a>` : '';

            tooltip.html(`
                <strong>${d.text}</strong>
                <div style="font-size:0.9em; color:#ddd; margin:4px 0; max-width:${this.isMobile() ? '100%' : '200px'}; white-space:normal; line-height:1.5;">${d.summary || '詳細情報なし'}</div>
                <div style="font-size:0.85em; opacity:0.8; margin-top:8px; border-top:1px solid rgba(255,255,255,0.1); padding-top:4px;">
                    カテゴリ: ${d.category} | スコア: ${d.score}
                </div>
                ${this.isMobile() ? linkHtml : ''}
            `);

            // PC位置調整
            if (!this.isMobile()) {
                tooltip.style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            }

        } else {
            // 非表示処理
            bubble.select('circle')
                .transition()
                .duration(300)
                .attr('r', d.radius)
                .attr('opacity', 0.85)
                .style('filter', null);

            bubble.select('text')
                .transition()
                .duration(300)
                .attr('font-size', Math.max(10, d.radius / 3));

            if (this.isMobile()) {
                tooltip.classed('visible', false);
            } else {
                tooltip.transition().duration(300).style('opacity', 0);
            }
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
