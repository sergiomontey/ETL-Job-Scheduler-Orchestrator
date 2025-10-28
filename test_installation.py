#!/usr/bin/env python3
"""
Test script to verify ETL Scheduler installation and functionality
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        print("✓ Tkinter is available")
    except ImportError as e:
        print(f"✗ Tkinter import failed: {e}")
        return False
    
    try:
        import sqlite3
        print("✓ SQLite3 is available")
    except ImportError as e:
        print(f"✗ SQLite3 import failed: {e}")
        return False
    
    try:
        import json
        import threading
        import subprocess
        import queue
        from datetime import datetime
        print("✓ Standard library modules available")
    except ImportError as e:
        print(f"✗ Standard library import failed: {e}")
        return False
    
    return True

def test_custom_modules():
    """Test that custom modules can be imported"""
    print("\nTesting custom modules...")
    
    modules = [
        'job_manager',
        'scheduler_engine', 
        'workflow_canvas',
        'job_dialog',
        'log_viewer',
        'settings_dialog',
        'croniter'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py")
        except ImportError as e:
            print(f"✗ {module}.py: {e}")
            all_ok = False
    
    return all_ok

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        from job_manager import JobManager
        
        # Create test database
        test_db = "test_etl.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        manager = JobManager(test_db)
        print("✓ Database initialized")
        
        # Test creating a job
        job_data = {
            'name': 'Test Job',
            'description': 'Test job for verification',
            'job_type': 'shell',
            'command': 'echo "test"',
            'enabled': True,
            'schedule_type': 'manual'
        }
        
        job_id = manager.create_job(job_data)
        print(f"✓ Job created (ID: {job_id})")
        
        # Test retrieving job
        job = manager.get_job(job_id)
        if job and job['name'] == 'Test Job':
            print("✓ Job retrieved successfully")
        else:
            print("✗ Job retrieval failed")
            return False
        
        # Clean up
        os.remove(test_db)
        print("✓ Database test completed")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_croniter():
    """Test cron expression parser"""
    print("\nTesting cron parser...")
    
    try:
        from croniter import croniter
        from datetime import datetime
        
        # Test daily at 9 AM
        cron = croniter("0 9 * * *", datetime(2025, 10, 27, 8, 0))
        next_run = cron.get_next()
        
        if next_run.hour == 9 and next_run.minute == 0:
            print("✓ Cron parser working correctly")
            return True
        else:
            print(f"✗ Cron parser returned unexpected time: {next_run}")
            return False
            
    except Exception as e:
        print(f"✗ Cron parser test failed: {e}")
        return False

def test_gui_components():
    """Test that GUI can be created (without showing)"""
    print("\nTesting GUI components...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Test basic widgets
        frame = ttk.Frame(root)
        label = ttk.Label(frame, text="Test")
        button = ttk.Button(frame, text="Test")
        entry = ttk.Entry(frame)
        
        print("✓ Basic GUI widgets work")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False

def check_files():
    """Check that all required files exist"""
    print("\nChecking files...")
    
    required_files = [
        'etl_scheduler.py',
        'job_manager.py',
        'scheduler_engine.py',
        'job_dialog.py',
        'workflow_canvas.py',
        'log_viewer.py',
        'settings_dialog.py',
        'croniter.py',
        'run_scheduler.py',
        'README_ETL.md',
        'QUICKSTART.txt',
        'example_jobs.json'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} - MISSING")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("=" * 70)
    print("ETL Scheduler Installation Test")
    print("=" * 70)
    
    tests = [
        ("File Check", check_files),
        ("Import Test", test_imports),
        ("Custom Modules", test_custom_modules),
        ("Database", test_database),
        ("Cron Parser", test_croniter),
        ("GUI Components", test_gui_components)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print("-" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The ETL Scheduler is ready to use.")
        print("\nTo start the application, run:")
        print("  python3 run_scheduler.py")
        print("\nOr:")
        print("  python3 etl_scheduler.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
