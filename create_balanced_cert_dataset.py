#!/usr/bin/env python3
"""
Create a balanced CERT r4.2 attack pattern dataset with all 3 scenarios.

Mix: 15 Scenario 1 + 10 Scenario 2 + 5 Scenario 3 = 30 total patterns
"""

import subprocess
import json
from pathlib import Path

def run_converter(scenario, limit, output):
    """Run CERT converter for a specific scenario."""
    cmd = [
        "python", "data/attacks/cert_converter.py",
        "--cert-dir", "r4.2/answers",
        "--output", output,
        "--scenario", str(scenario),
        "--limit", str(limit)
    ]
    
    print(f"\n{'='*60}")
    print(f"Converting Scenario {scenario} ({limit} patterns)")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True

def merge_datasets(files, output):
    """Merge multiple pattern files into one."""
    all_patterns = []
    
    for file in files:
        if not Path(file).exists():
            print(f"Warning: {file} not found")
            continue
        
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            patterns = data.get('attack_patterns', [])
            all_patterns.extend(patterns)
            print(f"Loaded {len(patterns)} patterns from {file}")
    
    # Create merged dataset
    merged = {
        "schema_version": "1.0",
        "description": "CERT r4.2 insider threat attack patterns (all scenarios)",
        "last_updated": "2026-03-27",
        "attack_patterns": all_patterns
    }
    
    # Write output
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2)
    
    print(f"\nMerged {len(all_patterns)} patterns to {output}")
    return len(all_patterns)

def main():
    print("="*60)
    print("Creating Balanced CERT r4.2 Attack Pattern Dataset")
    print("="*60)
    print("Mix: 15 Scenario 1 + 10 Scenario 2 + 5 Scenario 3 = 30 total")
    print()
    
    # Convert each scenario
    temp_files = []
    
    # Scenario 1: USB Exfiltration + Wikileaks (15 patterns)
    if run_converter(1, 15, "data/attacks/temp_s1.json"):
        temp_files.append("data/attacks/temp_s1.json")
    
    # Scenario 2: Job Hunting + USB Theft (10 patterns)
    if run_converter(2, 10, "data/attacks/temp_s2.json"):
        temp_files.append("data/attacks/temp_s2.json")
    
    # Scenario 3: Keylogger + Impersonation (5 patterns)
    if run_converter(3, 5, "data/attacks/temp_s3.json"):
        temp_files.append("data/attacks/temp_s3.json")
    
    # Merge all patterns
    print("\n" + "="*60)
    print("Merging all scenarios")
    print("="*60)
    
    total = merge_datasets(temp_files, "data/attacks/attack_patterns.json")
    
    # Clean up temp files
    for file in temp_files:
        Path(file).unlink(missing_ok=True)
    
    print("\n" + "="*60)
    print(f"SUCCESS: Created {total} CERT r4.2 attack patterns")
    print("="*60)
    print("\nBreakdown:")
    print("  - 15 Scenario 1: USB Exfiltration + Wikileaks (T1052.001)")
    print("  - 10 Scenario 2: Job Hunting + USB Theft (T1052.001)")
    print("  -  5 Scenario 3: Keylogger + Impersonation (T1056.001)")
    print("\nAll patterns are from real CERT r4.2 insider threat instances.")
    print()

if __name__ == "__main__":
    main()
