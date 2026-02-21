# Add SQLite timeout and scoped session to app.py

import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add connect_args={'timeout': 30} to SQLite configuration
old_sqlite = "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'"
new_sqlite = """app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance_system.db'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'connect_args': {'timeout': 30}
    }"""

content = content.replace(old_sqlite, new_sqlite)

# 2. Add scoped session for thread safety
old_db = """db = SQLAlchemy(app)
migrate = Migrate(app, db)"""

new_db = """db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Use scoped session for thread safety with multiple concurrent users
from sqlalchemy.orm import scoped_session, sessionmaker
db_session = scoped_session(sessionmaker(bind=db.engine))"""

content = content.replace(old_db, new_db)

# 3. Update teardown to use scoped session
old_teardown = """@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()"""

new_teardown = """@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
    db_session.remove()"""

content = content.replace(old_teardown, new_teardown)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added database timeout=30 and scoped session to app.py")
