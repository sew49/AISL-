"""
Flask Application - Main Entry Point

This file connects to Supabase and uses the 'RENDER' environment variable
to determine which routes to enable:
- If RENDER is set (True): Admin routes are enabled
- If RENDER is not set (False): Staff routes are enabled
"""

import os
from flask import Flask, jsonify, redirect, url_for

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Supabase client
from supabase import create_client, Client

# Get environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
RENDER = os.getenv('RENDER', 'False').lower() == 'true'

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

print(f"\n{'='*60}")
print("FLASK APP STARTUP")
print(f"{'='*60}")
print(f"Supabase URL: {SUPABASE_URL}")
print(f"RENDER mode: {RENDER}")
print(f"{'='*60}\n")

if RENDER:
    # RENDER (Production) - Admin routes only
    print(">>> Loading Admin Routes (Production Mode) <<<")
    
    @app.route('/')
    def index():
        """Admin dashboard route"""
        return jsonify({
            'mode': 'admin',
            'message': 'Admin route - Production mode'
        })
    
    @app.route('/admin')
    def admin():
        """Admin route"""
        return jsonify({
            'success': True,
            'mode': 'admin',
            'message': 'Admin routes enabled'
        })
    
    print(">>> Admin Routes Registered Successfully <<<\n")
    
else:
    # LOCAL (Development) - Staff routes only
    print(">>> Loading Staff Routes (Development Mode) <<<")
    
    @app.route('/')
    def index():
        """Staff dashboard route"""
        return jsonify({
            'mode': 'staff',
            'message': 'Staff route - Development mode'
        })
    
    @app.route('/staff')
    def staff():
        """Staff route"""
        return jsonify({
            'success': True,
            'mode': 'staff',
            'message': 'Staff routes enabled'
        })
    
    @app.route('/admin-login')
    def admin_login_disabled():
        """Admin login disabled in local mode"""
        return jsonify({
            'success': False,
            'error': 'Admin access is disabled in local (staff) mode'
        }), 403
    
    print(">>> Staff Routes Registered Successfully <<<\n")


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=not RENDER, host='0.0.0.0', port=port)
