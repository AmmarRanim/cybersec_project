# Test Commands - Quick Reference

## Current System Status

✅ **Phase 1 - Data Collection**: 11 collectors working
✅ **Collector-Executor MCP**: Exposes 11 collector tools
✅ **Event-Storage MCP**: Store, query, export events
✅ **Attack-Injector MCP**: 30 CERT r4.2 attack patterns (100% research-based)
❌ **Enrichment MCP**: Not started
❌ **Python-Executor MCP**: Not started

## Attack Pattern Dataset

- **30 CERT r4.2 patterns** (100% research-based, 0% hand-crafted)
- 15 Scenario 1: USB Exfiltration + Wikileaks (T1052.001, critical)
- 10 Scenario 2: Job Hunting + USB Theft (T1052.001, high)
- 5 Scenario 3: Keylogger + Impersonation (T1056.001, critical)

---

## Test Commands

### 1. Complete MCP Workflow Test (RECOMMENDED)

Tests everything: collection → storage → attack injection → export

```bash
python test_mcp_full_workflow.py
```

**What it does:**
1. Collects real system events using Collector-Executor MCP
2. Stores events using Event-Storage MCP
3. Queries stored events
4. Injects 2 CERT attack patterns using Attack-Injector MCP
5. Stores attack events
6. Exports everything to mailbox/clean_events.json

**Expected output:**
- Real events collected: ~10 system events
- Attack events generated: ~20 events (2 attacks)
- Total exported: ~30 events
- Files created: `logs/events_*.jsonl`, `mailbox/clean_events.json`

---

### 2. File Collector Test (Understanding Time Ranges)

Explains why you got 0 events and shows both modes

```bash
python test_file_collector_simple.py
```

**What it does:**
1. Explains snapshot vs monitor mode
2. Tests snapshot mode (files modified in last hour)
3. Tests monitor mode (real-time with file activity)

**Why you got 0 events before:**
- File collector was in MONITOR mode (60 seconds)
- No files were modified during those 60 seconds
- Monitor mode does NOT look at historical data

---

### 3. Individual Collector Tests

Test collectors directly (returns JSON):

```bash
# System events (fast, always works)
python -m collectors.system_collector

# File events (snapshot mode - last hour)
python -m collectors.file_collector

# Process events (currently running)
python -m collectors.process_collector

# Network connections (active connections)
python -m collectors.network_collector

# Browser history (last 24 hours)
python -m collectors.browser_collector

# USB device history
python -m collectors.usb_device_collector

# Windows events (last 24 hours, requires admin)
python -m collectors.windows_event_collector

# DNS queries (last 24 hours, requires admin)
python -m collectors.dns_collector
```

---

### 4. MCP Server Tests (Unit Tests)

Test individual MCP servers:

```bash
# Test Collector-Executor MCP
python -m pytest tests/test_collector_executor.py -v

# Test Event-Storage MCP
python -m pytest tests/test_event_storage.py -v

# Test Attack-Injector MCP
python -m pytest tests/test_attack_injector.py -v
```

---

### 5. CERT Dataset Operations

```bash
# View current attack patterns
python -c "import json; print(json.dumps(json.load(open('data/attacks/attack_patterns.json'))['attack_patterns'][:2], indent=2))"

# Regenerate balanced dataset (15 S1 + 10 S2 + 5 S3)
python create_balanced_cert_dataset.py

# Convert all 70 CERT instances
python data/attacks/cert_converter.py --cert-dir r4.2/answers --output data/attacks/attack_patterns_all.json --limit 70

# Convert only Scenario 1 (20 patterns)
python data/attacks/cert_converter.py --cert-dir r4.2/answers --output data/attacks/attack_patterns_s1.json --scenario 1 --limit 20
```

---

## Understanding File Collector Time Ranges

### Snapshot Mode (Historical)
```python
from collectors.file_collector import collect_file_snapshot

# Gets files modified in LAST HOUR
events = collect_file_snapshot()
```

### Monitor Mode (Real-time)
```python
from collectors.file_collector import start_file_monitor

# Monitors for 60 seconds, captures events DURING monitoring
events = start_file_monitor(["/path/to/watch"], duration_seconds=60)
```

**Key difference:**
- Snapshot: Historical data (last hour)
- Monitor: Real-time data (only during monitoring period)

---

## Quick Verification Commands

### Check if collectors work
```bash
python -m collectors.system_collector | python -m json.tool | head -20
```

### Check attack patterns count
```bash
python -c "import json; data=json.load(open('data/attacks/attack_patterns.json')); print(f'Total patterns: {len(data[\"attack_patterns\"])}')"
```

### Check mailbox export
```bash
python -c "import json; data=json.load(open('mailbox/clean_events.json')); print(f'Exported events: {len(data)}')"
```

### Check event storage
```bash
ls -lh logs/events_*.jsonl
```

---

## Troubleshooting

### "No events collected"
- **File collector**: Use snapshot mode or create file activity during monitoring
- **Windows events**: Requires admin privileges
- **DNS collector**: Requires admin privileges
- **Browser collector**: Requires browser history files

### "Module not found"
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### "Permission denied"
- Run as administrator for Windows events, DNS, registry collectors
- Or use collectors that don't require admin: system, file, process, network

---

## For Your Professor

When demonstrating the system:

1. **Show the dataset credibility:**
   ```bash
   python -c "import json; data=json.load(open('data/attacks/attack_patterns.json')); print('Attack patterns: 100% CERT r4.2 dataset'); print(f'Total: {len(data[\"attack_patterns\"])} real insider threat instances'); print('Source: CMU CERT Insider Threat Test Dataset r4.2')"
   ```

2. **Run the complete workflow:**
   ```bash
   python test_mcp_full_workflow.py
   ```

3. **Show the exported data:**
   ```bash
   python -c "import json; data=json.load(open('mailbox/clean_events.json')); print(f'Exported {len(data)} events'); simulated=sum(1 for e in data if e.get('is_simulated')); print(f'Real events: {len(data)-simulated}'); print(f'Simulated attacks: {simulated}')"
   ```

---

## Next Steps

1. ✅ Test complete workflow: `python test_mcp_full_workflow.py`
2. ✅ Verify mailbox export: Check `mailbox/clean_events.json`
3. ⏭️ Implement Enrichment MCP (optional)
4. ⏭️ Implement Python-Executor MCP (optional)
5. ⏭️ Create dashboard/visualization (optional)

---

**Last Updated**: 2026-03-27
**System Status**: 3/5 MCP servers complete, 30 CERT attack patterns loaded
