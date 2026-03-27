#!/usr/bin/env python3
"""
Check Collector Time Ranges

Shows what time range each collector uses.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    print("="*70)
    print("  COLLECTOR TIME RANGES")
    print("="*70)
    print()
    
    collectors = [
        {
            "name": "system_collector",
            "function": "collect_system_snapshot",
            "time_range": "Current snapshot (no time range)",
            "description": "Current system state: CPU, memory, disk, uptime"
        },
        {
            "name": "file_collector",
            "function": "collect_file_snapshot",
            "time_range": "Last 1 hour",
            "description": "Files modified in the last hour"
        },
        {
            "name": "file_collector",
            "function": "start_file_monitor",
            "time_range": "Real-time (60 seconds default)",
            "description": "Monitors file events DURING monitoring period"
        },
        {
            "name": "network_collector",
            "function": "collect_network_connections",
            "time_range": "Current snapshot (no time range)",
            "description": "Currently active network connections"
        },
        {
            "name": "process_collector",
            "function": "collect_running_processes",
            "time_range": "Current snapshot (no time range)",
            "description": "Currently running processes"
        },
        {
            "name": "browser_collector",
            "function": "collect_browser_history",
            "time_range": "Last 24 hours (default)",
            "description": "Browser history from last 24 hours"
        },
        {
            "name": "email_collector",
            "function": "collect_outlook_emails",
            "time_range": "Last 24 hours (default)",
            "description": "Outlook emails from last 24 hours"
        },
        {
            "name": "windows_event_collector",
            "function": "collect_windows_events",
            "time_range": "Last 24 hours (default)",
            "description": "Windows security events from last 24 hours"
        },
        {
            "name": "usb_device_collector",
            "function": "collect_usb_device_history",
            "time_range": "All history (registry)",
            "description": "All USB devices ever connected (from registry)"
        },
        {
            "name": "clipboard_collector",
            "function": "monitor_clipboard",
            "time_range": "Real-time (60 seconds default)",
            "description": "Monitors clipboard DURING monitoring period"
        },
        {
            "name": "registry_collector",
            "function": "collect_persistence_mechanisms",
            "time_range": "Current snapshot (no time range)",
            "description": "Current registry persistence mechanisms"
        },
        {
            "name": "dns_collector",
            "function": "collect_dns_queries",
            "time_range": "Last 24 hours (default)",
            "description": "DNS queries from last 24 hours"
        }
    ]
    
    print("Collector Time Ranges:\n")
    
    current_collector = None
    for collector in collectors:
        if collector["name"] != current_collector:
            if current_collector is not None:
                print()
            current_collector = collector["name"]
            print(f"{collector['name']}:")
        
        print(f"  • {collector['function']}")
        print(f"    Time Range: {collector['time_range']}")
        print(f"    Description: {collector['description']}")
    
    print("\n" + "="*70)
    print("  KEY POINTS")
    print("="*70)
    print("""
1. SNAPSHOT collectors (system, network, process, registry):
   - Return current state
   - No time range
   - Fast, always return data

2. HISTORICAL collectors (browser, email, windows_event, dns):
   - Default: Last 24 hours
   - Can be configured with hours_back parameter
   - May return 0 events if no activity in time range

3. MONITOR collectors (file_collector.start_file_monitor, clipboard):
   - Real-time monitoring
   - Default: 60 seconds
   - Only capture events DURING monitoring
   - Return 0 events if no activity during monitoring

4. SPECIAL cases:
   - file_collector.collect_file_snapshot: Last 1 hour (historical)
   - file_collector.start_file_monitor: Real-time (60 seconds)
   - usb_device_collector: All history (from registry)

ANSWER TO YOUR QUESTION:
When you ran file_collector and got 0 events, it was using
start_file_monitor (real-time mode) which monitors for 60 seconds.
Since no files were modified during those 60 seconds, it returned 0 events.

To get historical data, use collect_file_snapshot instead, which looks
at files modified in the LAST HOUR.
""")
    
    print("\n" + "="*70)
    print("  EXAMPLES")
    print("="*70)
    print("""
# Get files modified in last hour (historical)
from collectors.file_collector import collect_file_snapshot
events = collect_file_snapshot()

# Monitor for file events in real-time (60 seconds)
from collectors.file_collector import start_file_monitor
events = start_file_monitor(["/path/to/watch"], duration_seconds=60)

# Get browser history from last 48 hours
from collectors.browser_collector import collect_browser_history
events = collect_browser_history(hours_back=48)

# Get current system state (no time range)
from collectors.system_collector import collect_system_snapshot
events = collect_system_snapshot()
""")
    
    print()


if __name__ == "__main__":
    main()
