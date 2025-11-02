"""
Backend Database Connector for User News Submissions

This module simulates database operations for fetching user-submitted news data.
In a production environment, this would connect to your actual database
(PostgreSQL, MySQL, MongoDB, etc.) and fetch real user submissions.

Author: Infosphere Backend Team  
Date: October 2025
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import random


class NewsDataConnector:
    """
    Handles database connections and data retrieval for news submissions.
    
    In production, this would connect to your actual database system.
    For demonstration, it creates and manages a local SQLite database.
    """
    
    def __init__(self, db_path=None):
        """
        Initialize database connector.
        
        Args:
            db_path (str, optional): Path to database file
        """
        if db_path is None:
            # Use infosphere.db from the parent directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            self.db_path = os.path.join(parent_dir, 'infosphere.db')
        else:
            self.db_path = db_path
            
        self._initialize_database()
    
    def _initialize_database(self):
        """
        Initialize database with sample user submissions if not exists.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    label TEXT,
                    user_id TEXT,
                    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    location TEXT
                )
            ''')
            
            # Check if table is empty and populate with sample data
            cursor.execute('SELECT COUNT(*) FROM user_submissions')
            count = cursor.fetchone()[0]
            
            if count == 0:
                self._populate_sample_data(cursor)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def _populate_sample_data(self, cursor):
        """
        Populate database with realistic sample user submissions.
        
        Args:
            cursor: Database cursor object
        """
        sample_submissions = [
            # Crime reports
            ("Bike theft reported near metro station", "Crime", "user001", "Sector 14"),
            ("Chain snatching incident at bus stop", "Crime", "user002", "MG Road"),
            ("Purse stolen from market area", "Crime", "user003", "City Center"),
            ("Break-in attempt at apartment complex", "Crime", "user004", "Residency Road"),
            ("Phone snatching case during evening", "Crime", "user005", "Park Street"),
            
            # Accident reports  
            ("Car accident at traffic signal", "Accident", "user006", "Main Road"),
            ("Fire in electrical shop", "Accident", "user007", "Commercial Street"),
            ("Gas leakage in residential building", "Accident", "user008", "Housing Society"),
            ("Tree fell on parked vehicles", "Accident", "user009", "Green Avenue"),
            ("Water logging after pipe burst", "Accident", "user010", "Old City"),
            
            # Event announcements
            ("Free eye checkup camp tomorrow", "Event", "user011", "Community Hall"),
            ("Blood donation drive this weekend", "Event", "user012", "Hospital Campus"),
            ("Cooking competition registration open", "Event", "user013", "Cultural Center"),
            ("Yoga classes starting next week", "Event", "user014", "Sports Complex"),
            ("Career fair for engineering students", "Event", "user015", "College Grounds"),
            
            # Weather updates
            ("Heavy rain warning for next two days", "Weather", "user016", "City Wide"),
            ("Temperature touching 40 degrees today", "Weather", "user017", "Weather Station"),
            ("Fog affecting morning visibility", "Weather", "user018", "Highway Route"),
            ("Strong winds causing dust storms", "Weather", "user019", "Open Areas"),
            ("Humidity making weather uncomfortable", "Weather", "user020", "Residential Areas"),
        ]
        
        # Insert sample data with timestamps
        for i, (text, label, user_id, location) in enumerate(sample_submissions):
            submission_date = datetime.now() - timedelta(days=random.randint(0, 30))
            cursor.execute('''
                INSERT INTO user_submissions (text, label, user_id, submission_date, is_verified, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (text, label, user_id, submission_date, True, location))
    
    def fetch_all_submissions(self, include_unlabeled=False):
        """
        Fetch all user submissions from database.
        
        Args:
            include_unlabeled (bool): Whether to include submissions without labels
            
        Returns:
            pd.DataFrame: DataFrame with submission data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            if include_unlabeled:
                query = '''
                    SELECT text, label, user_id, submission_date, location 
                    FROM user_submissions 
                    ORDER BY submission_date DESC
                '''
            else:
                query = '''
                    SELECT text, label, user_id, submission_date, location 
                    FROM user_submissions 
                    WHERE label IS NOT NULL 
                    ORDER BY submission_date DESC
                '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"Error fetching submissions: {e}")
            return pd.DataFrame()
    
    def fetch_recent_submissions(self, days=7):
        """
        Fetch submissions from last N days.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            pd.DataFrame: Recent submissions
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT text, label, user_id, submission_date, location 
                FROM user_submissions 
                WHERE submission_date >= datetime('now', '-{} days')
                AND label IS NOT NULL
                ORDER BY submission_date DESC
            '''.format(days)
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            print(f"Error fetching recent submissions: {e}")
            return pd.DataFrame()
    
    def add_submission(self, text, user_id, location=None, label=None):
        """
        Add new user submission to database.
        
        Args:
            text (str): Submission text
            user_id (str): User identifier  
            location (str, optional): Location information
            label (str, optional): Pre-classified label
            
        Returns:
            int: ID of inserted record
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_submissions (text, user_id, location, label)
                VALUES (?, ?, ?, ?)
            ''', (text, user_id, location, label))
            
            submission_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return submission_id
            
        except Exception as e:
            print(f"Error adding submission: {e}")
            return None
    
    def update_submission_label(self, submission_id, label):
        """
        Update label for existing submission (for manual verification).
        
        Args:
            submission_id (int): Submission ID
            label (str): Verified label
            
        Returns:
            bool: Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_submissions 
                SET label = ?, is_verified = TRUE 
                WHERE id = ?
            ''', (label, submission_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error updating submission: {e}")
            return False
    
    def get_label_distribution(self):
        """
        Get distribution of labels in database.
        
        Returns:
            dict: Label counts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT label, COUNT(*) as count 
                FROM user_submissions 
                WHERE label IS NOT NULL 
                GROUP BY label
                ORDER BY count DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return dict(zip(df['label'], df['count']))
            
        except Exception as e:
            print(f"Error getting label distribution: {e}")
            return {}


