#!/usr/bin/env python3
"""Quick diagnostic script to verify CORS configuration."""

import os
import sys

print("=" * 70)
print("CORS CONFIGURATION DIAGNOSTIC")
print("=" * 70)

# Check .env file exists
print("\n[1] Checking .env file...")
if os.path.exists('.env'):
    print("  ✓ .env file exists")
    with open('.env', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('FLASK_ENV'):
                print(f"  ✓ {line.strip()}")
            elif line.startswith('ALLOWED_ORIGINS'):
                print(f"  ✓ {line.strip()}")
else:
    print("  ✗ .env file NOT FOUND")
    print("  → Run: cp .env.example .env")
    sys.exit(1)

# Check environment variables are loaded
print("\n[2] Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

flask_env = os.getenv('FLASK_ENV', 'NOT SET')
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'NOT SET')

print(f"  FLASK_ENV: {flask_env}")
print(f"  ALLOWED_ORIGINS: {allowed_origins}")

if flask_env == 'NOT SET':
    print("  ✗ FLASK_ENV not set in environment")
elif flask_env == 'development':
    print("  ✓ Running in development mode")
else:
    print("  ⚠  Running in production mode")

if allowed_origins == 'NOT SET':
    print("  ✗ ALLOWED_ORIGINS not set in environment")
else:
    origins = [o.strip() for o in allowed_origins.split(',')]
    print(f"  ✓ {len(origins)} origin(s) configured:")
    for origin in origins:
        print(f"    - {origin}")

# Check Flask app can start
print("\n[3] Checking Flask app initialization...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.chdir('web')

    # Suppress some warnings
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)

    from app import app, allowed_origins as app_origins

    print("  ✓ Flask app imported successfully")
    print(f"  ✓ CORS configured with {len(app_origins)} origin(s)")

    if app_origins:
        for origin in app_origins:
            print(f"    - {origin}")
    else:
        print("  ✗ No origins configured in app!")

except Exception as e:
    print(f"  ✗ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test CORS headers
print("\n[4] Testing CORS headers...")
try:
    with app.test_client() as client:
        # Test OPTIONS request (preflight)
        response = client.options(
            '/api/stocks',
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET'
            }
        )

        print(f"  OPTIONS /api/stocks status: {response.status_code}")

        if 'Access-Control-Allow-Origin' in response.headers:
            print(f"  ✓ Access-Control-Allow-Origin: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("  ✗ Access-Control-Allow-Origin header MISSING")

        if 'Access-Control-Allow-Methods' in response.headers:
            print(f"  ✓ Access-Control-Allow-Methods: {response.headers['Access-Control-Allow-Methods']}")
        else:
            print("  ✗ Access-Control-Allow-Methods header MISSING")

        # Test GET request
        response = client.get(
            '/health',
            headers={'Origin': 'http://localhost:5173'}
        )

        print(f"\n  GET /health status: {response.status_code}")

        if 'Access-Control-Allow-Origin' in response.headers:
            print(f"  ✓ Access-Control-Allow-Origin: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("  ✗ Access-Control-Allow-Origin header MISSING")

except Exception as e:
    print(f"  ✗ Error testing CORS: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 70)

if app_origins and len(app_origins) > 0:
    print("\n✓ CORS is properly configured")
    print("\nIf you're still getting CORS errors:")
    print("  1. Make sure Flask server is running: python3 web/app.py")
    print("  2. Restart the Flask server (it must reload .env)")
    print("  3. Check server logs for CORS configuration messages")
    print("  4. Verify frontend is running on http://localhost:5173")
else:
    print("\n✗ CORS is NOT properly configured")
    print("\nTo fix:")
    print("  1. Make sure .env file exists: cp .env.example .env")
    print("  2. Restart Flask server: python3 web/app.py")
    print("  3. Check server logs")
