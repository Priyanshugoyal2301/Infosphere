import sqlite3
import pandas as pd

def inspect_database():
    """Inspect the existing database structure and content"""
    try:
        conn = sqlite3.connect('infosphere.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("📊 Available tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Inspect each table
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
            
            # Get sample data
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"  Records: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                sample_data = cursor.fetchall()
                print("  Sample data:")
                for i, row in enumerate(sample_data):
                    print(f"    {i+1}. {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_database()