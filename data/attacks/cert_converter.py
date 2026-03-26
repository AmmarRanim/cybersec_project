#!/usr/bin/env python3
"""
CERT r4.2 Dataset Converter

Converts CERT Insider Threat Test Dataset r4.2 attack scenarios
to attack_patterns.json format compatible with Attack-Injector MCP.

Usage:
    python cert_converter.py --cert-dir /path/to/cert/r4.2/answers --output attack_patterns.json [--merge]

CERT Dataset: https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247
"""

import argparse
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


# Mapping from CERT event types to StandardEvent schema
CERT_EVENT_TYPE_MAPPING = {
    "Logon": {"event_type": "logon", "event_category": "system", "action": "logon"},
    "Logoff": {"event_type": "logoff", "event_category": "system", "action": "logoff"},
    "Connect": {"event_type": "device_connect", "event_category": "device", "action": "connect"},
    "Disconnect": {"event_type": "device_disconnect", "event_category": "device", "action": "disconnect"},
    "File": {"event_type": "file_access", "event_category": "file", "action": "read"},
    "Email": {"event_type": "email_sent", "event_category": "email", "action": "send"},
    "Http": {"event_type": "http_request", "event_category": "web", "action": "request"},
}

# MITRE ATT&CK technique mapping for common CERT scenarios
CERT_SCENARIO_MITRE_MAPPING = {
    "usb_exfiltration": "T1052.001",
    "email_exfiltration": "T1114.002",
    "web_exfiltration": "T1048.003",
    "credential_theft": "T1555.003",
    "file_discovery": "T1083",
}


