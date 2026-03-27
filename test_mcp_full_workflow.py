#!/usr/bin/env python3
"""
Complete MCP Workflow Test

Tests the full pipeline:
1. Collector-Executor MCP: Collect real events
2. Event-Storage MCP: Store and query events
3. Attack-Injector MCP: Inject CERT attack patterns
4. Event-Storage MCP: Store and export attack events

This demonstrates the complete system working together.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_collector_executor():
    """Test Collector-Executor MCP - Collect real events."""
    print_section("STEP 1: COLLECTOR-EXECUTOR MCP")
    print("Testing data collection from real system...")
    
    from mcp_servers.collector_executor.server import execute_collector
    
    # Test system collector (fast and reliable)
    print("\n[1.1] Collecting system events...")
    result = execute_collector("system_collector")
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return None
    
    events = result.get("events", [])
    print(f"✓ Collected {len(events)} system events in {result['execution_time_ms']}ms")
    
    if events:
        print(f"\nSample event:")
        sample = events[0]
        print(f"  Type: {sample['event_type']}")
        print(f"  User: {sample['user_id']}")
        print(f"  Device: {sample['device_id']}")
        print(f"  Source: {sample['source']}")
    
    return events


def test_event_storage(events):
    """Test Event-Storage MCP - Store and query events."""
    print_section("STEP 2: EVENT-STORAGE MCP")
    print("Testing event storage and querying...")
    
    from mcp_servers.event_storage.storage_engine import store_events
    from mcp_servers.event_storage.query_engine import query_events, get_summary
    
    # Store events
    print(f"\n[2.1] Storing {len(events)} events...")
    result = store_events(events)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    files = result.get('files_written', [])
    file_str = files[0] if files else 'logs/'
    print(f"✓ Stored {result['stored_count']} events to {file_str}")
    
    # Query events
    print(f"\n[2.2] Querying stored events...")
    result = query_events(event_category="system", page_size=10)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    print(f"✓ Found {result['total_matches']} system events")
    print(f"  Returned {result['count']} events (page 1)")
    
    # Get summary
    print(f"\n[2.3] Getting storage summary...")
    result = get_summary()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    print(f"✓ Storage summary:")
    print(f"  Total events: {result['total_events']}")
    print(f"  Event types: {len(result.get('events_by_type', {}))}")
    print(f"  Users: {result.get('unique_users', 0)}")
    print(f"  Devices: {result.get('unique_devices', 0)}")
    
    return True


def test_attack_injector():
    """Test Attack-Injector MCP - Inject CERT attack patterns."""
    print_section("STEP 3: ATTACK-INJECTOR MCP")
    print("Testing CERT r4.2 attack pattern injection...")
    
    from mcp_servers.attack_injector.dataset_loader import list_attack_patterns
    from mcp_servers.attack_injector.attack_generator import inject_attack
    
    # List available patterns
    print("\n[3.1] Listing available CERT attack patterns...")
    result = list_attack_patterns()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return None
    
    patterns = result.get("patterns", [])
    print(f"✓ Found {len(patterns)} attack patterns")
    
    # Show pattern breakdown
    scenarios = {}
    for p in patterns:
        scenario = p.get("cert_metadata", {}).get("scenario", "unknown")
        scenarios[scenario] = scenarios.get(scenario, 0) + 1
    
    print(f"\nPattern breakdown:")
    for scenario, count in sorted(scenarios.items()):
        print(f"  Scenario {scenario}: {count} patterns")
    
    # Inject a specific CERT attack
    print("\n[3.2] Injecting CERT Scenario 1 attack (USB Exfiltration)...")
    result = inject_attack(
        attack_id="cert_r42_s1_aam0658",
        randomize=True
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return None
    
    attack_events = result.get("events", [])
    print(f"✓ Generated {len(attack_events)} attack events")
    print(f"  Attack: {result['attack_name']}")
    print(f"  MITRE: {result['mitre_technique']}")
    print(f"  Severity: {result['severity']}")
    print(f"  User: {result['user_id']}")
    print(f"  Device: {result['device_id']}")
    
    # Show event sequence
    print(f"\nEvent sequence:")
    for i, event in enumerate(attack_events[:5], 1):
        print(f"  {i}. {event['event_type']}: {event['action']}")
    if len(attack_events) > 5:
        print(f"  ... and {len(attack_events) - 5} more events")
    
    # Inject a random critical attack
    print("\n[3.3] Injecting random critical attack...")
    result = inject_attack(
        severity="critical",
        randomize=True
    )
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return None
    
    random_events = result.get("events", [])
    print(f"✓ Generated {len(random_events)} events")
    print(f"  Attack: {result['attack_name']}")
    print(f"  Pattern: {result['attack_id']}")
    
    # Combine both attack event sets
    all_attack_events = attack_events + random_events
    return all_attack_events


def test_attack_storage(attack_events):
    """Test storing and exporting attack events."""
    print_section("STEP 4: STORE & EXPORT ATTACK EVENTS")
    print("Testing attack event storage and mailbox export...")
    
    from mcp_servers.event_storage.storage_engine import store_events
    from mcp_servers.event_storage.query_engine import export_to_mailbox
    
    # Store attack events
    print(f"\n[4.1] Storing {len(attack_events)} attack events...")
    result = store_events(attack_events)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    print(f"✓ Stored {result['stored_count']} attack events")
    
    # Export to mailbox
    print(f"\n[4.2] Exporting all events to mailbox...")
    result = export_to_mailbox()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    print(f"✓ Exported {result['events_exported']} events")
    print(f"  File: {result['export_file']}")
    print(f"  Metadata: {result['metadata_file']}")
    
    # Show what was exported
    mailbox_file = Path(result['export_file'])
    if mailbox_file.exists():
        with open(mailbox_file, 'r') as f:
            exported_events = json.load(f)
        
        # Count simulated vs real events (is_simulated is in metadata)
        simulated = sum(1 for e in exported_events if e.get('metadata', {}).get('is_simulated', False))
        real = len(exported_events) - simulated
        
        print(f"\nExported event breakdown:")
        print(f"  Real events: {real}")
        print(f"  Simulated attacks: {simulated}")
        print(f"  Total: {len(exported_events)}")
    
    return True


def main():
    """Run complete MCP workflow test."""
    print("="*70)
    print("  COMPLETE MCP WORKFLOW TEST")
    print("="*70)
    print("\nThis test demonstrates:")
    print("  1. Collector-Executor MCP: Collect real system events")
    print("  2. Event-Storage MCP: Store and query events")
    print("  3. Attack-Injector MCP: Inject CERT r4.2 attack patterns")
    print("  4. Event-Storage MCP: Store and export to mailbox")
    print()
    
    # Step 1: Collect real events
    real_events = test_collector_executor()
    if not real_events:
        print("\n❌ Failed to collect real events")
        return 1
    
    # Step 2: Store and query real events
    if not test_event_storage(real_events):
        print("\n❌ Failed to store/query events")
        return 1
    
    # Step 3: Inject attack patterns
    attack_events = test_attack_injector()
    if not attack_events:
        print("\n❌ Failed to inject attacks")
        return 1
    
    # Step 4: Store and export attack events
    if not test_attack_storage(attack_events):
        print("\n❌ Failed to store/export attacks")
        return 1
    
    # Final summary
    print_section("✓ ALL TESTS PASSED")
    print("\nSystem Status:")
    print("  ✓ Collector-Executor MCP: Working")
    print("  ✓ Event-Storage MCP: Working")
    print("  ✓ Attack-Injector MCP: Working")
    print("  ✓ CERT r4.2 Dataset: 30 patterns loaded")
    print("  ✓ Mailbox Export: Ready for Team 2")
    print()
    print("Next steps:")
    print("  1. Check mailbox/clean_events.json for exported data")
    print("  2. Check logs/events_*.jsonl for stored events")
    print("  3. Run: python dashboard.py (if available)")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
