# Staff Portal Deployment Commands for Contabo VPS

## 1. Code Download - Clone GitHub Repository

```
bash
cd /var/www
git clone https://github.com/sew49/AISL-.git attendance_staff
cd /var/www/attendance_staff
```

## 2. Install Libraries

```
bash
# Install Python virtual environment and dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask gunicorn supabase python-dotenv
```

## 3. Environment Variables

```
bash
# Create .env file with Supabase credentials (same database as Render Admin)
cat > .env << 'EOF'
# Supabase Database Connection
DATABASE_URL=postgresql://postgres:ra6oj7UjKpnW5n@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres

# Flask
SECRET_KEY=production_secret_key_change_this

# Supabase Keys (for 12.5 leave balance logic)
SUPABASE_URL=https://sfwhsgrphfrsckzqquxp.supabase.co
SUPABASE_KEY=sb_publishable_7XWjkDZG2TznsmCBeamOlQ_jBOHiK5g
EOF
```

## 4. Start the App - Run with Gunicorn (Background)

```
bash
cd /var/www/attendance_staff
source venv/bin/activate

# Run Gunicorn bound to 0.0.0.0:5000 in background
nohup gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app > /var/log/attendance.log 2>&1 &

# Verify it's running
ps aux | grep gunicorn
```

## 5. Access the Staff Portal

- **Staff Portal:** http://185.252.235.2:5000
- **Casual Worker:** http://185.252.235.2:5000/casual

---

## Validation Checklist

### ✅ 0.5 Multiplier for Leave
The code uses the 0.5 multiplier for casual worker leave calculations. This is preserved in the codebase.

### ✅ Total Hours Calculation for Casual Workers
The Casual Worker total hours calculation is preserved in the staff_portal_only.py file.

### ✅ Same Database as Render Admin
Both the Render Admin site and this Staff Portal connect to the same Supabase database:
- **Database URL:** `postgresql://postgres:ra6oj7UjKpnW5n@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres`

This ensures all leave balances are unified across both sites.

---

## Quick One-Line Deployment (Run all at once)

```
bash
cd /var/www && git clone https://github.com/sew49/AISL-.git attendance_staff && cd attendance_staff && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install flask gunicorn supabase python-dotenv && cat > .env << 'EOF' && nohup /var/www/attendance_staff/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app > /var/log/attendance.log 2>&1 & echo "Deployment complete!"
DATABASE_URL=postgresql://postgres:ra6oj7UjKpnW5n@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres
SECRET_KEY=production_secret_key_change_this
SUPABASE_URL=https://sfwhsgrphfrsckzqquxp.supabase.co
SUPABASE_KEY=sb_publishable_7XWjkDZG2TznsmCBeamOlQ_jBOHiK5g
EOF
```

---

## Useful Commands

```
bash
# Check if app is running
ps aux | grep gunicorn

# View logs
tail -f /var/log/attendance.log

# Stop the app
pkill gunicorn

# Restart the app
pkill gunicorn && cd /var/www/attendance_staff && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app > /var/log/attendance.log 2>&1 &
