"""
Configuration for the Attendance System
Handles Supabase connection and environment-based settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# =====================================================
# ENVIRONMENT CONFIGURATION
# =====================================================

# Detect if running on Render (production)
IS_RENDER = os.getenv('RENDER') is not None

# App Mode based on environment
if IS_RENDER:
    APP_MODE = 'admin'  # Render - Admin mode only
else:
    APP_MODE = 'staff'  # Local - Staff mode only

# =====================================================
# SUPABASE CONFIGURATION
# =====================================================

# Supabase credentials (same for both modes)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://sfwhsgrphfrsckzqquxp.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'MRaSgUIhVBNJKyBMAnYnJw_HvGuywcn')

# =====================================================
# DATABASE CONFIGURATION
# =====================================================

DB_TYPE = os.getenv('DB_TYPE', 'sqlite')

if DB_TYPE == 'postgresql':
    # PostgreSQL configuration (for production/Render)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/attendance_system'
    )
else:
    # SQLite configuration (for local development)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///attendance_system.db'

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'connect_args': {'timeout': 30} if DB_TYPE != 'postgresql' else {}
}

SQLALCHEMY_TRACK_MODIFICATIONS = False

# =====================================================
# FLASK CONFIGURATION
# =====================================================

SECRET_KEY = os.getenv('SECRET_KEY', 'aero_instrument_secure_key_2026')
PERMANENT_SESSION_LIFETIME_HOURS = 8

# =====================================================
# EXPORTS
# =====================================================

__all__ = [
    'IS_RENDER',
    'APP_MODE',
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'DB_TYPE',
    'SQLALCHEMY_DATABASE_URI',
    'SQLALCHEMY_ENGINE_OPTIONS',
    'SECRET_KEY',
    'PERMANENT_SESSION_LIFETIME_HOURS'
]
