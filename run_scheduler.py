#!/usr/bin/env python3
"""
Launch script for ETL Scheduler
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from etl_scheduler import main

if __name__ == "__main__":
    print("=" * 60)
    print("ETL Job Scheduler & Orchestrator")
    print("Version 1.0.0")
    print("=" * 60)
    print("\nStarting application...\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
