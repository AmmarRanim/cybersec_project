"""
Unit tests for Attack-Injector MCP Server

Tests dataset loading, attack generation, and tool functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.attack_injector.dataset_loader import (
    load_attack_patterns,
    get_pattern_by_id,
    filter_patterns,
    validate_pattern_schema
)
from mcp_servers.attack_injector.attack_generator import (
    inject_attack,
    load_user_device_map,
    select_random_user_device,
    generate_events_from_pattern
)


def test_load_attack_patterns():
    """Test loading attack patterns from dataset."""
    print("\n=== Test: Load Attack Patterns ===")
    
    dataset = load_attack_patterns()
    
    assert "attack_patterns" in dataset, "Dataset missing attack_patterns"
    assert isinstance(dataset["attack_patterns"], list), "attack_patterns must be a list"
    
    patterns = dataset["attack_patterns"]
    print(f"OK Loaded {len(patterns)} attack patterns")
    
    # Verify each pattern has required fields
    for pattern in patterns:
        assert "id" in pattern, f"Pattern missing id: {pattern}"
        assert "name" in pattern, f"Pattern missing name: {pattern}"
        assert "category" in pattern, f"Pattern missing category: {pattern}"
        assert "mitre_technique" in pattern, f"Pattern missing mitre_technique: {pattern}"
        assert "sequence" in pattern, f"Pattern missing sequence: {pattern}"
        print(f"  - {pattern['id']}: {pattern['name']} ({len(pattern['sequence'])} events)")
    
    print("OK All patterns have required fields")


def test_get_pattern_by_id():
    """Test retrieving specific attack pattern by ID."""
    print("\n=== Test: Get Pattern By ID ===")
    
    # Test valid pattern (use a CERT pattern)
    pattern = get_pattern_by_id("cert_r42_s1_aam0658")
    assert pattern is not None, "Pattern not found"
    assert pattern["id"] == "cert_r42_s1_aam0658"
    print(f"OK Found pattern: {pattern['name']}")
    
    # Test invalid pattern
    pattern = get_pattern_by_id("invalid_pattern_id")
    assert pattern is None, "Should return None for invalid ID"
    print("OK Returns None for invalid ID")


def test_filter_patterns():
    """Test filtering patterns by criteria."""
    print("\n=== Test: Filter Patterns ===")
    
    # Filter by category
    patterns = filter_patterns(category="data_exfiltration")
    assert len(patterns) > 0, "Should find data_exfiltration patterns"
    print(f"OK Found {len(patterns)} data_exfiltration patterns")
    
    # Filter by MITRE technique
    patterns = filter_patterns(mitre_technique="T1052.001")
    assert len(patterns) > 0, "Should find T1052.001 patterns"
    print(f"OK Found {len(patterns)} T1052.001 patterns")
    
    # Filter by severity
    patterns = filter_patterns(severity="high")
    assert len(patterns) > 0, "Should find high severity patterns"
    print(f"OK Found {len(patterns)} high severity patterns")


def test_load_user_device_map():
    """Test loading user/device mappings."""
    print("\n=== Test: Load User/Device Map ===")
    
    user_device_map = load_user_device_map()
    
    assert "users" in user_device_map, "Map missing users"
    assert "devices" in user_device_map, "Map missing devices"
    
    users = user_device_map["users"]
    devices = user_device_map["devices"]
    
    print(f"OK Loaded {len(users)} users and {len(devices)} devices")
    
    # Verify user structure
    for user_id, user_data in users.items():
        assert "username" in user_data, f"User {user_id} missing username"
        assert "department" in user_data, f"User {user_id} missing department"
        assert "devices" in user_data, f"User {user_id} missing devices"
        print(f"  - {user_id}: {user_data['username']} ({user_data['department']})")


def test_select_random_user_device():
    """Test random user/device selection."""
    print("\n=== Test: Select Random User/Device ===")
    
    user_id, device_id = select_random_user_device()
    
    assert user_id is not None, "Should return user_id"
    assert device_id is not None, "Should return device_id"
    
    print(f"OK Selected user {user_id} and device {device_id}")


def test_generate_events_from_pattern():
    """Test generating events from attack pattern."""
    print("\n=== Test: Generate Events From Pattern ===")
    
    # Get a pattern (use a CERT pattern)
    pattern = get_pattern_by_id("cert_r42_s1_aam0658")
    assert pattern is not None, "Pattern not found"
    
    # Generate events
    events = generate_events_from_pattern(pattern, "U001", "WORKSTATION-01", randomize=False)
    
    assert len(events) > 0, "Should generate events"
    assert len(events) == len(pattern["sequence"]), "Should generate one event per sequence step"
    
    print(f"OK Generated {len(events)} events")
    
    # Verify event structure
    for event in events:
        assert hasattr(event, 'event_id'), "Event missing event_id"
        assert hasattr(event, 'timestamp'), "Event missing timestamp"
        assert hasattr(event, 'user_id'), "Event missing user_id"
        assert hasattr(event, 'device_id'), "Event missing device_id"
        assert hasattr(event, 'event_type'), "Event missing event_type"
        assert hasattr(event, 'metadata'), "Event missing metadata"
        
        # Verify simulation markers
        assert event.metadata.is_simulated == True, "Event should be marked as simulated"
        assert event.metadata.attack_type is not None, "Event should have attack_type"
        assert event.metadata.mitre_technique is not None, "Event should have mitre_technique"
        
        print(f"  - {event.event_type}: {event.resource}")
    
    print("OK All events have required fields and simulation markers")


def test_inject_attack():
    """Test inject_attack function."""
    print("\n=== Test: Inject Attack ===")
    
    # Test with specific attack ID (use a CERT pattern)
    result = inject_attack(attack_id="cert_r42_s1_aam0658")
    
    assert "events" in result, "Result missing events"
    assert "count" in result, "Result missing count"
    assert "attack_id" in result, "Result missing attack_id"
    assert "mitre_technique" in result, "Result missing mitre_technique"
    
    events = result["events"]
    assert len(events) > 0, "Should generate events"
    assert result["count"] == len(events), "Count should match events length"
    
    print(f"OK Injected attack: {result['attack_name']}")
    print(f"  - Attack ID: {result['attack_id']}")
    print(f"  - MITRE Technique: {result['mitre_technique']}")
    print(f"  - Event Count: {result['count']}")
    print(f"  - User: {result['user_id']}")
    print(f"  - Device: {result['device_id']}")
    
    # Verify events are dictionaries (not Pydantic models)
    for event in events:
        assert isinstance(event, dict), "Events should be dictionaries"
        assert "event_id" in event, "Event missing event_id"
        assert "metadata" in event, "Event missing metadata"
        assert event["metadata"]["is_simulated"] == True, "Event should be marked as simulated"
    
    print("OK All events are valid dictionaries with simulation markers")


def test_inject_attack_by_category():
    """Test injecting attack by category."""
    print("\n=== Test: Inject Attack By Category ===")
    
    result = inject_attack(category="data_exfiltration", randomize=True)
    
    assert "events" in result, "Result missing events"
    assert result["attack_type"] == "data_exfiltration", "Should match requested category"
    
    print(f"OK Injected random data_exfiltration attack: {result['attack_name']}")
    print(f"  - Event Count: {result['count']}")


def test_inject_attack_invalid_id():
    """Test injecting attack with invalid ID."""
    print("\n=== Test: Inject Attack Invalid ID ===")
    
    result = inject_attack(attack_id="invalid_attack_id")
    
    assert "error" in result, "Should return error for invalid ID"
    assert result["error"]["type"] == "validation_error", "Should be validation error"
    
    print(f"OK Returns error for invalid attack ID: {result['error']['message']}")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Attack-Injector MCP Server - Unit Tests")
    print("=" * 60)
    
    try:
        test_load_attack_patterns()
        test_get_pattern_by_id()
        test_filter_patterns()
        test_load_user_device_map()
        test_select_random_user_device()
        test_generate_events_from_pattern()
        test_inject_attack()
        test_inject_attack_by_category()
        test_inject_attack_invalid_id()
        
        print("\n" + "=" * 60)
        print("OK ALL TESTS PASSED")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\nFAIL TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    except Exception as e:
        print(f"\nFAIL UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
