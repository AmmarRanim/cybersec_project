"""
Test Event-Storage MCP Server

Basic tests to verify storage, query, summary, and export functionality.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.event_storage.storage_engine import store_events
from mcp_servers.event_storage.query_engine import query_events, get_summary, export_to_mailbox
from collectors.event_schema import create_event


def test_store_and_query():
    """Test storing and querying events."""
    print("Testing store and query...")
    
    # Create test events
    test_events = [
        create_event(
            event_type="file_access",
            event_category="file",
            action="read",
            resource="C:\\test\\file1.txt",
            user_id="U001",
            device_id="TEST-DEVICE",
            source="test",
            timestamp="2024-01-15T10:00:00"
        ).model_dump(),
        create_event(
            event_type="file_access",
            event_category="file",
            action="write",
            resource="C:\\test\\file2.txt",
            user_id="U002",
            device_id="TEST-DEVICE",
            source="test",
            timestamp="2024-01-15T11:00:00"
        ).model_dump(),
        create_event(
            event_type="logon",
            event_category="system",
            action="login",
            resource="WORKSTATION-01",
            user_id="U001",
            device_id="TEST-DEVICE",
            source="test",
            timestamp="2024-01-15T09:00:00"
        ).model_dump()
    ]
    
    # Store events
    store_result = store_events(test_events)
    print(f"✓ Stored {store_result['stored_count']} events")
    assert store_result['stored_count'] == 3
    
    # Query all events
    query_result = query_events()
    print(f"✓ Queried {query_result['count']} events (total: {query_result['total_matches']})")
    assert query_result['count'] > 0
    
    # Query with filter
    file_events = query_events(event_category="file")
    print(f"✓ Filtered file events: {file_events['count']}")
    assert file_events['count'] >= 2
    
    # Query with user filter
    user_events = query_events(user_id="U001")
    print(f"✓ Filtered user U001 events: {user_events['count']}")
    assert user_events['count'] >= 2
    
    # Test pagination
    page1 = query_events(page_size=1, page=1)
    print(f"✓ Pagination works: page 1 has {page1['count']} events")
    assert page1['count'] == 1
    
    print("✓ Store and query tests passed!\n")


def test_summary():
    """Test summary statistics."""
    print("Testing summary statistics...")
    
    summary = get_summary()
    print(f"✓ Total events: {summary['total_events']}")
    print(f"✓ Unique users: {summary['unique_users']}")
    print(f"✓ Unique devices: {summary['unique_devices']}")
    print(f"✓ Events by type: {summary['events_by_type']}")
    print(f"✓ Events by category: {summary['events_by_category']}")
    
    assert summary['total_events'] > 0
    assert summary['unique_users'] > 0
    assert summary['unique_devices'] > 0
    
    print("✓ Summary tests passed!\n")


def test_export():
    """Test mailbox export."""
    print("Testing mailbox export...")
    
    export_result = export_to_mailbox(event_category="file")
    print(f"✓ Exported {export_result['events_exported']} events")
    print(f"✓ Export file: {export_result['export_file']}")
    print(f"✓ Metadata file: {export_result['metadata_file']}")
    
    # Verify files exist
    export_file = Path(export_result['export_file'])
    metadata_file = Path(export_result['metadata_file'])
    
    assert export_file.exists(), "Export file should exist"
    assert metadata_file.exists(), "Metadata file should exist"
    
    # Verify export file content
    with open(export_file, 'r') as f:
        exported_events = json.load(f)
        print(f"✓ Verified {len(exported_events)} events in export file")
    
    # Verify metadata file content
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
        print(f"✓ Metadata: {metadata['event_count']} events, source: {metadata['data_source']}")
    
    print("✓ Export tests passed!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Event-Storage MCP Server Tests")
    print("=" * 60 + "\n")
    
    try:
        test_store_and_query()
        test_summary()
        test_export()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
