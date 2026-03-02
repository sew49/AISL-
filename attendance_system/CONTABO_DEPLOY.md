# Staff Portal Deployment to Contabo VPS

## Overview

This guide explains how to deploy the **Staff Portal only** to a Contabo VPS, while keeping the **Admin Dashboard** on your local machine (192.168.8.74:5000).

Both portals will connect to the **same Supabase database**, ensuring:
- All staff leave balances preserved (21 Annual, 14 Sick)
- Riziki's 12.5 balance and Craig's 5.5 sick days maintained
- All attendance records shared between portals

## Architecture

```
                    ┌─────────────────────┐
                    │   SUPABASE DB       │
                    │ (Shared Database)   │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         │                                           │
         ▼                                           ▼
┌─────────────────────┐                   ┌─────────────────────┐
│  Admin Dashboard   │                   │   Staff Portal     │
│ (192.168.8.74:5000)│                   │ (Contabo VPS :5000) │
│   (Local/Render)   │                   │                     │
└─────────────────────┘                   └─────────────────────┘
```

## Step 1: Get Supabase Connection String

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `sfwhsgrphfrsckzqquxp`
3. Go to **Settings** → **Database**
4. Find **Connection String** (URI format)
5. Replace `YOUR_PASSWORD` with your actual password
6. Format should be:
   
```
   postgresql://postgres:YOUR_PASSWORD@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres
   
```

## Step 2: Deploy to Contabo VPS

### Option A: Automated Script

```
bash
# SSH into your Contabo server
ssh root@YOUR_CONTABO_IP

# Download the deployment script
cd /opt
curl -O https://raw.githubusercontent.com/sew49/AISL-/main/attendance_system/deploy_staff_portal.sh

# Make it executable
chmod +x deploy_staff_portal.sh

# Run it
./deploy_staff_portal.sh
```

### Option B: Manual Setup

```
bash
# SSH into Contabo
ssh root@YOUR_CONTABO_IP

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv git libpq-dev

# Create project directory
mkdir -p /var/www/attendance_staff
cd /var/www/attendance_staff

# Clone repository
git clone https://github.com/sew49/AISL-.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install gunicorn flask flask-sqlalchemy flask-cors python-dotenv pytz fpdf

# Create .env file (see env_template.txt)
nano .env
# Fill in DATABASE_URL with your Supabase connection string
```

## Step 3: Configure Environment Variables

Edit `/var/www/attendance_staff/.env`:

```
env
# Supabase Database - USE SAME AS ADMIN
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres

# Flask
SECRET_KEY=change_this_to_random_string

# Email (optional)
EMAIL_ENABLED=false
```

## Step 4: Create Systemd Service

```
bash
cat > /etc/systemd/system/attendance_staff.service << 'EOF'
[Unit]
Description=Attendance Staff Portal
After=network.targetUser=root
WorkingDirectory=/var

[Service]
/www/attendance_staff
Environment="PATH=/var/www/attendance_staff/venv/bin"
ExecStart=/var/www/attendance_staff/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable attendance_staff
systemctl start attendance_staff
```

## Step 5: Configure Firewall

```
bash
ufw allow 5000/tcp
ufw enable
```

## Step 6: Verify Deployment

```
bash
# Check service status
systemctl status attendance_staff

# Test API
curl http://localhost:5000/api/employees
```

## Staff Portal Features

The Contabo Staff Portal includes:

| Feature | Status |
|---------|--------|
| Staff Clock In/Out | ✅ |
| Casual Worker Clock In/Out | ✅ |
| Total Hours Calculation | ✅ |
| Leave Request Submission | ✅ |
| 0.5 Half-Day Multiplier | ✅ |
| 08:15 AM Late Threshold | ✅ |
| Email Notifications | ⚙️ (optional) |
| Admin Dashboard | ❌ (stays local) |

## Important Notes

### Data Preservation
- **Leave Balances**: All 21 Annual + 14 Sick days per staff are stored in Supabase
- **Riziki's 12.5 balance**: Preserved in `staff.leave_balance` column
- **Craig's 5.5 sick days**: Preserved in `staff.sick_leave_balance` column
- **All attendance records**: Shared between both portals

### UI Preservation
The following UI elements are preserved from local deployment:
- Green/Red color scheme for casual workers
- Large mobile-friendly buttons (🟢 CLOCK IN / 🔴 CLOCK OUT)
- Total Hours summary card
- All existing templates

### Network Access
- Staff Portal: `http://YOUR_CONTABO_IP:5000`
- If behind firewall, ensure port 5000 is open
- Consider using Nginx reverse proxy for domain name

## Troubleshooting

### Service won't start
```
bash
# Check logs
journalctl -u attendance_staff -f

# Common issues:
# - Wrong DATABASE_URL in .env
# - Missing dependencies
# - Port 5000 already in use
```

### Can't connect to database
```
bash
# Test Supabase connection
psql "postgresql://postgres:YOUR_PASSWORD@db.sfwhsgrphfrsckzqquxp.supabase.co:5432/postgres" -c "SELECT 1"
```

### Check current balances
```
bash
# SSH into Contabo and run Python
cd /var/www/attendance_staff
source venv/bin/activate
python3
from app import app, db, Staff
with app.app_context():
    for s in Staff.query.all():
        print(f"{s.first_name} {s.last_name}: Annual={s.leave_balance}, Sick={s.sick_leave_balance}")
```

## Rollback

If you need to stop the Contabo server and revert to local only:

```
bash
# On Contabo
systemctl stop attendance_staff
systemctl disable attendance_staff
```

The local Admin Dashboard at 192.168.8.74:5000 will continue working with the Supabase database.
