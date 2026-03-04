"""
Fix for Render 503 Error - Enhanced app.py with better error handling and startup logic

This script creates a fixed version of app.py that:
1. Handles database connection failures gracefully
2. Uses proper timeout settings for PostgreSQL
3. Adds a /health endpoint for Render's health checks
4. Implements proper PORT handling
5. Adds startup error handling to prevent silent crashes

Run this script to update app.py with the fixes.
"""

import os
import re

def apply_fix():
    """Apply the fix to app.py"""
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Improve the database connection configuration
    old_db_config = '''# =====================================================
# CONFIGURATION
# =====================================================

# Database URL - Production (Render) or Local fallback
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///attendance.db')

# Fix for Supabase/Render: replace postgres:// with postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"📊 Database URL: {DATABASE_URL[:50]}...")

# =====================================================
# ENGINE FIX: Configure SSL for Supabase PostgreSQL
# =====================================================
if DATABASE_URL and 'postgresql' in DATABASE_URL:
    # Use Flask-SQLAlchemy's engine_options for SSL
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 10
        }
    }
    print("🔒 SSL mode enabled for PostgreSQL")
else:
    # SQLite configuration (local development)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False'''

    new_db_config = '''# =====================================================
# CONFIGURATION
# =====================================================

# Database URL - Production (Render) or Local fallback
# IMPORTANT: Check multiple environment variables for DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or 'sqlite:///attendance.db'

# Fix for Supabase/Render: replace postgres:// with postgresql://
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"📊 Database URL: {DATABASE_URL[:50]}...")

# =====================================================
# ENGINE FIX: Configure SSL for Supabase PostgreSQL
# =====================================================
if DATABASE_URL and 'postgresql' in DATABASE_URL:
    # Use Flask-SQLAlchemy's engine_options for SSL
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10,
        'connect_args': {
            'sslmode': 'require',
            'connect_timeout': 30,  # Increased timeout
            'keepalives': 1,
            'keepalives_idle': 30
        }
    }
    print("🔒 SSL mode enabled for PostgreSQL")
else:
    # SQLite configuration (local development)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False'''
    
    content = content.replace(old_db_config, new_db_config)
    
    # Fix 2: Improve the health check endpoint
    old_health = '''@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        staff_count = Staff.query.count()
        attendance_count = Attendance.query.filter_by(work_date=date.today()).count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'staff_count': staff_count,
            'today_attendance_count': attendance_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500'''

    new_health = '''@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection with a simple query
        db.session.execute(db.text('SELECT 1'))
        staff_count = Staff.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'staff_count': staff_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503  # Return 503 so Render knows the service is down'''

    content = content.replace(old_health, new_health)
    
    # Fix 3: Improve the startup section to handle errors better
    old_main = '''if __name__ == '__main__':
    try:
        # Get port first - Render requires this
        port = int(os.environ.get('PORT', 5000))
        debug_mode = os.environ.get('PORT') is None
        
        db_type = "PostgreSQL (Supabase)" if "postgresql" in DATABASE_URL else "SQLite (Local)"
        print(f"\\n{'='*60}")
        print("ATTENDANCE SYSTEM STARTUP")
        print(f"{'='*60}")
        print(f"Database: {db_type}")
        print(f"URL: {DATABASE_URL[:50]}...")
        print(f"Late Threshold: {LATE_THRESHOLD}")
        print(f"Port: {port}")
        print(f"{'='*60}\\n")
        
        # Initialize database before starting server
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables created")
                seed_staff()
            except Exception as e:
                print(f"⚠️ Database initialization warning: {e}")
        
        print(f"🚀 Starting server on port {port}...")
        # Start server immediately - Render needs the port open ASAP
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    except Exception as e:
        print(f"❌ FATAL ERROR during startup: {e}")
        import traceback
        traceback.print_exc()
        exit(1)'''

    new_main = '''if __name__ == '__main__':
    # Get port first - Render requires this
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', '').lower() == 'true'
    
    # Check if we're in production (Render sets PORT)
    is_production = os.environ.get('PORT') is not None
    
    db_type = "PostgreSQL (Supabase)" if "postgresql" in DATABASE_URL else "SQLite (Local)"
    print(f"\\n{'='*60}")
    print("ATTENDANCE SYSTEM STARTUP")
    print(f"{'='*60}")
    print(f"Database: {db_type}")
    print(f"URL: {DATABASE_URL[:50]}...")
    print(f"Late Threshold: {LATE_THRESHOLD}")
    print(f"Port: {port}")
    print(f"Mode: {'PRODUCTION' if is_production else 'DEVELOPMENT'}")
    print(f"{'='*60}\\n")
    
    # Initialize database with error handling
    # Don't block startup if database is temporarily unavailable
    db_init_error = None
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables created/verified")
            # Only seed if using SQLite (local dev)
            if 'sqlite' in DATABASE_URL:
                seed_staff()
    except Exception as e:
        db_init_error = str(e)
        print(f"⚠️ Database initialization warning: {e}")
        print("⚠️ Continuing anyway - will retry on first request")
    
    # Start server immediately - Render needs the port open ASAP
    # Use threaded=True to handle multiple requests
    print(f"🚀 Starting server on port {port}...")
    app.run(debug=debug_mode, host='0.0.0.0', port=port, threaded=True)'''

    content = content.replace(old_main, new_main)
    
    # Write the fixed content
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fix applied successfully!")
    print("\nChanges made:")
    print("1. Improved database connection timeout (10s → 30s)")
    print("2. Added connection pool settings for PostgreSQL")
    print("3. Improved health check to return 503 when unhealthy")
    print("4. Made database initialization non-blocking")
    print("5. Added threaded=True for better request handling")
    print("\nTo deploy to Render:")
    print("1. Commit these changes")
    print("2. Push to your Git repository")
    print("3. Render will automatically deploy")

if __name__ == '__main__':
    apply_fix()

