#!/usr/bin/env python3
"""
Test with actual file activity

This script:
1. Creates test files to generate events
2. Runs file collector
3. Stores and queries the events
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_servers.event_storage.storage_engine import store_events
from mcp_servers.event_storage.query_engine import query_events, export_to_mailbox


def create_test_files():
    """Create some test files to generate events."""
    print("\n" + "="*60)
    print("Creating test files to generate events...")
    print("="*60)
    
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create various files
    files_created = []
    
    # 1. Text file
    (test_dir / "document.txt").write_text("This is a test document")
    files_created.append("document.txt")
    time.sleep(0.5)
    
    # 2. JSON file (medium sensitivity)
    (test_dir / "config.json").write_text('{"setting": "value"}')
    files_created.append("config.json")
    time.sleep(0.5)
    
    # 3. Excel-like file (medium sensitivity)
    (test_dir / "data.xlsx").write_text("fake excel data")
    files_created.append("data.xlsx")
    time.sleep(0.5)
    
    # 4. Modify a file
    (test_dir / "document.txt").write_text("Modified content")
    files_created.append("document.txt (modified)")
    time.sleep(0.5)
    
    # 5. Delete a file
    (test_dir / "config.json").unlink()
    files_created.append("config.json (deleted)")
    
    print(f"Created {len(files_created)} file operations:")
    for f in files_created:
        print(f"  - {f}")
    
    return test_dir


def run_file_collector_with_activity():
    """Run file collector while creating file activity."""
    print("\n" + "="*60)
    print("Running file collector (monitoring for 10 seconds)...")
    print("="*60)
    
    # Start collector in background
    import threading
    
    collector_output = []
    collector_error = []
    
    def run_collector():
        try:
            # Run collector with shorter duration
            result = subprocess.run(
                ["python", "-c", 
                 "from collectors.file_collector import start_file_monitor; "
                 "import json; "
                 "events = start_file_monitor(['test_files'], duration_seconds=10); "
                 "print(json.dumps([e.model_dump() for e in events], indent=2))"],
                capture_output=True,
                text=True,
                timeout=15
            )
            collector_output.append(result.stdout)
            collector_error.append(result.stderr)
        except Exception as e:
            collector_error.append(str(e))
    
    # Start collector
    collector_thread = threading.Thread(target=run_collector)
    collector_thread.start()
    
    # Wait a bit for collector to start
    time.sleep(2)
    
    # Create file activity while collector is running
    print("\nGenerating file activity...")
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    for i in range(5):
        filename = f"test_{i}.txt"
        (test_dir / filename).write_text(f"Test file {i} created at {datetime.now()}")
        print(f"  Created: {filename}")
        time.sleep(1)
    
    # Wait for collector to finish
    collector_thread.join()
    
    # Parse output
    if collector_output and collector_output[0]:
        try:
            events = json.loads(collector_output[0])
            print(f"\nOK Collected {len(events)} events")
            return events
        except json.JSONDecodeError as e:
            print(f"Error parsing output: {e}")
            print(f"Output: {collector_output[0][:500]}")
            return []
    else:
        print("No output from collector")
        if collector_error:
            print(f"Error: {collector_error}")
        return []


def main():
    print("="*60)
    print("FILE COLLECTION TEST WITH ACTIVITY")
    print("="*60)
    print("\nThis test will:")
    print("  1. Create test files to generate events")
    print("  2. Run file collector while creating more files")
    print("  3. Store collected events")
    print("  4. Query and export them")
    print()
    
    # Step 1: Create initial test files
    test_dir = create_test_files()
    
    # Step 2: Run collector with activity
    events = run_file_collector_with_activity()
    
    if not events:
        print("\nNo events collected.")
        print("\nAlternative: Use process collector instead")
        print("  python -m collectors.process_collector")
        return 1
    
    # Step 3: Store events
    print("\n" + "="*60)
    print(f"Storing {len(events)} events...")
    print("="*60)
    
    result = store_events(events)
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    files = result.get('files_written', [])
    file_str = files[0] if files else 'logs/'
    print(f"OK Stored {result['stored_count']} events to {file_str}")
    
    # Step 4: Query events
    print("\n" + "="*60)
    print("Querying file events...")
    print("="*60)
    
    result = query_events(event_category="file", page_size=20)
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    print(f"OK Found {result['total_matches']} file events")
    print(f"\nSample events:")
    for i, event in enumerate(result['events'][:5], 1):
        print(f"  {i}. {event['event_type']}: {Path(event['resource']).name}")
    
    # Step 5: Export
    print("\n" + "="*60)
    print("Exporting to mailbox...")
    print("="*60)
    
    result = export_to_mailbox(event_category="file")
    if "error" in result:
        print(f"Error: {result['error']}")
        return 1
    
    print(f"OK Exported {result['event_count']} events")
    print(f"   File: {result['export_file']}")
    
    # Cleanup
    print("\n" + "="*60)
    print("Cleaning up test files...")
    print("="*60)
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("OK Test files removed")
    
    print("\n" + "="*60)
    print("SUCCESS - Check mailbox/clean_events.json for results!")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    exit(main())
