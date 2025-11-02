"""
Database Adapter for Infosphere Complaint Data

This module adapts the existing Infosphere database structure to work with 
the ML pipeline, converting complaint data into training data for news classification.

Author: Infosphere ML Team  
Date: October 2025
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InfosphereDataAdapter:
    """
    Adapter class to connect ML pipeline with existing Infosphere database.
    
    Converts complaint/policy data into training data for news classification.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database adapter.
        
        Args:
            db_path (str, optional): Path to infosphere database
        """
        if db_path is None:
            # Default to infosphere.db in current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            self.db_path = os.path.join(parent_dir, 'infosphere.db')
        else:
            self.db_path = db_path
            
        self.category_mapping = self._setup_category_mapping()
        
    def _setup_category_mapping(self) -> Dict[str, str]:
        """
        Setup mapping from Infosphere categories to ML categories.
        
        Maps complaint categories to Crime/Accident/Event/Weather categories.
        """
        return {
            # Infosphere categories -> ML categories
            'Water': 'Event',
            'Road': 'Accident', 
            'Garbage': 'Event',
            'Security': 'Crime',
            'Traffic': 'Accident',
            'Infrastructure': 'Event',
            'Public Safety': 'Crime',
            'Environment': 'Weather',
            'Emergency': 'Accident',
            'Crime': 'Crime',
            'Accident': 'Accident',
            'Event': 'Event',
            'Weather': 'Weather'
        }
    
    def check_database_exists(self) -> bool:
        """Check if database file exists and is accessible."""
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"❌ Database not found: {self.db_path}")
                return False
                
            # Try to connect and check for tables
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            conn.close()
            
            logger.info(f"✅ Database found with tables: {tables}")
            return len(tables) > 0
            
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            return False
    
    def fetch_complaint_data(self) -> pd.DataFrame:
        """
        Fetch complaint data from Infosphere database.
        
        Returns:
            pd.DataFrame: Complaint data with text and label columns
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Query complaints with relevant fields
            query = """
            SELECT 
                title,
                description, 
                category,
                urgency,
                status,
                created_at,
                location,
                confidence_score
            FROM complaints 
            WHERE category IS NOT NULL 
            AND (title IS NOT NULL OR description IS NOT NULL)
            ORDER BY created_at DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) == 0:
                logger.warning("⚠️  No complaint data found in database")
                return pd.DataFrame()
            
            logger.info(f"✅ Fetched {len(df)} complaints from database")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching complaint data: {e}")
            return pd.DataFrame()
    
    def fetch_policy_data(self) -> pd.DataFrame:
        """
        Fetch policy data from Infosphere database.
        
        Returns:
            pd.DataFrame: Policy data with text and category columns
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
            SELECT 
                title,
                content,
                category,
                ai_summary,
                status,
                created_at
            FROM policies 
            WHERE category IS NOT NULL 
            AND (title IS NOT NULL OR content IS NOT NULL)
            ORDER BY created_at DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"✅ Fetched {len(df)} policies from database")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching policy data: {e}")
            return pd.DataFrame()
    
    def convert_to_training_data(self, complaint_df: pd.DataFrame, policy_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Convert complaint and policy data to ML training format.
        
        Args:
            complaint_df (pd.DataFrame): Complaint data
            policy_df (pd.DataFrame, optional): Policy data
            
        Returns:
            pd.DataFrame: Training data with 'text' and 'label' columns
        """
        training_data = []
        
        # Process complaints
        for _, row in complaint_df.iterrows():
            # Combine title and description as text
            text_parts = []
            if pd.notna(row['title']):
                text_parts.append(str(row['title']))
            if pd.notna(row['description']):
                text_parts.append(str(row['description']))
            
            if not text_parts:
                continue
                
            text = " ".join(text_parts)
            
            # Map category to ML category
            original_category = str(row['category']).strip()
            ml_category = self.category_mapping.get(original_category, 'Event')  # Default to Event
            
            training_data.append({
                'text': text,
                'label': ml_category,
                'original_category': original_category,
                'urgency': row.get('urgency', 'medium'),
                'source': 'complaint'
            })
        
        # Process policies if provided
        if policy_df is not None and len(policy_df) > 0:
            for _, row in policy_df.iterrows():
                text_parts = []
                if pd.notna(row['title']):
                    text_parts.append(str(row['title']))
                if pd.notna(row['ai_summary']):
                    text_parts.append(str(row['ai_summary']))
                elif pd.notna(row['content']):
                    # Use first 200 chars of content if no summary
                    content = str(row['content'])[:200]
                    text_parts.append(content)
                
                if not text_parts:
                    continue
                    
                text = " ".join(text_parts)
                
                # Map policy category 
                original_category = str(row['category']).strip() if pd.notna(row['category']) else 'Event'
                ml_category = self.category_mapping.get(original_category, 'Event')
                
                training_data.append({
                    'text': text,
                    'label': ml_category,
                    'original_category': original_category,
                    'urgency': 'medium',
                    'source': 'policy'
                })
        
        df = pd.DataFrame(training_data)
        
        if len(df) > 0:
            logger.info(f"✅ Converted to {len(df)} training examples")
            logger.info(f"📊 Label distribution: {df['label'].value_counts().to_dict()}")
        
        return df[['text', 'label']]  # Return only required columns for ML
    
    def get_database_stats(self) -> Dict:
        """
        Get statistics about the database content.
        
        Returns:
            Dict: Database statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            stats = {}
            
            # Complaint stats
            complaint_query = """
            SELECT 
                category,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence
            FROM complaints 
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            """
            
            complaint_stats = pd.read_sql_query(complaint_query, conn)
            stats['complaints'] = {
                'total': len(complaint_stats),
                'by_category': complaint_stats.to_dict('records') if len(complaint_stats) > 0 else []
            }
            
            # Policy stats 
            try:
                policy_query = "SELECT COUNT(*) as total, category FROM policies GROUP BY category"
                policy_stats = pd.read_sql_query(policy_query, conn)
                stats['policies'] = {
                    'total': policy_stats['total'].sum() if len(policy_stats) > 0 else 0,
                    'by_category': policy_stats.to_dict('records') if len(policy_stats) > 0 else []
                }
            except:
                stats['policies'] = {'total': 0, 'by_category': []}
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return {'complaints': {'total': 0}, 'policies': {'total': 0}}


def fetch_user_data():
    """
    Main function to fetch training data from Infosphere database.
    
    This function replaces the simulated data fetching in the ML pipeline.
    
    Returns:
        pd.DataFrame: Training data with 'text' and 'label' columns
    """
    logger.info("🔌 Connecting to Infosphere database...")
    
    try:
        # Initialize adapter
        adapter = InfosphereDataAdapter()
        
        # Check database exists
        if not adapter.check_database_exists():
            logger.warning("⚠️  Infosphere database not found, using fallback data...")
            return _get_fallback_data()
        
        # Get database statistics
        stats = adapter.get_database_stats()
        logger.info(f"📊 Database stats: {stats['complaints']['total']} complaints, {stats['policies']['total']} policies")
        
        # Fetch complaint data
        complaint_df = adapter.fetch_complaint_data()
        
        if len(complaint_df) == 0:
            logger.warning("⚠️  No complaint data available, using fallback...")
            return _get_fallback_data()
        
        # Try to fetch policy data
        policy_df = adapter.fetch_policy_data()
        
        # Convert to training format
        training_df = adapter.convert_to_training_data(complaint_df, policy_df)
        
        if len(training_df) < 5:  # Minimum threshold for training
            logger.warning("⚠️  Insufficient training data, supplementing with fallback...")
            fallback_df = _get_fallback_data()
            training_df = pd.concat([training_df, fallback_df], ignore_index=True)
        
        logger.info(f"✅ Successfully prepared {len(training_df)} training examples")
        return training_df
        
    except Exception as e:
        logger.error(f"❌ Error accessing Infosphere database: {e}")
        logger.info("🔄 Falling back to simulated data...")
        return _get_fallback_data()


def _get_fallback_data():
    """
    Fallback data in case database is not accessible.
    
    Returns:
        pd.DataFrame: Simulated training data
    """
    logger.info("📁 Using fallback simulated data...")
    
    fallback_data = [
        # Crime examples
        ("Security breach at office building", "Crime"),
        ("Theft reported in residential area", "Crime"), 
        ("Vandalism at public property", "Crime"),
        ("Fraud complaint filed by citizen", "Crime"),
        
        # Accident examples
        ("Water pipe burst flooding road", "Accident"),
        ("Traffic accident at intersection", "Accident"),
        ("Fire incident at commercial area", "Accident"),  
        ("Infrastructure collapse reported", "Accident"),
        
        # Event examples
        ("Public health checkup camp", "Event"),
        ("Community waste management drive", "Event"),
        ("Road maintenance work scheduled", "Event"),
        ("Public meeting announcement", "Event"),
        
        # Weather examples  
        ("Heavy rainfall affecting area", "Weather"),
        ("Temperature rise causes discomfort", "Weather"),
        ("Fog disrupts visibility", "Weather"),
        ("Storm warning for region", "Weather")
    ]
    
    return pd.DataFrame(fallback_data, columns=['text', 'label'])


if __name__ == "__main__":
    # Test the adapter
    print("🧪 Testing Infosphere Database Adapter")
    print("=" * 40)
    
    adapter = InfosphereDataAdapter()
    
    # Check database
    if adapter.check_database_exists():
        print("✅ Database connection successful")
        
        # Get stats
        stats = adapter.get_database_stats() 
        print(f"📊 Database contains:")
        print(f"   Complaints: {stats['complaints']['total']}")
        print(f"   Policies: {stats['policies']['total']}")
        
        # Test data fetching
        training_data = fetch_user_data()
        print(f"\n📈 Training data prepared: {len(training_data)} examples")
        if len(training_data) > 0:
            print(training_data['label'].value_counts())
    else:
        print("❌ Database connection failed")