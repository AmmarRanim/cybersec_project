#!/usr/bin/env python3
"""
Real-world test: Collect actual data and store it

This script:
1. Runs a real collector (system_collector)
2. Stores the events
3. Queries them back
4. Exports to mailbox
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_servers.event_storage.storage_engine import store_events
from mcp_servers.event_storage.query_engine import query_events, export_to_mailbox

def run_collector(collector_name):
    """Run a collector and return events."""
    print(f"\n{'='*60}")
    print(f"Step 1: Running {collector_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            ["python", "-m", f"collectors.{collector_name}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Error running collector: {result.stderr}")
            return []
        
        # Parse JSON output - skip the first line which is the count
        output = result.stdout.strip()
        if not output:
            print("No output from collector")
            return []
        
        # Split by lines and find the JSON array
        lines = output.split('\n')
        
        # Skip first line if it's a message like "Collected X events"
        json_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('[') or line.strip().startswith('{'):
                json_start = i
                break
        
        json_text = '\n'.join(lines[json_start:])
        
        try:
            # Try parsing as array first
            events = json.loads(json_text)
            if not isinstance(events, list):
                events = [events]
        except:
            # If that fails, try parsing line by line
            events = []
            for line in lines[json_start:]:
                line = line.strip()
                if line and (line.startswith('{') or line.startswith('[')):
                    try:
                        event = json.loads(line)
                        if isinstance(event, list):
                            events.extend(event)
                        else:
                            events.append(event)
                    except:
                        continue
        
        print(f"OK Collected {len(events)} events")
        
        # Show first event
        if events and len(events) > 0:
            print(f"\nSample event:")
            try:
                event = events[0]
                print(f"  Type: {event.get('event_type', 'N/A')}")
                print(f"  User: {event.get('user_id', 'N/A')}")
                print(f"  Device: {event.get('device_id', 'N/A')}")
                print(f"  Resource: {event.get('resource', 'N/A')[:60]}...")
                print(f"  Source: {event.get('source', 'N/A')}")
            except Exception as e:
                print(f"  Error displaying event: {e}")
        
        return events
    
    except subprocess.TimeoutExpired:
        print("Collector timed out after 30 seconds")
        return []
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_storage(events):
    """Store events and verify."""
    print(f"\n{'='*60}")
    print(f"Step 2: Storing {len(events)} events")
    print(f"{'='*60}")
    
    result = store_events(events)
    
    if "error" in result:
        print(f"Error storing events: {result['error']}")
        return False
    
    files = result.get('files_written', [])
    file_str = files[0] if files else 'logs/'
    print(f"OK Stored {result['stored_count']} events")
    print(f"   File: {file_str}")
    return True


def test_query(event_category):
    """Query stored events."""
    print(f"\n{'='*60}")
    print(f"Step 3: Querying {event_category} events")
    print(f"{'='*60}")
    
    result = query_events(
        event_category=event_category,
        page_size=10
    )
    
    if "error" in result:
        print(f"Error querying events: {result['error']}")
        return False
    
    print(f"OK Found {result['total_matches']} matching events")
    print(f"   Returned {result['count']} events (page 1)")
    
    if result['events']:
        print(f"\nSample queried event:")
        event = result['events'][0]
        print(f"  Type: {event['event_type']}")
        print(f"  Timestamp: {event['timestamp']}")
        print(f"  Resource: {event['resource']}")
    
    return True


def test_export(event_category):
    """Export to mailbox."""
    print(f"\n{'='*60}")
    print(f"Step 4: Exporting {event_category} events to mailbox")
    print(f"{'='*60}")
    
    result = export_to_mailbox(event_category=event_category)
    
    if "error" in result:
        print(f"Error exporting: {result['error']}")
        return False
    
    print(f"OK Exported {result['event_count']} events")
    print(f"   File: {result['export_file']}")
    print(f"   Metadata: {result['metadata_file']}")
    
    # Show what was exported
    mailbox_file = Path(result['export_file'])
    if mailbox_file.exists():
        with open(mailbox_file, 'r') as f:
            exported_events = json.load(f)
        print(f"\nExported events preview:")
        for i, event in enumerate(exported_events[:3], 1):
            print(f"  {i}. {event['event_type']}: {event['resource']}")
        if len(exported_events) > 3:
            print(f"  ... and {len(exported_events) - 3} more")
    
    return True


def main():
    print("="*60)
    print("REAL-WORLD COLLECTION TEST")
    print("="*60)
    print("This test will:")
    print("  1. Run file_collector to get real events")
    print("  2. Store them in logs/")
    print("  3. Query them back")
    print("  4. Export to mailbox/")
    print()
    
    # Step 1: Collect real data
    events = run_collector("file_collector")  # Use file_collector instead
    
    if not events:
        print("\nNo events collected. This might be normal if:")
        print("  - No system events occurred recently")
        print("  - Collector needs admin privileges")
        print("  - Collector is not supported on this system")
        print("\nTry running a different collector:")
        print("  python -m collectors.file_collector")
        print("  python -m collectors.process_collector")
        return 1
    
    # Step 2: Store events
    if not test_storage(events):
        return 1
    
    # Step 3: Query events
    event_category = events[0]['event_category']
    if not test_query(event_category):
        return 1
    
    # Step 4: Export to mailbox
    if not test_export(event_category):
        return 1
    
    print(f"\n{'='*60}")
    print("OK ALL STEPS COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\nYou now have:")
    print("  - Real events stored in logs/events_*.jsonl")
    print("  - Real events exported to mailbox/clean_events.json")
    print("\nCheck mailbox/clean_events.json to see the real data!")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
