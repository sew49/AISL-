# Render Deployment Guide

## Quick Fix for ModuleNotFoundError

The error `ModuleNotFoundError: No module named 'main'` occurs because Gunicorn is trying to import from `main.py` but your Flask app is in `app.py`.

### Solution

Change your Gunicorn Start Command from:
```
gunicorn main:app
```

To:
```
gunicorn app:app
```

## Render Settings

In your Render dashboard, set:

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Root Directory** | `attendance_system` |

Or if you put contents at root:

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

## Environment Variables

Add these in Render:

- `DATABASE_URL`: Your PostgreSQL connection string (from Supabase)
- `SECRET_KEY`: A random secret key for sessions

## Files Already Configured

Your `attendance_system/app.py` already has:
- ✅ `db.create_all()` at module level for Gunicorn
- ✅ PostgreSQL SSL configuration
- ✅ Admin login with GET/POST methods
- ✅ All required routes

## Dependencies (requirements.txt)

```
flask==2.3.3
flask-sqlalchemy==3.0.5
sqlalchemy==2.0.20
python-dotenv==1.0.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
