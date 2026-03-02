#!/bin/bash
# ============================================================
# CONTABO STAFF PORTAL SETUP COMMANDS
# Run these commands on your Contabo VPS (185.252.235.2)
# ============================================================

echo "========================================"
echo "Staff Portal Setup for Contabo VPS"
echo "========================================"

# --- STEP 1: Update & Install Dependencies ---
echo "[1/6] Installing Python and dependencies..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git libpq-dev

# --- STEP 2: Clone Repository ---
echo "[2/6] Cloning repository..."
cd /var/www
git clone https://github.com/sew49/AISL-.git attendance_staff
cd /var/www/attendance_staff

# --- STEP 3: Setup Virtual Environment ---
echo "[3/6] Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install gunicorn flask flask-sqlalchemy flask-cors python-dotenv pytz fpdf

# --- STEP 4: Environment Variables ---
echo "[4/6] Setting up environment variables..."

# Create .env file with Supabase credentials
cat > .env << 'EOF'
# Supabase Database Connection
DATABASE_URL=postgresql://postgres:ra6oj7UjKpnW5n@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres

# Flask
SECRET_KEY=production_secret_key_change_this

# Email (optional - for leave approval notifications)
EMAIL_ENABLED=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USERNAME=
EMAIL_PASSWORD=
EMAIL_FROM=noreply@attendance.com
EMAIL_FROM_NAME=Attendance System
EOF

echo "✅ Environment file created at /var/www/attendance_staff/.env"

# --- STEP 5: Firewall ---
echo "[5/6] Configuring firewall..."
ufw allow 5000/tcp
ufw --force enable

# --- STEP 6: Create Systemd Service ---
echo "[6/6] Creating systemd service..."

cat > /etc/systemd/system/attendance_staff.service << 'EOF'
[Unit]
Description=Attendance Staff Portal
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/attendance_staff
Environment="PATH=/var/www/attendance_staff/venv/bin"
ExecStart=/var/www/attendance_staff/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 staff_portal_only:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable attendance_staff
systemctl start attendance_staff

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "Staff Portal URL: http://185.252.235.2:5000"
echo "Casual Worker:     http://185.252.235.2:5000/casual"
echo ""
echo "Admin Dashboard:   https://aisl-cimr.onrender.com/admin-login"
echo ""
echo "Commands:"
echo "  Status:   systemctl status attendance_staff"
echo "  Restart:  systemctl restart attendance_staff"
echo "  Logs:     journalctl -u attendance_staff -f"
echo ""
