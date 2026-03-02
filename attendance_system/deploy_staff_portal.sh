#!/bin/bash

# =====================================================
# Staff Portal Deployment Script for Contabo VPS
# =====================================================

echo "========================================"
echo "Staff Portal Deployment for Contabo VPS"
echo "========================================"

# Update system
echo "[1/7] Updating system packages..."
apt update && apt upgrade -y

# Install Python and required packages
echo "[2/7] Installing Python and dependencies..."
apt install -y python3 python3-pip python3-venv git

# Install PostgreSQL client (for Supabase connection)
apt install -y libpq-dev postgresql-client

# Create project directory
echo "[3/7] Creating project directory..."
mkdir -p /var/www/attendance_staff
cd /var/www/attendance_staff

# Clone the repository (or copy files)
# Note: Replace with your git repo URL
# git clone https://github.com/sew49/AISL-.git .

# For now, we'll assume files are copied or cloned

# Create virtual environment
echo "[4/7] Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install gunicorn flask flask-sqlalchemy flask-cors python-dotenv pytz fpdf email_validator

# Create environment file
echo "[5/7] Creating environment configuration..."
cat > .env << 'EOF'
# Supabase Database (use same as Admin Dashboard)
DATABASE_URL=postgresql://postgres.sfwhsgrphfrsckzqquxp:YOUR_PASSWORD@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres

# Flask Configuration
SECRET_KEY=your_secret_key_here

# Email Configuration (for leave approval notifications)
EMAIL_ENABLED=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=noreply@attendance.com
EMAIL_FROM_NAME=Attendance System
EOF

echo "⚠️  IMPORTANT: Edit .env file with your Supabase password and email credentials!"
echo "    Location: /var/www/attendance_staff/.env"

# Create systemd service
echo "[6/7] Creating systemd service..."
cat > /etc/systemd/system/attendance_staff.service << 'EOF'
[Unit]
Description=Attendance Staff Portal
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/attendance_staff
Environment="PATH=/var/www/attendance_staff/venv/bin"
ExecStart=/var/www/attendance_staff/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable attendance_staff

# Configure firewall
echo "[7/7] Configuring firewall..."
ufw allow 5000/tcp
ufw --force enable

# Start the service
echo "Starting Staff Portal..."
systemctl start attendance_staff

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Staff Portal URL: http://YOUR_CONTABO_IP:5000"
echo ""
echo "Commands:"
echo "  Start:   systemctl start attendance_staff"
echo "  Stop:    systemctl stop attendance_staff"
echo "  Restart: systemctl restart attendance_staff"
echo "  Status:  systemctl status attendance_staff"
echo ""
echo "⚠️  Don't forget to:"
echo "  1. Edit /var/www/attendance_staff/.env with your Supabase password"
echo "  2. Ensure the same Supabase database is used as Admin Dashboard"
echo ""
