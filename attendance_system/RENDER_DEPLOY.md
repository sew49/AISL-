# Render Deployment Guide

## Quick Fix for "Port scan timeout reached, no open HTTP ports detected"

This error occurs when the app doesn't listen on the correct port. Render provides a `PORT` environment variable that your app must use.

### ✅ FIXED: The app now uses the PORT environment variable

The `app.py` has been updated to:
```python
port = int(os.environ.get('PORT', 5000))
app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

## Render Settings

In your Render dashboard, set:

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |
| **Root Directory** | `attendance_system` |

## Environment Variables

Add these in Render:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Your PostgreSQL connection string (from Supabase) |
| `SECRET_KEY` | A random secret key for sessions (e.g., `your-secret-key-here`) |

## Files Already Configured

Your `attendance_system/app.py` now has:
- ✅ Uses `PORT` environment variable (defaults to 5000 locally)
- ✅ Disables debug mode automatically when PORT is set (production)
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
```

## Troubleshooting

If you still get port errors:
1. Check that `PORT` environment variable is set in Render dashboard
2. Verify the Start Command is `python app.py` (not `gunicorn app:app`)
3. Make sure the Root Directory is set to `attendance_system`
4. Redeploy the service after making changes
