# Quick Deploy Commands for Contabo VPS

## Option 1: Upload via SCP (Recommended for Quick Transfer)

### From your local machine terminal:

```
bash
# Upload app.py
scp C:/Users/ADMIN/Desktop/attendance_system/app.py root@185.252.235.2:/var/www/attendance_staff/

# Upload templates folder
scp -r C:/Users/ADMIN/Desktop/attendance_system/templates root@185.252.235.2:/var/www/attendance_staff/

# Upload requirements.txt (if needed)
scp C:/Users/ADMIN/Desktop/attendance_system/requirements.txt root@185.252.235.2:/var/www/attendance_staff/

# Upload .env file (if you have one locally)
scp C:/Users/ADMIN/Desktop/attendance_system/.env root@185.252.235.2:/var/www/attendance_staff/
```

---

## Option 2: Clone from GitHub (Easiest - Do This!)

### SSH into your server first, then run:

```
bash
# Navigate to web directory
cd /var/www

# Clone your repository
git clone https://github.com/sew49/AISL-.git attendance_staff

# Enter the directory
cd attendance_staff

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install flask gunicorn supabase python-dotenv flask-sqlalchemy flask-cors

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:ra6oj7UjKpnW5n@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres
SECRET_KEY=production_secret_key_change_this
SUPABASE_URL=https://sfwhsgrphfrsckzqquxp.supabase.co
SUPABASE_KEY=sb_publishable_7XWjkDZG2TznsmCBeamOlQ_jBOHiK5g
EOF
```

---

## Final Launch - Start the Staff Portal

### Command to run in background (using nohup):

```
bash
cd /var/www/attendance_staff
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app > /var/log/attendance.log 2>&1 &
```

### What this does:
- `nohup` - Keeps running even after you close the terminal
- `--bind 0.0.0.0:5000` - Accepts connections from outside
- `--workers 3` - Handles multiple users
- `app:app` - Your Flask app name
- `> /var/log/attendance.log` - Saves logs to a file
- `&` - Runs in background

---

## Verify It's Working

```
bash
# Check if gunicorn is running
ps aux | grep gunicorn

# Test locally
curl http://localhost:5000

# Check logs
tail -f /var/log/attendance.log
```

---

## Access Your Site

- **Staff Portal:** http://185.252.235.2:5000
- **Casual Worker:** http://185.252.235.2:5000/casual

---

## If You Need to Stop/Restart

```
bash
# Stop the app
pkill gunicorn

# Restart
cd /var/www/attendance_staff
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app > /var/log/attendance.log 2>&1 &