def parse_cert_answers(cert_dir: Path) -> Dict[str, Dict[str, Any]]:
    """
    Parse CERT r4.2 answers directory for labeled attack scenarios.
    
    Args:
        cert_dir: Path to CERT r4.2 answers/ directory
    
    Returns:
        Dictionary mapping scenario IDs to scenario metadata
    """
    scenarios = {}
    
    # Look for answers.csv or similar files
    answer_files = list(cert_dir.glob("*.csv"))
    
    if not answer_files:
        print(f"Warning: No CSV files found in {cert_dir}")
        return scenarios
    
    for answer_file in answer_files:
        print(f"Parsing {answer_file.name}...")
        
        try:
            with open(answer_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    scenario_id = row.get('scenario', row.get('id', 'unknown'))
                    
                    scenarios[scenario_id] = {
                        "user": row.get('user', row.get('userid', 'unknown')),
                        "start_date": row.get('start', row.get('start_date', '')),
                        "end_date": row.get('end', row.get('end_date', '')),
                        "description": row.get('description', row.get('scenario_description', '')),
                        "attack_type": row.get('attack_type', 'unknown'),
                        "severity": row.get('severity', 'medium')
                    }
        
        except Exception as e:
            print(f"Error parsing {answer_file}: {e}")
    
    print(f"Found {len(scenarios)} scenarios")
    return scenarios


def parse_cert_events(cert_dir: Path, scenario_id: str, user_id: str) -> List[Dict[str, Any]]:
    """
    Parse CERT event logs for a specific scenario and user.
    
    Args:
        cert_dir: Path to CERT r4.2 directory
        scenario_id: Scenario identifier
        user_id: User identifier
    
    Returns:
        List of parsed events
    """
    events = []
    
    # CERT r4.2 typically has separate log files for each event type
    log_types = ["logon.csv", "device.csv", "file.csv", "email.csv", "http.csv"]
    
    for log_type in log_types:
        log_file = cert_dir.parent / log_type
        
        if not log_file.exists():
            continue
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Filter by user
                    if row.get('user', row.get('userid')) != user_id:
                        continue
                    
                    # Parse event
                    event = {
                        "timestamp": row.get('date', row.get('timestamp', '')),
                        "activity": row.get('activity', ''),
                        "resource": row.get('content', row.get('filename', row.get('url', 'unknown'))),
                        "raw_data": row
                    }
                    
                    events.append(event)
        
        except Exception as e:
            print(f"Error parsing {log_file}: {e}")
    
    # Sort by timestamp
    events.sort(key=lambda e: e.get('timestamp', ''))
    
    return events


def convert_cert_scenario_to_pattern(
    scenario_id: str,
    scenario_data: Dict[str, Any],
    events: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Convert a CERT scenario to attack_patterns.json format.
    
    Args:
        scenario_id: Scenario identifier
        scenario_data: Scenario metadata
        events: List of events for this scenario
    
    Returns:
        Attack pattern dictionary or None if conversion fails
    """
    if not events:
        print(f"Warning: No events for scenario {scenario_id}")
        return None
    
    # Determine attack category and MITRE technique
    attack_type = scenario_data.get('attack_type', 'unknown').lower()
    category = "data_exfiltration"  # Default
    mitre_technique = "T1041"  # Default: Exfiltration Over C2 Channel
    
    if "usb" in attack_type or "removable" in attack_type:
        category = "data_exfiltration"
        mitre_technique = "T1052.001"
    elif "email" in attack_type:
        category = "data_exfiltration"
        mitre_technique = "T1114.002"
    elif "web" in attack_type or "http" in attack_type:
        category = "data_exfiltration"
        mitre_technique = "T1048.003"
    elif "credential" in attack_type or "password" in attack_type:
        category = "credential_access"
        mitre_technique = "T1555.003"
    elif "discovery" in attack_type or "reconnaissance" in attack_type:
        category = "discovery"
        mitre_technique = "T1083"
    
    # Build event sequence
    sequence = []
    
    # Sample events (limit to first 10 for pattern)
    sampled_events = events[:10]
    
    for idx, event in enumerate(sampled_events, start=1):
        activity = event.get('activity', '').lower()
        
        # Map CERT activity to StandardEvent
        event_mapping = None
        for cert_type, mapping in CERT_EVENT_TYPE_MAPPING.items():
            if cert_type.lower() in activity:
                event_mapping = mapping
                break
        
        if not event_mapping:
            # Default to file access
            event_mapping = {"event_type": "file_access", "event_category": "file", "action": "read"}
        
        # Calculate time offset (relative to last event)
        time_offset = [-(len(sampled_events) - idx) * 5, -(len(sampled_events) - idx) * 3]
        if idx == len(sampled_events):
            time_offset = [0, 0]
        
        sequence.append({
            "step": idx,
            "event_type": event_mapping["event_type"],
            "event_category": event_mapping["event_category"],
            "action": event_mapping["action"],
            "resource_patterns": [event.get('resource', 'unknown')],
            "time_offset_minutes": time_offset,
            "metadata": {
                "sensitivity_level": 1 if "sensitive" in str(event).lower() else 0
            }
        })
    
    # Build pattern
    pattern = {
        "id": f"cert_{scenario_id}",
        "name": f"CERT Scenario {scenario_id}",
        "category": category,
        "subcategory": "cert_dataset",
        "mitre_technique": mitre_technique,
        "severity": scenario_data.get('severity', 'medium'),
        "description": scenario_data.get('description', f"CERT r4.2 scenario {scenario_id}"),
        "sequence": sequence,
        "source": "cert_r4.2",
        "cert_metadata": {
            "scenario_id": scenario_id,
            "user": scenario_data.get('user'),
            "start_date": scenario_data.get('start_date'),
            "end_date": scenario_data.get('end_date')
        }
    }
    
    return pattern


def main():
    parser = argparse.ArgumentParser(description="Convert CERT r4.2 dataset to attack_patterns.json")
    parser.add_argument("--cert-dir", required=True, help="Path to CERT r4.2 answers/ directory")
    parser.add_argument("--output", default="attack_patterns.json", help="Output file path")
    parser.add_argument("--merge", action="store_true", help="Merge with existing patterns")
    parser.add_argument("--limit", type=int, help="Limit number of scenarios to convert")
    
    args = parser.parse_args()
    
    cert_dir = Path(args.cert_dir)
    output_path = Path(args.output)
    
    if not cert_dir.exists():
        print(f"Error: CERT directory not found: {cert_dir}")
        return 1
    
    print(f"Converting CERT r4.2 dataset from {cert_dir}")
    print(f"Output: {output_path}")
    
    # Parse CERT scenarios
    scenarios = parse_cert_answers(cert_dir)
    
    if not scenarios:
        print("Error: No scenarios found in CERT dataset")
        return 1
    
    # Convert scenarios to patterns
    patterns = []
    
    for idx, (scenario_id, scenario_data) in enumerate(scenarios.items()):
        if args.limit and idx >= args.limit:
            break
        
        print(f"\nConverting scenario {scenario_id}...")
        
        # Parse events for this scenario
        user_id = scenario_data.get('user')
        events = parse_cert_events(cert_dir, scenario_id, user_id)
        
        # Convert to pattern
        pattern = convert_cert_scenario_to_pattern(scenario_id, scenario_data, events)
        
        if pattern:
            patterns.append(pattern)
            print(f"  ✓ Converted {len(pattern['sequence'])} events")
        else:
            print(f"  ✗ Failed to convert")
    
    print(f"\nConverted {len(patterns)} patterns")
    
    # Load existing patterns if merging
    existing_patterns = []
    if args.merge and output_path.exists():
        print(f"Loading existing patterns from {output_path}")
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_patterns = existing_data.get('attack_patterns', [])
        print(f"Found {len(existing_patterns)} existing patterns")
    
    # Merge patterns
    all_patterns = existing_patterns + patterns
    
    # Create output dataset
    output_data = {
        "schema_version": "1.0",
        "description": "Insider threat attack patterns (custom + CERT r4.2)",
        "last_updated": datetime.now().isoformat(),
        "attack_patterns": all_patterns
    }
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Wrote {len(all_patterns)} patterns to {output_path}")
    print(f"  - {len(existing_patterns)} existing patterns")
    print(f"  - {len(patterns)} new CERT patterns")
    
    return 0


if __name__ == "__main__":
    exit(main())
