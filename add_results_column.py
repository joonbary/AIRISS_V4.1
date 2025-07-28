# -*- coding: utf-8 -*-
"""
Add results_data column to jobs table
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_results_column():
    print("Adding results_data column to jobs table...")
    
    # Connect to database
    database_url = settings.DATABASE_URL or "sqlite:///./airiss.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {})
    
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(jobs)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'results_data' not in columns:
                print("Adding results_data column...")
                conn.execute(text("ALTER TABLE jobs ADD COLUMN results_data TEXT"))
                conn.commit()
                print("✅ results_data column added successfully")
            else:
                print("✅ results_data column already exists")
                
    except Exception as e:
        print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_results_column()