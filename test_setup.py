#!/usr/bin/env python
"""
Test script to verify SAFMC FMP Tracker setup
Run this after setting up the application to verify everything works
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import flask
        import flask_sqlalchemy
        import flask_migrate
        import bs4
        import requests
        import apscheduler
        print("✓ All required packages installed")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_app_creation():
    """Test that Flask app can be created"""
    print("\nTesting Flask app creation...")
    try:
        from app import app
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating app: {e}")
        return False

def test_database_config():
    """Test database configuration"""
    print("\nTesting database configuration...")
    try:
        from app import app
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if db_uri:
            print(f"✓ Database configured: {db_uri.split('@')[0]}@...")
            return True
        else:
            print("✗ Database URI not configured")
            return False
    except Exception as e:
        print(f"✗ Error checking database config: {e}")
        return False

def test_models():
    """Test that models can be imported"""
    print("\nTesting database models...")
    try:
        from src.models.action import Action
        from src.models.meeting import Meeting
        from src.models.comment import Comment
        from src.models.milestone import Milestone
        from src.models.scrape_log import ScrapeLog
        print("✓ All models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        return False

def test_routes():
    """Test that routes can be imported"""
    print("\nTesting routes...")
    try:
        from src.routes.api_routes import bp as api_bp
        from src.routes.web_routes import bp as web_bp
        print("✓ All routes imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing routes: {e}")
        return False

def test_scrapers():
    """Test that scrapers can be imported"""
    print("\nTesting scrapers...")
    try:
        from src.scrapers.amendments_scraper import AmendmentsScraper
        from src.scrapers.meetings_scraper import MeetingsScraper
        print("✓ All scrapers imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing scrapers: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from app import app
        from src.config.extensions import db

        with app.app_context():
            # Try to execute a simple query
            db.session.execute('SELECT 1')
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

def test_file_structure():
    """Test that required files and directories exist"""
    print("\nTesting file structure...")
    required_files = [
        'app.py',
        'requirements.txt',
        'render.yaml',
        '.env.example',
        'public/index.html',
        'public/css/styles.css',
        'public/js/app.js'
    ]

    required_dirs = [
        'src/models',
        'src/routes',
        'src/scrapers',
        'src/services',
        'src/config',
        'public',
        'migrations'
    ]

    all_exist = True

    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ Missing: {file}")
            all_exist = False

    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"✓ {dir}/")
        else:
            print(f"✗ Missing: {dir}/")
            all_exist = False

    return all_exist

def main():
    """Run all tests"""
    print("="*60)
    print("SAFMC FMP Tracker - Setup Verification")
    print("="*60)

    tests = [
        ("File Structure", test_file_structure),
        ("Package Imports", test_imports),
        ("Flask App", test_app_creation),
        ("Database Config", test_database_config),
        ("Models", test_models),
        ("Routes", test_routes),
        ("Scrapers", test_scrapers),
        ("Database Connection", test_database_connection)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")

    print(f"\nTests passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python init_db.py (if not already done)")
        print("2. Run: python app.py")
        print("3. Visit: http://localhost:5000")
        print("4. Trigger initial scrape: curl -X POST http://localhost:5000/api/scrape/all")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
