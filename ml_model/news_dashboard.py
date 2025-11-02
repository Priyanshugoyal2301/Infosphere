"""
Web Dashboard for Infosphere News Service

A Flask web application to monitor and manage the real-time news
fetching service with interactive charts and controls.

Features:
- Real-time service monitoring
- News statistics and analytics
- Manual service controls
- Live news feed display
- Performance metrics

Author: Infosphere Team
Date: October 2025
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, List

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.extend([current_dir, parent_dir])

from realtime_news_fetcher import RealTimeNewsFetcher
from news_service import NewsService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'infosphere-news-dashboard-2025'

# Global service instance
news_service = NewsService()
news_fetcher = RealTimeNewsFetcher()


@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/status')
def api_status():
    """Get current service status."""
    try:
        status = news_service.get_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/news/latest')
def api_latest_news():
    """Get latest news articles."""
    try:
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        df = news_fetcher.get_latest_news(hours=hours)
        
        # Convert to list of dicts for JSON response
        articles = []
        for _, row in df.head(limit).iterrows():
            articles.append({
                'title': row['title'],
                'content': row['content'][:200] + '...' if len(row['content']) > 200 else row['content'],
                'source': row['source'],
                'category': row['ml_category'],
                'published_date': row['published_date'],
                'fetched_date': row['fetched_date'],
                'url': row.get('url', '#')
            })
        
        return jsonify({
            'success': True,
            'data': articles,
            'total': len(df)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics')
def api_statistics():
    """Get news statistics."""
    try:
        stats = news_fetcher.get_news_statistics()
        
        # Add time-based analytics
        conn = sqlite3.connect(news_fetcher.db_path)
        cursor = conn.cursor()
        
        # Hourly distribution (last 24 hours)
        cursor.execute('''
            SELECT strftime('%H', fetched_date) as hour, COUNT(*) as count
            FROM news_articles 
            WHERE fetched_date >= datetime('now', '-24 hours')
            GROUP BY hour
            ORDER BY hour
        ''')
        hourly_data = dict(cursor.fetchall())
        
        # Daily distribution (last 7 days)
        cursor.execute('''
            SELECT DATE(fetched_date) as date, COUNT(*) as count
            FROM news_articles 
            WHERE fetched_date >= datetime('now', '-7 days')
            GROUP BY date
            ORDER BY date
        ''')
        daily_data = dict(cursor.fetchall())
        
        conn.close()
        
        # Format for charts
        stats['charts'] = {
            'hourly': {
                'labels': [f"{i:02d}:00" for i in range(24)],
                'data': [hourly_data.get(f"{i:02d}", 0) for i in range(24)]
            },
            'daily': {
                'labels': list(daily_data.keys()),
                'data': list(daily_data.values())
            }
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/service/start', methods=['POST'])
def api_start_service():
    """Start the news service."""
    try:
        if not news_service.running:
            # Start in background thread
            service_thread = threading.Thread(target=news_service.start, daemon=True)
            service_thread.start()
            time.sleep(2)  # Give it time to start
            
        return jsonify({
            'success': True,
            'message': 'Service started successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/service/stop', methods=['POST'])
def api_stop_service():
    """Stop the news service."""
    try:
        news_service.stop()
        return jsonify({
            'success': True,
            'message': 'Service stopped successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/fetch/manual', methods=['POST'])
def api_manual_fetch():
    """Trigger manual news fetch."""
    try:
        result = news_service.fetch_and_process()
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/csv', methods=['GET'])
def api_export_csv():
    """Export news to CSV."""
    try:
        filename = news_fetcher.export_to_csv()
        if filename:
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'Exported to {filename}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Export failed'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_dashboard_template():
    """Create the HTML dashboard template."""
    template_dir = os.path.join(current_dir, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infosphere News Service Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .status-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .stat-box {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-top: 3px solid #667eea;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-running { background: #28a745; }
        .status-stopped { background: #dc3545; }
        .status-starting { background: #ffc107; }
        
        .charts-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 25px;
        }
        
        .chart-box {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }
        
        .news-feed {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            max-height: 500px;
            overflow-y: auto;
        }
        
        .news-item {
            border-bottom: 1px solid #eee;
            padding: 15px 0;
        }
        
        .news-item:last-child {
            border-bottom: none;
        }
        
        .news-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }
        
        .news-meta {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 8px;
        }
        
        .news-content {
            color: #555;
            line-height: 1.4;
        }
        
        .category-tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .charts-container {
                grid-template-columns: 1fr;
            }
            
            .controls {
                justify-content: center;
            }
            
            .btn {
                flex: 1;
                min-width: 120px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Infosphere News Service</h1>
            <p>Real-time news monitoring and classification dashboard</p>
        </div>
        
        <div class="status-card">
            <h2>Service Status</h2>
            <p id="service-status">Loading...</p>
            <div class="controls">
                <button class="btn btn-success" onclick="startService()">▶️ Start Service</button>
                <button class="btn btn-danger" onclick="stopService()">⏹️ Stop Service</button>
                <button class="btn btn-primary" onclick="manualFetch()">📡 Manual Fetch</button>
                <button class="btn btn-secondary" onclick="exportData()">📄 Export CSV</button>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-number" id="total-articles">0</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="recent-articles">0</div>
                <div class="stat-label">Recent (24h)</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="fetch-cycles">0</div>
                <div class="stat-label">Fetch Cycles</div>
            </div>
            <div class="stat-box">
                <div class="stat-number" id="uptime">0</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>
        
        <div class="charts-container">
            <div class="chart-box">
                <h3>Hourly Distribution</h3>
                <canvas id="hourlyChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Category Distribution</h3>
                <canvas id="categoryChart"></canvas>
            </div>
        </div>
        
        <div class="news-feed">
            <h2>Latest News Feed</h2>
            <div id="news-container">
                <div class="loading">Loading latest news...</div>
            </div>
        </div>
    </div>

    <script>
        let hourlyChart, categoryChart;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            loadDashboard();
            
            // Auto-refresh every 30 seconds
            setInterval(loadDashboard, 30000);
        });
        
        function initCharts() {
            // Hourly chart
            const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
            hourlyChart = new Chart(hourlyCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Articles per Hour',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            
            // Category chart
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            categoryChart = new Chart(categoryCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB', 
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40'
                        ]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        }
        
        async function loadDashboard() {
            try {
                await Promise.all([
                    loadStatus(),
                    loadStatistics(),
                    loadLatestNews()
                ]);
            } catch (error) {
                console.error('Dashboard load error:', error);
            }
        }
        
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const result = await response.json();
                
                if (result.success) {
                    const status = result.data;
                    const statusElement = document.getElementById('service-status');
                    const indicator = getStatusIndicator(status.status);
                    
                    statusElement.innerHTML = `
                        ${indicator} Status: <strong>${status.status}</strong><br>
                        Uptime: ${status.uptime}<br>
                        Last fetch: ${status.last_fetch || 'Never'}
                    `;
                    
                    // Update stats
                    document.getElementById('fetch-cycles').textContent = status.total_fetch_cycles;
                    document.getElementById('uptime').textContent = status.uptime;
                }
            } catch (error) {
                console.error('Status load error:', error);
            }
        }
        
        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const result = await response.json();
                
                if (result.success) {
                    const stats = result.data;
                    
                    // Update stats
                    document.getElementById('total-articles').textContent = stats.total_articles || 0;
                    document.getElementById('recent-articles').textContent = stats.recent_24h || 0;
                    
                    // Update charts
                    if (stats.charts) {
                        // Hourly chart
                        hourlyChart.data.labels = stats.charts.hourly.labels;
                        hourlyChart.data.datasets[0].data = stats.charts.hourly.data;
                        hourlyChart.update();
                        
                        // Category chart
                        if (stats.ml_categories) {
                            categoryChart.data.labels = Object.keys(stats.ml_categories);
                            categoryChart.data.datasets[0].data = Object.values(stats.ml_categories);
                            categoryChart.update();
                        }
                    }
                }
            } catch (error) {
                console.error('Statistics load error:', error);
            }
        }
        
        async function loadLatestNews() {
            try {
                const response = await fetch('/api/news/latest?limit=10');
                const result = await response.json();
                
                if (result.success) {
                    const container = document.getElementById('news-container');
                    
                    if (result.data.length === 0) {
                        container.innerHTML = '<div class="loading">No news articles found</div>';
                        return;
                    }
                    
                    container.innerHTML = result.data.map(article => `
                        <div class="news-item">
                            <div class="news-title">${article.title}</div>
                            <div class="news-meta">
                                📰 ${article.source} • 
                                📅 ${new Date(article.published_date).toLocaleString()}
                                <span class="category-tag">${article.category}</span>
                            </div>
                            <div class="news-content">${article.content}</div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('News load error:', error);
            }
        }
        
        function getStatusIndicator(status) {
            const indicators = {
                'running': '<span class="status-indicator status-running"></span>',
                'stopped': '<span class="status-indicator status-stopped"></span>',
                'starting': '<span class="status-indicator status-starting"></span>'
            };
            return indicators[status] || '<span class="status-indicator status-stopped"></span>';
        }
        
        async function startService() {
            try {
                const response = await fetch('/api/service/start', {method: 'POST'});
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Service started successfully', 'success');
                    setTimeout(loadStatus, 2000);
                } else {
                    showMessage('Failed to start service: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('Error starting service: ' + error.message, 'error');
            }
        }
        
        async function stopService() {
            try {
                const response = await fetch('/api/service/stop', {method: 'POST'});
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Service stopped successfully', 'success');
                    loadStatus();
                } else {
                    showMessage('Failed to stop service: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('Error stopping service: ' + error.message, 'error');
            }
        }
        
        async function manualFetch() {
            try {
                showMessage('Starting manual fetch...', 'info');
                const response = await fetch('/api/fetch/manual', {method: 'POST'});
                const result = await response.json();
                
                if (result.success) {
                    const newArticles = result.data.new_saved || 0;
                    showMessage(`Manual fetch completed: ${newArticles} new articles`, 'success');
                    setTimeout(loadDashboard, 2000);
                } else {
                    showMessage('Manual fetch failed: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('Error during manual fetch: ' + error.message, 'error');
            }
        }
        
        async function exportData() {
            try {
                const response = await fetch('/api/export/csv');
                const result = await response.json();
                
                if (result.success) {
                    showMessage(`Data exported to ${result.filename}`, 'success');
                } else {
                    showMessage('Export failed: ' + result.error, 'error');
                }
            } catch (error) {
                showMessage('Error during export: ' + error.message, 'error');
            }
        }
        
        function showMessage(message, type) {
            // Remove existing messages
            const existing = document.querySelector('.message');
            if (existing) {
                existing.remove();
            }
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = message;
            messageDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                animation: slideIn 0.3s ease;
            `;
            
            if (type === 'success') messageDiv.style.background = '#28a745';
            else if (type === 'error') messageDiv.style.background = '#dc3545';
            else messageDiv.style.background = '#17a2b8';
            
            document.body.appendChild(messageDiv);
            
            setTimeout(() => {
                messageDiv.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => messageDiv.remove(), 300);
            }, 3000);
        }
        
        // CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>'''
    
    with open(os.path.join(template_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    """Main function to start the dashboard."""
    print("🌐 Starting Infosphere News Dashboard...")
    
    # Create template
    create_dashboard_template()
    
    # Start Flask app
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🚀 Starting web server...")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )


if __name__ == "__main__":
    main()