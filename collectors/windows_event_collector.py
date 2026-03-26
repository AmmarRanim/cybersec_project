"""
Windows Event Log Collector — Captures security events from Windows Event Log.
Tracks login failures, privilege escalation, service creation, process creation.
Critical for detecting authentication anomalies and privilege abuse (CERT r4.2).
"""

import getpass
import socket
from datetime import datetime, timedelta
from typing import Optional
from collectors.event_schema import StandardEvent, create_event

# Try to import win32evtlog for Windows Event Log access
try:
    import win32evtlog
    import win32evtlogutil
    import win32con
    EVTLOG_AVAILABLE = True
except ImportError:
    EVTLOG_AVAILABLE = False
    print("[windows_event_collector] win32evtlog not available. Install: pip install pywin32")


# Critical Event IDs for security monitoring
SECURITY_EVENT_IDS = {
    # Authentication
    4624: "Successful logon",
    4625: "Failed logon",
    4634: "Logoff",
    4648: "Logon using explicit credentials",
    4672: "Special privileges assigned (admin rights)",
    
    # Account Management
    4720: "User account created",
    4722: "User account enabled",
    4723: "Password change attempt",
    4724: "Password reset attempt",
    4725: "User account disabled",
    4726: "User account deleted",
    4738: "User account changed",
    4740: "User account locked out",
    4767: "User account unlocked",
    
    # Process/Service
    4688: "Process creation",
    4689: "Process termination",
    7045: "Service installed",
    7040: "Service start type changed",
    
    # Policy Changes
    4719: "System audit policy changed",
    4739: "Domain policy changed",
    
    # Scheduled Tasks
    4698: "Scheduled task created",
    4699: "Scheduled task deleted",
    4700: "Scheduled task enabled",
    4701: "Scheduled task disabled",
}


def collect_windows_events(
    hours_back: int = 24,
    max_events: int = 1000,
    event_ids: Optional[list[int]] = None
) -> list[StandardEvent]:
    """
    Collect security events from Windows Event Log.
    Requires administrator privileges for full access.
    """
    if not EVTLOG_AVAILABLE:
        print("[windows_event_collector] Windows Event Log access not available (pywin32 not installed)")
        return []
    
    events = []
    device_id = socket.gethostname()
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    
    # Default to critical security events
    if event_ids is None:
        event_ids = [4624, 4625, 4672, 4688, 7045, 4698]
    
    try:
        # Open Security log
        hand = win32evtlog.OpenEventLog(None, "Security")
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        
        total = 0
        while total < max_events:
            # Read events in batches
            event_records = win32evtlog.ReadEventLog(hand, flags, 0)
            if not event_records:
                break
            
            for event in event_records:
                if total >= max_events:
                    break
                
                # Check if event is in our filter list
                if event.EventID not in event_ids:
                    continue
                
                # Convert Windows timestamp to datetime
                try:
                    event_time = datetime.fromtimestamp(int(event.TimeGenerated.timestamp()))
                    if event_time < cutoff_time:
                        # Events are in reverse chronological order, so we can stop
                        total = max_events
                        break
                except Exception:
                    continue
                
                # Extract user from event (if available)
                user_id = getpass.getuser()  # Default to current user
                if event.StringInserts and len(event.StringInserts) > 0:
                    # Try to extract username from event data
                    for insert in event.StringInserts:
                        if insert and "\\" in insert:
                            # Format: DOMAIN\Username
                            user_id = insert.split("\\")[-1]
                            break
                        elif insert and "@" not in insert and insert.strip():
                            # Might be a username
                            user_id = insert.strip()
                            break
                
                # Get event description
                event_desc = SECURITY_EVENT_IDS.get(event.EventID, f"Event {event.EventID}")
                
                # Determine event type and category
                event_type = "logon"
                event_category = "system"
                action = "unknown"
                
                if event.EventID in [4624, 4648]:
                    event_type = "logon"
                    action = "login_success"
                elif event.EventID == 4625:
                    event_type = "logon"
                    action = "login_failed"
                elif event.EventID == 4634:
                    event_type = "logoff"
                    action = "logout"
                elif event.EventID == 4672:
                    event_type = "logon"
                    action = "privilege_escalation"
                elif event.EventID == 4688:
                    event_type = "process_start"
                    event_category = "process"
                    action = "create"
                elif event.EventID == 7045:
                    event_type = "process_start"
                    event_category = "process"
                    action = "service_install"
                elif event.EventID in [4698, 4699, 4700, 4701]:
                    event_type = "process_start"
                    event_category = "process"
                    action = "scheduled_task"
                
                # Extract additional data from StringInserts
                metadata = {
                    "event_id": event.EventID,
                    "event_description": event_desc,
                }
                
                # For process creation events, try to extract command line
                if event.EventID == 4688 and event.StringInserts and len(event.StringInserts) > 5:
                    try:
                        process_name = event.StringInserts[5] if len(event.StringInserts) > 5 else ""
                        command_line = event.StringInserts[8] if len(event.StringInserts) > 8 else ""
                        metadata["process_name"] = process_name
                        metadata["command_line"] = command_line[:500]  # Truncate
                    except Exception:
                        pass
                
                events.append(create_event(
                    event_type=event_type,
                    event_category=event_category,
                    action=action,
                    resource=f"event_{event.EventID}",
                    user_id=user_id,
                    device_id=device_id,
                    source="windows_event_log",
                    timestamp=event_time.isoformat(),
                    **metadata
                ))
                
                total += 1
        
        win32evtlog.CloseEventLog(hand)
        print(f"[windows_event_collector] Collected {len(events)} security events")
        
    except Exception as e:
        print(f"[windows_event_collector] Error reading Windows Event Log: {e}")
        print("  Note: Administrator privileges may be required for full access")
    
    return events


if __name__ == "__main__":
    import json
    print("Collecting Windows security events...")
    print("Note: Run as Administrator for full access\n")
    events = collect_windows_events(hours_back=24)
    print(f"\nCollected {len(events)} events")
    for e in events[:5]:
        print(json.dumps(e.model_dump(), indent=2))
