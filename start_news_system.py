"""
Infosphere News System - Quick Start Guide

Complete real-time news integration system for Infosphere platform.
This script provides easy access to all components.

Usage:
    python start_news_system.py [option]

Options:
    service     - Start automated news service
    dashboard   - Start web dashboard
    fetch       - Run manual news fetch
    api         - Start FastAPI with news endpoints
    status      - Show system status
    help        - Show this help

Author: Infosphere Team
Date: October 2025
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))


def show_banner():
    """Display system banner."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🌐 Infosphere News System                     ║
║                  Real-time News Integration                      ║
╠══════════════════════════════════════════════════════════════════╣
║  📡 Fetches news from Times of India, Hindustan Times & more    ║
║  🤖 ML-powered automatic categorization                          ║
║  📊 Interactive web dashboard                                    ║  
║  🔄 Automated scheduling & management                            ║
║  🚀 FastAPI integration ready                                   ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def show_help():
    """Show help information."""
    show_banner()
    print("""
📖 AVAILABLE COMMANDS:

🔄 Service Management:
   python start_news_system.py service     - Start automated news service
   python start_news_system.py dashboard   - Launch web dashboard
   python start_news_system.py api         - Start FastAPI server

📡 Manual Operations:  
   python start_news_system.py fetch       - Run single news fetch
   python start_news_system.py status      - Show system status
   python start_news_system.py stats       - Show database statistics

🛠️ Development Tools:
   python start_news_system.py test        - Test system components
   python start_news_system.py export      - Export news to CSV

📚 Direct Access:
   python ml_model/realtime_news_fetcher.py     - Direct news fetcher
   python ml_model/news_service.py              - Service manager
   python ml_model/news_dashboard.py            - Web dashboard
   python backend/main.py                       - FastAPI server

🔗 Integration Endpoints:
   GET  /api/v1/news/latest        - Get latest news
   GET  /api/v1/news/statistics    - Get news statistics  
   GET  /api/v1/news/search        - Search news articles
   POST /api/v1/news/fetch         - Trigger manual fetch
   GET  /api/v1/news/health        - System health check

📊 Web Dashboard: http://localhost:5000
🚀 API Documentation: http://localhost:8000/docs
    """)


def run_service():
    """Start the automated news service."""
    print("🚀 Starting Infosphere News Service...")
    print("📝 This will run continuous news fetching every 30 minutes")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            sys.executable, 
            str(current_dir / "ml_model" / "news_service.py")
        ])
    except KeyboardInterrupt:
        print("\n✋ Service stopped by user")


def run_dashboard():
    """Start the web dashboard."""
    print("📊 Starting Infosphere News Dashboard...")
    print("🌐 Dashboard will be available at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            sys.executable,
            str(current_dir / "ml_model" / "news_dashboard.py")
        ])
    except KeyboardInterrupt:
        print("\n✋ Dashboard stopped by user")


def run_fetch():
    """Run manual news fetch."""
    print("📡 Running manual news fetch...")
    
    result = subprocess.run([
        sys.executable,
        str(current_dir / "ml_model" / "realtime_news_fetcher.py")
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Fetch completed successfully!")
        # Extract key information from output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Fetch cycle completed' in line or 'New Saved:' in line:
                print(f"   {line.strip()}")
    else:
        print("❌ Fetch failed:")
        print(result.stderr)


def run_api():
    """Start FastAPI server with news endpoints."""
    print("🚀 Starting FastAPI server with news integration...")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            sys.executable,
            str(current_dir / "backend" / "main.py")
        ])
    except KeyboardInterrupt:
        print("\n✋ API server stopped by user")


def show_status():
    """Show system status."""
    print("📊 Infosphere News System Status:")
    print("=" * 50)
    
    # Check database
    try:
        from ml_model.realtime_news_fetcher import RealTimeNewsFetcher
        fetcher = RealTimeNewsFetcher()
        stats = fetcher.get_news_statistics()
        
        print(f"📰 Total Articles: {stats.get('total_articles', 0)}")
        print(f"📅 Recent (24h): {stats.get('recent_24h', 0)}")
        print(f"📊 Categories: {len(stats.get('ml_categories', {}))}")
        print(f"🌐 Sources: {len(stats.get('sources', {}))}")
        
        if stats.get('ml_categories'):
            print("\n📋 Category Distribution:")
            for category, count in stats['ml_categories'].items():
                print(f"   • {category}: {count}")
                
    except Exception as e:
        print(f"❌ Error checking system: {e}")
    
    # Check files
    print(f"\n📁 System Files:")
    files_to_check = [
        "ml_model/realtime_news_fetcher.py",
        "ml_model/news_service.py", 
        "ml_model/news_dashboard.py",
        "backend/api/v1/endpoints/news.py"
    ]
    
    for file_path in files_to_check:
        full_path = current_dir / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"   {status} {file_path}")


