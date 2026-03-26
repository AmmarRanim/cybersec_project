# Quick Reference Card — Cyber-Data Genesis

## 🎯 Project Overview
**Team 1**: Data Processing & Attack Simulation Agent  
**Goal**: Collect, normalize, enrich, and inject attack simulations into event streams  
**Output**: Enriched event stream for Team 2's Behavior Analysis

---

## 📊 10 Data Collectors

| # | Collector | Command | Admin Required | CERT Match |
|---|-----------|---------|----------------|------------|
| 1 | System | `python -m collectors.system_collector` | No | ✅ logon.csv |
| 2 | Network | `python -m collectors.network_collector` | No | ⚠️ Partial |
| 3 | Process | `python -m collectors.process_collector` | No | ✅ General |
| 4 | File | `python -m collectors.file_collector` | No | ✅ file.csv |
| 5 | Browser | `python -m collectors.browser_collector` | No | ✅ http.csv |
| 6 | Email | `python -m collectors.email_collector` | No* | ✅ email.csv |
| 7 | Windows Events | `python -m collectors.windows_event_collector` | Yes | ✅ Enhanced |
| 8 | USB History | `python -m collectors.usb_device_collector` | Yes | ✅ device.csv |
| 9 | Clipboard | `python -m collectors.clipboard_collector` | No | ✅ Insider threat |
| 10 | Registry | `python -m collectors.registry_collector` | Yes | ✅ Advanced |

*Requires Outlook installed and configured

---

## 🚀 Common Commands

```bash
# Activate environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pywin32 (critical!)
pip install pywin32
python .venv\Scripts\pywin32_postinstall.py -install

# Run dashboard
python dashboard.py

# Test all collectors
python -m collectors.system_collector
python -m collectors.network_collector
python -m collectors.process_collector
python -m collectors.file_collector
python -m collectors.browser_collector
python -m collectors.email_collector
python -m collectors.windows_event_collector
python -m collectors.usb_device_collector
python -m collectors.clipboard_collector
python -m collectors.registry_collector
```

---

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `collectors/event_schema.py` | Core data contract (StandardEvent) |
| `dashboard.py` | Web UI for testing collectors |
| `DATASET_COMPARISON.md` | CERT r4.2 vs UNSW-NB15 coverage |
| `NEW_COLLECTORS_SUMMARY.md` | Detailed docs for 5 new collectors |
| `INSTALLATION.md` | Setup and testing guide |
| `PROGRESS.md` | Implementation log |

---

## 📋 Event Schema

```python
StandardEvent(
    event_id: UUID,
    timestamp: ISO8601,
    user_id: str,
    device_id: str,
    event_type: Literal[...],
    event_category: Literal["system", "file", "network", "process", "web", "email", "device"],
    action: str,
    resource: str,
    metadata: EventMetadata,
    source: str
)
```

---

## 🎯 Detection Capabilities

### Insider Threats (CERT r4.2)
- ✅ Data exfiltration via email (external recipients, large attachments)
- ✅ Data exfiltration via USB (device history, file copying)
- ✅ Credential theft (clipboard patterns, file access)
- ✅ Pre-termination activity (job search sites, mass file copying)

### Advanced Threats
- ✅ Privilege escalation (Windows Event ID 4672)
- ✅ Persistence mechanisms (registry Run keys, services)
- ✅ Lateral movement (remote logons, unusual connections)
- ✅ LOLBins abuse (PowerShell, certutil, bitsadmin)

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "win32com not found" | `pip install pywin32` + run postinstall script |
| "Access Denied" | Run as Administrator |
| "Outlook not available" | Install and configure Outlook |
| Clipboard not detecting | Copy text (not images) during monitoring |
| WMI errors | `pip install WMI` |

---

## 📊 Dashboard

**URL**: http://localhost:5000

**Buttons**:
- 🖥️ System
- 🌐 Network
- ⚙️ Process
- 📁 File
- 🔍 Browser
- 📧 Email
- 📋 Event Log
- 💾 USB History
- 🔑 Registry
- 🚀 Collect All

---

## 🔄 Workflow

```
1. Collectors → Raw Events
2. StandardEvent Schema → Normalization
3. Enrichment Layer → User/Device Context
4. Attack Injection → Simulated Threats
5. Output → Team 2 (Behavior Analysis)
```

---

## 📦 Dependencies

```
psutil          # System/network/process monitoring
watchdog        # File system monitoring
pydantic        # Data validation
pywin32         # Windows API (email, events, clipboard, registry)
WMI             # Windows Management Instrumentation
Flask           # Dashboard web server
```

---

## 🎯 Next Phase

**Phase 2**: MCP Tool Servers
- Wrap collectors in MCP protocol
- Enable AI agent discovery and execution
- Build attack injection logic

---

## 📚 Documentation

- `README.md` — Project overview
- `TECHNICAL_REPORT.md` — Phase 1 technical details
- `DATASET_COMPARISON.md` — Dataset coverage analysis
- `NEW_COLLECTORS_SUMMARY.md` — New collectors documentation
- `INSTALLATION.md` — Setup guide
- `PROGRESS.md` — Implementation log
- `QUICK_REFERENCE.md` — This file

---

## ✅ Status

**Phase 1**: ✅ COMPLETE (10 collectors, full CERT r4.2 compatibility)  
**Phase 2**: 🔜 NEXT (MCP Tool Servers)  
**Phase 3**: 📅 PLANNED (AI Agents)
