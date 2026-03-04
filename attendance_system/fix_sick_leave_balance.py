#!/usr/bin/env python3
"""
Fix script to add sick_leave_balance column to staff table
Run this on the Contabo server to fix the database
"""

import os
import sys

# Try to import from the app - handles both SQLite and other DBs
try:
    from app import db, Staff
    from main import app
    
    with app.app_context():
        # Check if column exists by trying to access it
        try:
            staff = Staff.query.first()
            print("sick_leave_balance column exists!")
        except Exception as e:
            print(f"Error: {e}")
            print("Attempting to add column...")
            
            # For SQLite, we need to recreate table
            if 'sqlite' in str(db.engine.url):
                print("Detected SQLite database")
                # Add column using raw SQL
                try:
                    db.session.execute(db.text('ALTER TABLE staff ADD COLUMN sick_leave_balance REAL DEFAULT 0'))
                    db.session.commit()
                    print("Added sick_leave_balance column successfully!")
                except Exception as sqle:
                    print(f"SQL Error: {sqle}")
            else:
                print("Please add the column manually to your database")
                
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run this script from the project directory with proper environment")
except Exception as e:
    print(f"Error: {e}")
    print("Database may need manual migration")