def fetch_user_data():
    """
    Main function to fetch user data for model training.
    This is the function called by the training pipeline.
    
    Returns:
        pd.DataFrame: User submission data with 'text' and 'label' columns
    """
    print("🔌 Connecting to user submissions database...")
    
    try:
        # Initialize database connector
        db_connector = NewsDataConnector()
        
        # Fetch all labeled submissions
        df = db_connector.fetch_all_submissions(include_unlabeled=False)
        
        if len(df) == 0:
            print("⚠️  No labeled data found in database, using simulated data...")
            # Fallback to simulated data if database is empty
            return _get_simulated_data()
        
        # Keep only text and label columns for training
        df = df[['text', 'label']].copy()
        
        print(f"✅ Fetched {len(df)} labeled submissions from database")
        print(f"📊 Label distribution: {df['label'].value_counts().to_dict()}")
        
        return df
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("🔄 Falling back to simulated data...")
        return _get_simulated_data()


def _get_simulated_data():
    """
    Fallback simulated data if database connection fails.
    
    Returns:
        pd.DataFrame: Simulated user submission data
    """
    sample_data = [
        ("Fire near MG Road junction", "Accident"),
        ("Free vaccination camp tomorrow", "Event"), 
        ("Heavy rain warning issued", "Weather"),
        ("Theft reported at shopping mall", "Crime"),
        ("Car accident on highway", "Accident"),
        ("Blood donation drive announced", "Event"),
        ("Temperature rising significantly", "Weather"),
        ("Chain snatching at bus stop", "Crime"),
        ("Gas leakage in apartment", "Accident"),
        ("Cultural festival next week", "Event"),
        ("Thunderstorm expected tonight", "Weather"),
        ("Burglary attempt failed", "Crime"),
    ]
    
    return pd.DataFrame(sample_data, columns=['text', 'label'])


if __name__ == "__main__":
    # Test the database connector
    print("🧪 Testing Database Connector")
    print("=" * 30)
    
    connector = NewsDataConnector()
    
    # Test fetching data
    df = fetch_user_data()
    print(f"\nFetched {len(df)} records")
    print(df.head())
    
    # Test label distribution
    distribution = connector.get_label_distribution()
    print(f"\nLabel distribution: {distribution}")