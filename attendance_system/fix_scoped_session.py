# Fix the scoped session error - remove it and just keep timeout=30

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the scoped session creation that causes the error
old_db = """db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Use scoped session for thread safety with multiple concurrent users
from sqlalchemy.orm import scoped_session, sessionmaker
db_session = scoped_session(sessionmaker(bind=db.engine))"""

new_db = """db = SQLAlchemy(app)
migrate = Migrate(app, db)"""

content = content.replace(old_db, new_db)

# Update teardown to remove db_session.remove()
old_teardown = """@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
    db_session.remove()"""

new_teardown = """@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()"""

content = content.replace(old_teardown, new_teardown)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed scoped session error - removed it, kept timeout=30")
