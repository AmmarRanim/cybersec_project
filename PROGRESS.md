# 📋 Progress Log — Cyber-Data Genesis

> Running record of everything implemented. Updated after each work session.

---

## ✅ Phase 1: Project Setup & Data Collection Layer — COMPLETE

**Date:** 2026-03-25 to 2026-03-26

### 1.1 — Project Structure & Environment
- Created full folder structure (`collectors/`, `agents/`, `mcp_servers/`, `mailbox/`, `data/`, `logs/`, `webapp/`, `tests/`)
- Set up `pyproject.toml` with all dependencies
- Created `.env.example` with API key template
- Initialized `.venv` virtual environment
- Installed core dependencies: `psutil`, `watchdog`, `pydantic`, `pywin32`, `WMI`

### 1.2 — Event Schema (`collectors/event_schema.py`)
- Defined `StandardEvent` Pydantic model — the **core contract** between Team 1 and Team 2
- Defined `EventMetadata` model with fields for all event types (system, file, network, process, web, email, device, registry, clipboard)
- Includes attack simulation fields (`is_simulated`, `attack_type`, `mitre_technique`)
- Extended metadata to support new collectors (email, Windows events, USB, clipboard, registry)
- Created `create_event()` helper function

### 1.3 — Collectors (11 total) ✅ CERT r4.2 100% Compatible + UNSW-NB15 40% Compatible

| Collector | File | What it captures | CERT Dataset Match | Status |
|-----------|------|------------------|-------------------|--------|
| System | `system_collector.py` | Login sessions, idle time, boot time | ✅ logon.csv | ✅ Working |
| Network | `network_collector.py` | Active TCP/UDP connections, src/dst IPs, ports, owning process | ✅ UNSW-NB15 flow | ✅ Working |
| Process | `process_collector.py` | Running processes, LOLBins detection, CPU/memory usage | ✅ General | ✅ Working |
| File | `file_collector.py` | File create/modify/delete/move, USB detection, sensitivity classification | ✅ file.csv | ✅ Working |
| Browser | `browser_collector.py` | Chrome/Edge history from SQLite, suspicious domain flagging | ✅ http.csv | ✅ Working |
| Email | `email_collector.py` | Outlook sent/received, external recipients, attachments | ✅ email.csv | ✅ Working |
| Windows Events | `windows_event_collector.py` | Login failures, privilege escalation, service creation | ✅ Enhanced | ✅ Working |
| USB History | `usb_device_collector.py` | Complete USB device history from registry | ✅ device.csv | ✅ Working |
| Clipboard | `clipboard_collector.py` | Clipboard monitoring, sensitive pattern detection | ✅ Insider threat | ✅ Working |
| Registry | `registry_collector.py` | Persistence mechanisms (Run keys, services, startup) | ✅ Advanced | ✅ Working |
| **DNS** | `dns_collector.py` | DNS queries, C2 detection, DGA patterns, DNS tunneling | ✅ UNSW-NB15 service | 🆕 NEW |

### 1.4 — Enrichment Layer
- Created `data/enrichment/user_device_map.json` with sample users (IT admin, marketing, finance) and devices with criticality levels

### 1.5 — Utilities
- Created `pdf_reader.py` for extracting text from project PDFs
- Created `DATASET_COMPARISON.md` documenting CERT r4.2 and UNSW-NB15 dataset coverage

### 1.6 — Dashboard
- Flask web application with 11 collector buttons
- Real-time data visualization
- Background file watcher
- Color-coded event categories
- Time range slider for time-sensitive collectors

---

## ✅ Phase 1: Data Collection Layer — COMPLETE

**Summary:**
- 11 collectors implemented
- CERT r4.2: 100% coverage (all 5 CSV files)
- UNSW-NB15: 40% coverage (flow + DNS features)
- Dashboard with time range control
- Full documentation and testing guides

**Date Completed:** 2026-03-26

---

## 🔜 Next: Phase 2 — MCP Tool Servers

- [ ] Local-Log-Reader MCP
- [ ] Web-Scraper MCP
- [ ] Python-Executor MCP (Daytona)
- [ ] Attack-Injector MCP
- [ ] Sequential-Thinking MCP
