"""
Drop and recreate opinion tables with updated schema
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.opinion_result import OpinionResult, OpinionKeyword
from app.db.database import Base

# Create engine
engine = create_engine(settings.DATABASE_URL)

print("Dropping existing opinion tables...")
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS opinion_keywords CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS opinion_results CASCADE"))
    conn.commit()
    print("Tables dropped successfully")

# Create tables with new schema
print("\nCreating opinion tables with updated schema...")
OpinionResult.__table__.create(engine, checkfirst=True)
OpinionKeyword.__table__.create(engine, checkfirst=True)

print("\nChecking created tables...")
with engine.connect() as conn:
    # Check opinion_results columns
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'opinion_results'
        ORDER BY ordinal_position
    """))
    
    print("\nopinion_results columns:")
    for row in result:
        print(f"  - {row[0]}: {row[1].upper()}")
    
    # Check if employee_result_id column exists
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'opinion_results' AND column_name = 'employee_result_id'
    """))
    
    if result.fetchone():
        print("\n✓ employee_result_id column created successfully!")
    else:
        print("\n✗ employee_result_id column NOT found!")

print("\nTables recreated successfully!")