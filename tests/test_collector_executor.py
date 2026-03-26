"""
Test suite for Collector-Executor MCP Server.

Tests basic functionality, tool definitions, and collector execution.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.collector_executor.tool_definitions import COLLECTOR_TOOLS
from mcp_servers.common.utils import (
    setup_logger,
    create_error_response,
    create_success_response,
    validate_required_fields,
    sanitize_path
)


def test_tool_definitions():
    """Test that all 11 collector tools are defined."""
    print("Testing tool definitions...")
    
    assert len(COLLECTOR_TOOLS) == 11, f"Expected 11 tools, got {len(COLLECTOR_TOOLS)}"
    
    expected_tools = [
        "collect_system_events",
        "collect_file_events",
        "collect_network_events",
        "collect_process_events",
        "collect_browser_events",
        "collect_email_events",
        "collect_windows_events",
        "collect_usb_events",
        "collect_clipboard_events",
        "collect_registry_events",
        "collect_dns_events",
    ]
    
    tool_names = [tool.name for tool in COLLECTOR_TOOLS]
    for expected in expected_tools:
        assert expected in tool_names, f"Tool {expected} not found in definitions"
    
    print("  ✓ All 11 tools defined correctly")


def test_time_range_parameters():
    """Test that time-range collectors have hours_back parameter."""
    print("Testing time-range parameters...")
    
    time_range_collectors = [
        "collect_browser_events",
        "collect_email_events",
        "collect_windows_events",
        "collect_dns_events",
    ]
    
    for tool in COLLECTOR_TOOLS:
        if tool.name in time_range_collectors:
            assert "hours_back" in tool.inputSchema["properties"], \
                f"Tool {tool.name} missing hours_back parameter"
            
            hours_back_schema = tool.inputSchema["properties"]["hours_back"]
            assert hours_back_schema["type"] == "integer", \
                f"hours_back should be integer for {tool.name}"
            assert hours_back_schema["minimum"] == 1, \
                f"hours_back minimum should be 1 for {tool.name}"
            assert hours_back_schema["maximum"] == 720, \
                f"hours_back maximum should be 720 for {tool.name}"
    
    print("  ✓ Time-range parameters configured correctly")


def test_common_utils():
    """Test common utility functions."""
    print("Testing common utilities...")
    
    # Test error response
    error = create_error_response("test_error", "Test message", {"detail": "test"})
    assert error["error"]["type"] == "test_error"
    assert error["error"]["message"] == "Test message"
    assert error["error"]["details"]["detail"] == "test"
    assert "timestamp" in error["error"]
    
    # Test success response
    success = create_success_response({"data": "test"})
    assert success["success"] is True
    assert success["data"] == "test"
    assert "timestamp" in success
    
    # Test field validation
    is_valid, error_msg = validate_required_fields(
        {"field1": "value1", "field2": "value2"},
        ["field1", "field2"]
    )
    assert is_valid is True
    assert error_msg is None
    
    is_valid, error_msg = validate_required_fields(
        {"field1": "value1"},
        ["field1", "field2"]
    )
    assert is_valid is False
    assert "field2" in error_msg
    
    # Test path sanitization
    is_safe, error_msg = sanitize_path("logs/events.json")
    assert is_safe is True
    
    is_safe, error_msg = sanitize_path("../etc/passwd")
    assert is_safe is False
    assert ".." in error_msg
    
    print("  ✓ Common utilities working correctly")


def test_collector_imports():
    """Test that all collector modules can be imported."""
    print("Testing collector imports...")
    
    import importlib
    
    collectors = [
        "system_collector",
        "file_collector",
        "network_collector",
        "process_collector",
        "usb_device_collector",
        "clipboard_collector",
        "registry_collector",
    ]
    
    for collector in collectors:
        try:
            module = importlib.import_module(f"collectors.{collector}")
            print(f"  ✓ {collector} imported successfully")
        except ImportError as e:
            print(f"  ✗ {collector} import failed: {e}")
            raise
    
    print("  ✓ All collector modules can be imported")


def test_server_import():
    """Test that the MCP server can be imported."""
    print("Testing server import...")
    
    try:
        from mcp_servers.collector_executor import server
        print("  ✓ Server module imported successfully")
    except ImportError as e:
        print(f"  ✗ Server import failed: {e}")
        raise


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Collector-Executor MCP Server Test Suite")
    print("="*60 + "\n")
    
    tests = [
        test_tool_definitions,
        test_time_range_parameters,
        test_common_utils,
        test_collector_imports,
        test_server_import,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Test error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
