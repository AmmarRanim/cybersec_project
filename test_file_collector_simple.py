#!/usr/bin/env python3
"""
Simple File Collector Test

The file collector monitors in REAL-TIME for 60 seconds by default.
This means it only captures file events that happen DURING the monitoring period.

This script demonstrates:
1. How to use the snapshot mode (historical data)
2. How to use the monitor mode (real-time with file activity)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_snapshot_mode():
    """Test file collector in snapshot mode (historical data)."""
    print("="*70)
    print("  FILE COLLECTOR - SNAPSHOT MODE")
    print("="*70)
    print("\nThis mode scans for files modified in the last hour.")
    print("It does NOT monitor in real-time.\n")
    
    from collectors.file_collector import collect_file_snapshot
    
    # Collect files modified in last hour
    print("Scanning for files modified in last hour...")
    events = collect_file_snapshot()
    
    print(f"\n✓ Found {len(events)} file events")
    
    if events:
        print(f"\nSample events:")
        for i, event in enumerate(events[:5], 1):
            file_path = Path(event.resource)
            print(f"  {i}. {event.action}: {file_path.name}")
            print(f"     Path: {event.resource}")
            print(f"     Size: {event.file_size_bytes} bytes")
            print(f"     Sensitivity: {event.sensitivity_level}")
        
        if len(events) > 5:
            print(f"  ... and {len(events) - 5} more")
    else:
        print("\nNo files modified in the last hour.")
        print("This is normal if you haven't been working with files recently.")
    
    return events


def test_monitor_mode_with_activity():
    """Test file collector in monitor mode with file activity."""
    print("\n" + "="*70)
    print("  FILE COLLECTOR - MONITOR MODE (with activity)")
    print("="*70)
    print("\nThis mode monitors in REAL-TIME for 10 seconds.")
    print("We'll create test files during monitoring.\n")
    
    import time
    import threading
    from collectors.file_collector import start_file_monitor
    
    # Create test directory
    test_dir = Path("test_files_monitor")
    test_dir.mkdir(exist_ok=True)
    
    print(f"Test directory: {test_dir}")
    print("Starting monitor for 10 seconds...")
    
    # Function to create files during monitoring
    def create_test_files():
        time.sleep(2)  # Wait for monitor to start
        print("\n[Activity] Creating test files...")
        for i in range(5):
            filename = test_dir / f"test_{i}_{datetime.now().strftime('%H%M%S')}.txt"
            filename.write_text(f"Test file {i} created at {datetime.now()}")
            print(f"  Created: {filename.name}")
            time.sleep(1)
    
    # Start file creation in background
    activity_thread = threading.Thread(target=create_test_files)
    activity_thread.start()
    
    # Monitor for 10 seconds
    events = start_file_monitor([str(test_dir)], duration_seconds=10)
    
    # Wait for activity thread to finish
    activity_thread.join()
    
    print(f"\n✓ Captured {len(events)} file events during monitoring")
    
    if events:
        print(f"\nCaptured events:")
        for i, event in enumerate(events, 1):
            file_path = Path(event.resource)
            print(f"  {i}. {event.action}: {file_path.name}")
    else:
        print("\nNo events captured. This might happen if:")
        print("  - The monitor started after files were created")
        print("  - File events were filtered out")
        print("  - Timing issues with threading")
    
    # Cleanup
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"\n✓ Cleaned up test directory")
    
    return events


def explain_time_ranges():
    """Explain the time range behavior of file collector."""
    print("\n" + "="*70)
    print("  FILE COLLECTOR TIME BEHAVIOR")
    print("="*70)
    print("""
The file collector has TWO modes:

1. SNAPSHOT MODE (collect_file_snapshot)
   - Scans for files modified in the LAST HOUR
   - Returns historical data
   - Fast, no waiting
   - Usage: collect_file_snapshot()

2. MONITOR MODE (start_file_monitor)
   - Monitors in REAL-TIME for specified duration (default 60 seconds)
   - Only captures events that happen DURING monitoring
   - Returns 0 events if no files are modified during monitoring
   - Usage: start_file_monitor(paths, duration_seconds=60)

When you ran the collector and got 0 events, it was because:
- The collector was in MONITOR mode (60 seconds)
- No files were modified during those 60 seconds
- It does NOT look at historical data in monitor mode

To get events, you need to either:
- Use SNAPSHOT mode for historical data
- Use MONITOR mode and create file activity during monitoring
""")


def main():
    """Run file collector tests."""
    print("="*70)
    print("  FILE COLLECTOR TEST")
    print("="*70)
    print("\nTesting both snapshot and monitor modes...\n")
    
    # Explain time behavior first
    explain_time_ranges()
    
    # Test snapshot mode (historical)
    input("\nPress Enter to test SNAPSHOT mode (historical data)...")
    snapshot_events = test_snapshot_mode()
    
    # Test monitor mode (real-time with activity)
    input("\nPress Enter to test MONITOR mode (real-time with activity)...")
    monitor_events = test_monitor_mode_with_activity()
    
    # Summary
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"\nSnapshot mode: {len(snapshot_events)} events (last hour)")
    print(f"Monitor mode: {len(monitor_events)} events (10 seconds with activity)")
    print()
    print("Recommendation:")
    print("  - Use SNAPSHOT mode for testing (faster, historical data)")
    print("  - Use MONITOR mode for real-time detection (production)")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
