"""
Automated News Fetching Service for Infosphere

This service runs continuously to fetch real-time news from major Indian
news sources, classify them, and integrate with the Infosphere platform.

Features:
- Continuous news monitoring
- Scheduled automated fetching  
- Web dashboard for monitoring
- Integration with existing ML pipeline
- Automatic model retraining with new data

Author: Infosphere Team
Date: October 2025
"""

import os
import sys
import time
import schedule
import threading
import signal
from datetime import datetime, timedelta
import json
import sqlite3
from typing import Dict, List
import logging

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.extend([current_dir, parent_dir, os.path.join(parent_dir, 'backend')])

from realtime_news_fetcher import RealTimeNewsFetcher
from infosphere_db_adapter import InfosphereDataAdapter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsService:
    """
    Automated news fetching and processing service.
    """
    
    def __init__(self):
        self.fetcher = RealTimeNewsFetcher()
        self.adapter = InfosphereDataAdapter()
        self.running = False
        self.stats = {
            'service_started': datetime.now().isoformat(),
            'total_fetch_cycles': 0,
            'total_articles_processed': 0,
            'last_fetch': None,
            'last_error': None,
            'status': 'stopped'
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("🛑 Shutdown signal received")
        self.stop()
    
    def fetch_and_process(self) -> Dict:
        """Single fetch and process cycle."""
        try:
            logger.info("📡 Starting fetch and process cycle...")
            
            # Fetch news
            result = self.fetcher.run_single_fetch()
            
            # Update stats
            self.stats['total_fetch_cycles'] += 1
            self.stats['total_articles_processed'] += result.get('new_saved', 0)
            self.stats['last_fetch'] = datetime.now().isoformat()
            self.stats['status'] = 'active'
            
            # Check if we should retrain the model (if significant new data)
            if result.get('new_saved', 0) >= 10:  # Threshold for retraining
                logger.info("🔄 Sufficient new data - considering model retraining...")
                self._check_and_retrain_model()
            
            return result
            
        except Exception as e:
            error_msg = f"Fetch cycle error: {e}"
            logger.error(f"❌ {error_msg}")
            self.stats['last_error'] = {
                'message': error_msg,
                'timestamp': datetime.now().isoformat()
            }
            return {'status': 'error', 'error': str(e)}
    
    def _check_and_retrain_model(self):
        """Check if model should be retrained with new data."""
        try:
            # Get news data statistics
            news_stats = self.fetcher.get_news_statistics()
            total_articles = news_stats.get('total_articles', 0)
            
            # Simple heuristic: retrain if we have 50+ articles and it's been 24+ hours
            if total_articles >= 50:
                logger.info("🤖 Initiating model retraining with news data...")
                
                # Import and run training
                import subprocess
                
                result = subprocess.run([
                    sys.executable, 
                    os.path.join(parent_dir, 'ml_model', 'train_from_website.py')
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✅ Model retrained successfully with latest news data")
                else:
                    logger.error(f"❌ Model retraining failed: {result.stderr}")
                    
        except Exception as e:
            logger.error(f"❌ Model retraining check failed: {e}")
    
    def setup_schedule(self):
        """Setup the fetching schedule."""
        # Fetch news every 30 minutes
        schedule.every(30).minutes.do(self.fetch_and_process)
        
        # Daily statistics report at 9 AM
        schedule.every().day.at("09:00").do(self._daily_report)
        
        # Weekly model retraining check on Sundays at 2 AM
        schedule.every().sunday.at("02:00").do(self._weekly_retrain)
        
        # Cleanup old articles monthly (keep last 3 months)
        schedule.every().month.do(self._cleanup_old_articles)
        
        logger.info("📅 Schedule configured:")
        logger.info("   • News fetch: Every 30 minutes")
        logger.info("   • Daily report: 9:00 AM")
        logger.info("   • Weekly retrain: Sunday 2:00 AM")
        logger.info("   • Monthly cleanup: 1st of month")
    
    def _daily_report(self):
        """Generate daily statistics report."""
        try:
            stats = self.fetcher.get_news_statistics()
            recent_count = stats.get('recent_24h', 0)
            
            report = f"""
📊 Daily News Service Report - {datetime.now().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Articles processed in last 24h: {recent_count}
📰 Total articles in database: {stats.get('total_articles', 0)}
🔄 Total fetch cycles: {self.stats['total_fetch_cycles']}
⏰ Service uptime: {self._get_uptime()}

📊 Category Distribution:
{self._format_categories(stats.get('ml_categories', {}))}

🌐 Source Distribution:
{self._format_sources(stats.get('sources', {}))}
            """
            
            logger.info(report)
            
            # Save report to file
            report_file = f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(report_file, 'w') as f:
                f.write(report)
                
        except Exception as e:
            logger.error(f"❌ Daily report generation failed: {e}")
    
    def _weekly_retrain(self):
        """Weekly model retraining."""
        logger.info("🗓️ Weekly model retraining initiated...")
        self._check_and_retrain_model()
    
    def _cleanup_old_articles(self):
        """Clean up articles older than 3 months."""
        try:
            conn = sqlite3.connect(self.fetcher.db_path)
            cursor = conn.cursor()
            
            # Delete articles older than 3 months
            cursor.execute('''
                DELETE FROM news_articles 
                WHERE fetched_date < datetime('now', '-3 months')
            ''')
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"🧹 Cleaned up {deleted_count} old articles")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
    
    def _format_categories(self, categories: Dict) -> str:
        """Format category statistics for display."""
        if not categories:
            return "   No data available"
        
        formatted = []
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            formatted.append(f"   {category}: {count}")
        
        return '\n'.join(formatted)
    
    def _format_sources(self, sources: Dict) -> str:
        """Format source statistics for display."""
        if not sources:
            return "   No data available"
        
        formatted = []
        for source, count in list(sorted(sources.items(), key=lambda x: x[1], reverse=True))[:5]:
            formatted.append(f"   {source}: {count}")
        
        return '\n'.join(formatted)
    
    def _get_uptime(self) -> str:
        """Calculate service uptime."""
        start_time = datetime.fromisoformat(self.stats['service_started'])
        uptime = datetime.now() - start_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return f"{days}d {hours}h {minutes}m"
    
    def get_status(self) -> Dict:
        """Get current service status."""
        current_stats = self.stats.copy()
        current_stats.update({
            'uptime': self._get_uptime(),
            'news_stats': self.fetcher.get_news_statistics(),
            'scheduled_jobs': len(schedule.jobs)
        })
        return current_stats
    
    def start(self):
        """Start the news service."""
        if self.running:
            logger.warning("⚠️ Service already running")
            return
        
        logger.info("🚀 Starting Infosphere News Service...")
        
        self.running = True
        self.stats['status'] = 'starting'
        
        # Setup schedule
        self.setup_schedule()
        
        # Run initial fetch
        logger.info("📡 Running initial news fetch...")
        self.fetch_and_process()
        
        self.stats['status'] = 'running'
        logger.info("✅ News service started successfully")
        
        # Main service loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("⌨️ Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ Service error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the news service."""
        if not self.running:
            return
            
        logger.info("🛑 Stopping news service...")
        
        self.running = False
        self.stats['status'] = 'stopped'
        
        # Clear scheduled jobs
        schedule.clear()
        
        logger.info("✅ News service stopped")
    
    def run_interactive_menu(self):
        """Interactive menu for service management."""
        while True:
            print("\n" + "=" * 50)
            print("🌐 Infosphere News Service Manager")
            print("=" * 50)
            print("1. Start Service")
            print("2. Stop Service") 
            print("3. Service Status")
            print("4. Manual Fetch")
            print("5. View Latest News")
            print("6. Export News to CSV")
            print("7. Database Statistics")
            print("8. Run Model Retraining")
            print("0. Exit")
            print("-" * 50)
            
            try:
                choice = input("Select option (0-8): ").strip()
                
                if choice == "0":
                    if self.running:
                        self.stop()
                    print("👋 Goodbye!")
                    break
                    
                elif choice == "1":
                    if not self.running:
                        # Start in background thread
                        service_thread = threading.Thread(target=self.start, daemon=True)
                        service_thread.start()
                        time.sleep(2)  # Give it time to start
                    else:
                        print("⚠️ Service already running")
                        
                elif choice == "2":
                    self.stop()
                    
                elif choice == "3":
                    status = self.get_status()
                    print(f"\n📊 Service Status:")
                    print(f"   Status: {status['status']}")
                    print(f"   Uptime: {status['uptime']}")
                    print(f"   Fetch cycles: {status['total_fetch_cycles']}")
                    print(f"   Articles processed: {status['total_articles_processed']}")
                    print(f"   Last fetch: {status.get('last_fetch', 'Never')}")
                    
                elif choice == "4":
                    print("📡 Running manual fetch...")
                    result = self.fetch_and_process()
                    print(f"✅ Fetch completed: {result.get('new_saved', 0)} new articles")
                    
                elif choice == "5":
                    df = self.fetcher.get_latest_news(hours=6)
                    print(f"\n📰 Latest News (last 6 hours): {len(df)} articles")
                    for _, row in df.head(5).iterrows():
                        print(f"   • {row['title'][:70]}... → {row['ml_category']}")
                        
                elif choice == "6":
                    filename = self.fetcher.export_to_csv()
                    if filename:
                        print(f"📄 Exported to: {filename}")
                    else:
                        print("❌ Export failed")
                        
                elif choice == "7":
                    stats = self.fetcher.get_news_statistics()
                    print(f"\n📊 Database Statistics:")
                    print(f"   Total articles: {stats.get('total_articles', 0)}")
                    print(f"   Recent (24h): {stats.get('recent_24h', 0)}")
                    print(f"   ML categories: {stats.get('ml_categories', {})}")
                    
                elif choice == "8":
                    print("🤖 Running model retraining...")
                    self._check_and_retrain_model()
                    
                else:
                    print("⚠️ Invalid option")
                    
            except KeyboardInterrupt:
                if self.running:
                    self.stop()
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function."""
    print("🌐 Infosphere Real-time News Service")
    print("=" * 40)
    
    service = NewsService()
    
    # Check if arguments provided for direct execution
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            service.start()
        elif command == "status":
            status = service.get_status()
            print(json.dumps(status, indent=2))
        elif command == "fetch":
            result = service.fetch_and_process()
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: start, status, fetch")
    else:
        # Run interactive menu
        service.run_interactive_menu()


if __name__ == "__main__":
    main()