def run_test():
    """Test system components."""
    print("🧪 Testing Infosphere News System Components...")
    print("=" * 50)
    
    # Test 1: Import check
    print("1️⃣ Testing imports...")
    try:
        from ml_model.realtime_news_fetcher import RealTimeNewsFetcher
        from ml_model.news_service import NewsService
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return
    
    # Test 2: Database connectivity
    print("2️⃣ Testing database connectivity...")
    try:
        fetcher = RealTimeNewsFetcher()
        stats = fetcher.get_news_statistics()
        print(f"   ✅ Database connected ({stats.get('total_articles', 0)} articles)")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    # Test 3: ML model loading
    print("3️⃣ Testing ML model...")
    try:
        from backend.infosphere_db_adapter import InfosphereDataAdapter
        adapter = InfosphereDataAdapter()
        adapter.load_model()
        print("   ✅ ML model loaded successfully")
    except Exception as e:
        print(f"   ⚠️ ML model warning: {e}")
    
    # Test 4: Service creation
    print("4️⃣ Testing service creation...")
    try:
        service = NewsService()
        status = service.get_status()
        print(f"   ✅ Service created (status: {status['status']})")
    except Exception as e:
        print(f"   ❌ Service error: {e}")
    
    print("\n🎉 System test completed!")


def export_data():
    """Export news data to CSV."""
    print("📄 Exporting news data...")
    
    try:
        from ml_model.realtime_news_fetcher import RealTimeNewsFetcher
        fetcher = RealTimeNewsFetcher()
        filename = fetcher.export_to_csv()
        
        if filename:
            print(f"✅ Data exported to: {filename}")
        else:
            print("❌ Export failed")
            
    except Exception as e:
        print(f"❌ Export error: {e}")


def show_stats():
    """Show detailed statistics."""
    print("📊 Infosphere News Database Statistics:")
    print("=" * 60)
    
    try:
        from ml_model.realtime_news_fetcher import RealTimeNewsFetcher
        fetcher = RealTimeNewsFetcher()
        stats = fetcher.get_news_statistics()
        
        print(f"📰 Total Articles: {stats.get('total_articles', 0)}")
        print(f"📅 Recent (24h): {stats.get('recent_24h', 0)}")
        print(f"📅 Recent (7d): {stats.get('recent_7d', 0)}")
        
        print(f"\n📊 Categories ({len(stats.get('ml_categories', {}))}):")
        for category, count in sorted(stats.get('ml_categories', {}).items(), 
                                    key=lambda x: x[1], reverse=True):
            percentage = count / max(stats.get('total_articles', 1), 1) * 100
            print(f"   • {category:15} : {count:3d} ({percentage:5.1f}%)")
            
        print(f"\n🌐 Sources ({len(stats.get('sources', {}))}):")
        for source, count in list(sorted(stats.get('sources', {}).items(), 
                                       key=lambda x: x[1], reverse=True))[:10]:
            print(f"   • {source:20} : {count:3d}")
            
        if stats.get('locations'):
            print(f"\n📍 Locations ({len(stats.get('locations', {}))}):")
            for location, count in list(sorted(stats.get('locations', {}).items(), 
                                             key=lambda x: x[1], reverse=True))[:5]:
                print(f"   • {location:15} : {count:3d}")
                
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "service":
        run_service()
    elif command == "dashboard":
        run_dashboard()
    elif command == "fetch":
        run_fetch()
    elif command == "api":
        run_api()
    elif command == "status":
        show_status()
    elif command == "stats":
        show_stats()
    elif command == "test":
        run_test()
    elif command == "export":
        export_data()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        print("📖 Use 'python start_news_system.py help' for available commands")


if __name__ == "__main__":
    main()