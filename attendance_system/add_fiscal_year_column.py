"""Migration script to add fiscal_year column to leave_requests table"""
from app import app, db

def add_fiscal_year_column():
    with app.app_context():
        # Add column using raw SQL
        try:
            db.session.execute(db.text("""
                ALTER TABLE leave_requests 
                ADD COLUMN fiscal_year INTEGER;
            """))
            db.session.commit()
            print("✅ Successfully added fiscal_year column to leave_requests table")
        except Exception as e:
            # Check if column already exists
            if 'duplicate' in str(e).lower() or 'already exists' in str(e).lower():
                print("ℹ️  Column already exists")
            else:
                print(f"❌ Error: {e}")
                db.session.rollback()

if __name__ == '__main__':
    add_fiscal_year_column()
