"""
Infosphere ML Model Management Tool

This tool helps manage the ML pipeline with your existing Infosphere database:
- Add new training data from complaints
- Retrain the model with updated data  
- Test model performance
- Monitor database statistics

Author: Infosphere Team
Date: October 2025
"""

import sys
import os
import sqlite3
from datetime import datetime
import pandas as pd

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

from backend.infosphere_db_adapter import InfosphereDataAdapter
from backend.analyze_input import analyze_news_input, get_model_status


class InfosphereMLManager:
    """Management tool for Infosphere ML pipeline."""
    
    def __init__(self):
        self.adapter = InfosphereDataAdapter()
        
    def show_database_stats(self):
        """Display current database statistics."""
        print("📊 Infosphere Database Statistics")
        print("-" * 35)
        
        if not self.adapter.check_database_exists():
            print("❌ Database not accessible")
            return
            
        stats = self.adapter.get_database_stats()
        
        print(f"Total Complaints: {stats['complaints']['total']}")
        print(f"Total Policies: {stats['policies']['total']}")
        
        print("\n📈 Complaints by Category:")
        for category_info in stats['complaints']['by_category']:
            print(f"  {category_info['category']}: {category_info['count']} (avg confidence: {category_info['avg_confidence']:.3f})")
        
        print("\n📋 Policies by Category:")
        for category_info in stats['policies']['by_category']:
            print(f"  {category_info['category']}: {category_info['total']}")
    
    def show_training_data_preview(self):
        """Show preview of current training data."""
        print("\n🔍 Current Training Data Preview")
        print("-" * 35)
        
        # Get training data
        complaint_df = self.adapter.fetch_complaint_data()
        policy_df = self.adapter.fetch_policy_data()
        
        if len(complaint_df) == 0:
            print("⚠️  No complaint data available")
            return
            
        training_df = self.adapter.convert_to_training_data(complaint_df, policy_df)
        
        print(f"📊 Total training examples: {len(training_df)}")
        print(f"📈 Label distribution: {training_df['label'].value_counts().to_dict()}")
        
        print("\n📋 Sample training data:")
        for i, (_, row) in enumerate(training_df.head(5).iterrows()):
            print(f"  {i+1}. {row['text'][:60]}... → {row['label']}")
    
    def test_current_model(self):
        """Test the current model with sample inputs."""
        print("\n🧪 Testing Current Model")
        print("-" * 25)
        
        status = get_model_status()
        if not status['model_loaded']:
            print("❌ No trained model found. Please train first.")
            return
            
        print(f"Model Status: {status['status']}")
        print(f"Training Date: {status.get('training_date', 'Unknown')}")
        print(f"Accuracy: {status.get('accuracy', 'Unknown')}")
        
        # Test with Infosphere-style inputs
        test_cases = [
            ("Water leakage in residential area causing inconvenience", "Event"),
            ("Chain snatching incident reported in market area", "Crime"),
            ("Traffic signal malfunction creating congestion", "Accident"), 
            ("Air pollution from factory smoke affecting health", "Weather"),
            ("Illegal waste dumping in park area", "Event"),
            ("Street lights not working creating safety concerns", "Crime")
        ]
        
        print("\n🎯 Classification Results:")
        correct = 0
        for text, expected in test_cases:
            result = analyze_news_input(text)
            if 'error' not in result:
                predicted = result['category']
                confidence = result['confidence']
                is_correct = predicted == expected
                if is_correct:
                    correct += 1
                    
                status_icon = "✅" if is_correct else "⚠️"
                print(f"  {status_icon} '{text[:50]}...' → {predicted} ({confidence:.3f})")
            else:
                print(f"  ❌ Error: {result['error']}")
        
        accuracy = correct / len(test_cases) if test_cases else 0
        print(f"\n📈 Test Accuracy: {accuracy:.2%} ({correct}/{len(test_cases)})")
    
    def add_sample_complaint(self, title, description, category, urgency="medium"):
        """Add a new complaint to the database."""
        try:
            conn = sqlite3.connect(self.adapter.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO complaints 
                (title, description, category, urgency, confidence_score, status, created_at, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, category, urgency, 0.85, 'submitted', datetime.now(), 'User Added'))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added complaint: '{title}' → {category}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding complaint: {e}")
            return False
    
    def retrain_model(self):
        """Retrain the ML model with current database."""
        print("\n🚀 Retraining Model with Current Data")
        print("-" * 35)
        
        import subprocess
        
        try:
            # Run training script
            result = subprocess.run([
                sys.executable, 
                'ml_model/train_from_website.py'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Model retraining completed successfully!")
                return True
            else:
                print(f"❌ Training failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error during retraining: {e}")
            return False
    
    def interactive_menu(self):
        """Interactive menu for managing the ML pipeline."""
        while True:
            print("\n" + "=" * 50)
            print("🤖 Infosphere ML Management Tool")
            print("=" * 50)
            print("1. Show Database Statistics")
            print("2. Preview Training Data")
            print("3. Test Current Model")  
            print("4. Add Sample Complaint")
            print("5. Retrain Model")
            print("6. Run Full Integration Tests")
            print("0. Exit")
            print("-" * 50)
            
            try:
                choice = input("Select option (0-6): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.show_database_stats()
                elif choice == "2":
                    self.show_training_data_preview()
                elif choice == "3":
                    self.test_current_model()
                elif choice == "4":
                    self.add_complaint_interactive()
                elif choice == "5":
                    success = self.retrain_model()
                    if success:
                        print("🎉 Model retrained! Testing new model...")
                        self.test_current_model()
                elif choice == "6":
                    self.run_integration_tests()
                else:
                    print("⚠️  Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def add_complaint_interactive(self):
        """Interactive complaint addition."""
        print("\n📝 Add New Complaint")
        print("-" * 20)
        
        try:
            title = input("Title: ").strip()
            if not title:
                print("❌ Title required")
                return
                
            description = input("Description: ").strip()
            if not description:
                print("❌ Description required")
                return
            
            print("\nCategories: Water, Road, Garbage, Security, Public Safety, Environment")
            category = input("Category: ").strip()
            if not category:
                category = "Public Safety"  # Default
            
            print("\nUrgency levels: low, medium, high, critical")
            urgency = input("Urgency (default: medium): ").strip()
            if not urgency:
                urgency = "medium"
            
            success = self.add_sample_complaint(title, description, category, urgency)
            if success:
                print("\n💡 Tip: Retrain the model (option 5) to use this new data!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_integration_tests(self):
        """Run the full integration test suite."""
        print("\n🧪 Running Integration Tests")
        print("-" * 28)
        
        try:
            import subprocess
            
            result = subprocess.run([
                sys.executable, 
                'test_ml_pipeline.py'
            ], capture_output=False, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False


def main():
    """Main function."""
    print("🤖 Infosphere ML Pipeline Manager")
    print("=" * 35)
    
    manager = InfosphereMLManager()
    
    # Check if we can access the database
    if not manager.adapter.check_database_exists():
        print("❌ Cannot access Infosphere database")
        print("Please ensure infosphere.db exists and is accessible")
        return
    
    print("✅ Connected to Infosphere database")
    
    # Show quick stats
    manager.show_database_stats()
    
    # Start interactive menu
    manager.interactive_menu()


if __name__ == "__main__":
    main()