#!/bin/bash
# ============================================================
# CONTABO VPS DEBUG & FIX SCRIPT
# Run this on your Contabo VPS (185.252.235.2) to fix the staff portal
# ============================================================

echo "========================================"
echo "Staff Portal Debug & Fix for Contabo VPS"
echo "========================================"

# --- STEP 1: Configure Firewall ---
echo "[1/5] Configuring firewall..."
ufw allow 5000/tcp
ufw allow ssh
ufw enable
echo "✅ Firewall configured"

# --- STEP 2: Set Environment Variables ---
echo "[2/5] Setting environment variables..."
export SUPABASE_URL='https://sfwhsgrphfrsckzqquxp.supabase.co'
export SUPABASE_KEY='sb_publishable_7XWjkDZG2TznsmCBeamOlQ_jBOHiK5g'

# Also save to .env file for persistence
cd /var/www/attendance_staff
if [ -f .env ]; then
    # Check if SUPABASE_URL already exists, if not add it
    if ! grep -q "SUPABASE_URL" .env; then
        echo "SUPABASE_URL=$SUPABASE_URL" >> .env
    fi
    if ! grep -q "SUPABASE_KEY" .env; then
        echo "SUPABASE_KEY=$SUPABASE_KEY" >> .env
    fi
else
    echo "SUPABASE_URL=$SUPABASE_URL" >> .env
    echo "SUPABASE_KEY=$SUPABASE_KEY" >> .env
fi
echo "✅ Environment variables set"

# --- STEP 3: Process Check & Kill ---
echo "[3/5] Checking for running processes..."
ps aux | grep gunicorn
ps aux | grep python

echo "Do you want to kill any stuck gunicorn processes? (y/n)"
read -r kill_process
if [ "$kill_process" = "y" ] || [ "$kill_process" = "Y" ]; then
    pkill -9 gunicorn
    pkill -9 python
    echo "✅ Stuck processes killed"
else
    echo "⚠️  Skipped killing processes"
fi

# --- STEP 4: Restart App ---
echo "[4/5] Restarting Flask app with Gunicorn..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found, creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install flask gunicorn supabase python-dotenv
else
    source venv/bin/activate
fi

# Export environment variables before starting
export SUPABASE_URL='https://sfwhsgrphfrsckzqquxp.supabase.co'
export SUPABASE_KEY='sb_publishable_7XWjkDZG2TznsmCBeamOlQ_jBOHiK5g'

# Start Gunicorn bound to 0.0.0.0:5000
# Using app:app as per your configuration
gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app &

echo "✅ Flask app started with Gunicorn"

# --- STEP 5: Verify ---
echo "[5/5] Verifying connection..."
sleep 3

# Check if gunicorn is running
echo "Current gunicorn processes:"
ps aux | grep gunicorn

# Test port 5000
echo "Testing port 5000..."
if command -v curl &> /dev/null; then
    curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ || echo "Connection test failed"
else
    echo "curl not installed, skipping HTTP test"
fi

echo ""
echo "========================================"
echo "✅ DEBUG & FIX COMPLETE!"
echo "========================================"
echo ""
echo "Staff Portal URL: http://185.252.235.2:5000"
echo "Casual Worker:    http://185.252.235.2:5000/casual"
echo ""
echo "Commands:"
echo "  Check status:   ps aux | grep gunicorn"
echo "  View logs:      tail -f /var/log/attendance.log"
echo "  Restart:        sudo systemctl restart attendance_staff"
echo "  Stop:           pkill gunicorn"
echo ""
