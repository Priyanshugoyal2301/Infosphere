"""
Sample Data Populator for Infosphere Database

This script adds realistic sample complaint and policy data to the existing
Infosphere database to enable ML model training with real data structure.

Author: Infosphere Team
Date: October 2025
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random


def populate_sample_complaints():
    """Add sample complaint data to the existing database."""
    
    # Sample complaint data with realistic examples
    sample_complaints = [
        # Water category complaints  
        ("Water leakage in residential area", "Water supply disruption causing inconvenience to residents. Pipe burst near sector 12 affecting multiple households. Urgent repair needed.", "Water", "high", "Downtown", "9876543210"),
        ("Contaminated water supply reported", "Water quality issues reported by multiple residents. Strange smell and color in tap water. Health concerns raised by community.", "Water", "critical", "Sector 15", "9876543211"),
        ("Low water pressure complaint", "Insufficient water pressure in apartment complex. Residents facing difficulty in daily activities due to poor water flow.", "Water", "medium", "Residential Area", "9876543212"),
        
        # Road category complaints
        ("Pothole on main road causing accidents", "Large potholes on busy intersection creating safety hazards. Multiple vehicle damages reported. Immediate repair required.", "Road", "high", "Main Street", "9876543213"),
        ("Traffic signal malfunction", "Traffic lights not working properly at major junction. Creating traffic congestion and accident risks during peak hours.", "Road", "critical", "Central Square", "9876543214"),
        ("Road construction blocking traffic", "Ongoing road work causing severe traffic jams. No alternative routes provided. Commuters facing daily delays.", "Road", "medium", "Highway Route", "9876543215"),
        
        # Garbage category complaints
        ("Garbage collection not done for days", "Waste accumulation in residential colony. Garbage trucks haven't arrived for over a week. Creating health hazards.", "Garbage", "high", "Colony A", "9876543216"),
        ("Illegal waste dumping in open area", "Construction debris being dumped illegally near park. Environmental damage and aesthetic concerns raised by locals.", "Garbage", "medium", "Near Park", "9876543217"),
        ("Overflowing dustbins creating mess", "Public dustbins overflowing on main road. Waste scattered by stray animals. Sanitation issues in commercial area.", "Garbage", "medium", "Market Street", "9876543218"),
        
        # Security category complaints
        ("Street lights not working in colony", "Multiple street lights out of order creating safety concerns. Increased crime risk in dark areas during night time.", "Security", "high", "Residential Colony", "9876543219"),
        ("Suspicious activity reported at night", "Unknown individuals loitering near residential area. Residents feeling unsafe. Security patrol requested for area.", "Security", "high", "Sector 8", "9876543220"),
        ("Chain snatching incident reported", "Multiple chain snatching cases reported in market area. Women feeling unsafe during evening hours. Police intervention needed.", "Security", "critical", "Market Area", "9876543221"),
        
        # Public Safety complaints
        ("Stray dogs creating nuisance", "Aggressive stray dogs in park area. Children and elderly people scared to visit. Animal control measures needed.", "Public Safety", "medium", "City Park", "9876543222"),
        ("Open manhole without cover", "Dangerous open drainage near school. Safety hazard for students and pedestrians. Immediate covering required.", "Public Safety", "critical", "School Area", "9876543223"),
        ("Electric pole damaged in storm", "Electrical pole tilted after recent storm. Live wires hanging dangerously low. Risk of electrocution reported.", "Public Safety", "critical", "Residential Road", "9876543224"),
        
        # Environment complaints  
        ("Air pollution from factory smoke", "Industrial emissions causing respiratory problems. Thick smoke visible throughout the day. Environmental clearance questioned.", "Environment", "high", "Industrial Area", "9876543225"),
        ("Noise pollution from construction", "Construction work continuing late night. Sleep disturbance reported by residents. Noise levels exceeding permitted limits.", "Environment", "medium", "Apartment Complex", "9876543226"),
        ("Tree cutting without permission", "Large trees being cut illegally for commercial project. Environmental activists protesting. Forest department intervention needed.", "Environment", "high", "Green Belt", "9876543227"),
    ]
    
    return sample_complaints


def populate_sample_policies():
    """Add sample policy data to the existing database."""
    
    sample_policies = [
        ("Water Conservation Policy 2025", "Mandatory rainwater harvesting for all new constructions. Water recycling systems to be installed in residential complexes above 50 units. Penalties for water wastage during shortage periods.", "Water", "Guidelines for sustainable water usage and conservation in urban areas"),
        
        ("Traffic Management Guidelines", "New traffic rules for peak hours. Odd-even vehicle scheme during pollution alerts. Enhanced public transport facilities to reduce private vehicle usage.", "Road", "Comprehensive traffic management system for city infrastructure"),
        
        ("Waste Management Protocol", "Segregation of waste at source mandatory. Penalties for improper garbage disposal. Reward system for communities maintaining cleanliness standards.", "Garbage", "Sustainable waste management and recycling initiatives"),
        
        ("Public Safety Enhancement Plan", "Increased police patrolling in residential areas. Installation of CCTV cameras at vulnerable locations. Emergency response system upgrade for faster assistance.", "Security", "Comprehensive safety measures for citizen protection"),
        
        ("Environmental Protection Act", "Stricter emission norms for industries. Green building certification mandatory for commercial projects. Tree plantation drives in all development projects.", "Environment", "Environmental conservation and pollution control measures"),
    ]
    
    return sample_policies


def insert_complaints_to_db(db_path):
    """Insert sample complaints into the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        complaints = populate_sample_complaints()
        
        # Insert complaints
        for i, (title, description, category, urgency, location, contact) in enumerate(complaints):
            # Random confidence score between 0.7-0.95
            confidence = round(random.uniform(0.70, 0.95), 3)
            
            # Random creation date within last 30 days
            days_ago = random.randint(0, 30)
            created_at = datetime.now() - timedelta(days=days_ago)
            
            # Random status
            status = random.choice(['submitted', 'in_progress', 'resolved'])
            
            cursor.execute('''
                INSERT INTO complaints 
                (title, description, category, urgency, confidence_score, status, created_at, location, contact_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, category, urgency, confidence, status, created_at, location, contact))
        
        conn.commit()
        print(f"✅ Inserted {len(complaints)} complaint records")
        
        # Show inserted data
        cursor.execute('SELECT COUNT(*), category FROM complaints GROUP BY category')
        results = cursor.fetchall()
        print("📊 Complaints by category:")
        for count, category in results:
            print(f"   {category}: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error inserting complaints: {e}")
        return False


def insert_policies_to_db(db_path):
    """Insert sample policies into the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        policies = populate_sample_policies()
        
        # Insert policies
        for title, content, category, ai_summary in policies:
            created_at = datetime.now() - timedelta(days=random.randint(0, 60))
            status = random.choice(['draft', 'active', 'archived'])
            
            cursor.execute('''
                INSERT INTO policies 
                (title, content, category, ai_summary, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, content, category, ai_summary, status, created_at))
        
        conn.commit()
        print(f"✅ Inserted {len(policies)} policy records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error inserting policies: {e}")
        return False


def main():
    """Main function to populate sample data."""
    print("🗃️ Populating Infosphere Database with Sample Data")
    print("=" * 50)
    
    # Database path
    db_path = "infosphere.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Please ensure the Infosphere database exists first.")
        return False
    
    print(f"📁 Using database: {db_path}")
    
    # Insert sample data
    print("\n📋 Inserting sample complaints...")
    complaints_success = insert_complaints_to_db(db_path)
    
    print("\n📋 Inserting sample policies...")
    policies_success = insert_policies_to_db(db_path)
    
    if complaints_success and policies_success:
        print("\n🎉 Sample data insertion completed successfully!")
        print("\n📈 Ready for ML model training with real data!")
        print("Run: python ml_model/train_from_website.py")
        return True
    else:
        print("\n❌ Some data insertion failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🔍 Testing database adapter with new data...")
        try:
            import sys
            sys.path.append('backend')
            from infosphere_db_adapter import fetch_user_data
            
            # Test data fetching
            training_data = fetch_user_data()
            print(f"✅ Training data prepared: {len(training_data)} examples")
            if len(training_data) > 0:
                print("📊 Label distribution:")
                print(training_data['label'].value_counts())
        except Exception as e:
            print(f"⚠️ Could not test adapter: {e}")