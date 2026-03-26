# Cyber-Data Genesis 🛡️

**Autonomous SOC Threat Detection & Response System — Team 1**

> Data Processing & Attack Simulation Agent

---

## 🎯 What This Project Does

Part of a multi-agent SOC (Security Operations Center) system. Our Team 1 pipeline:

1. **Collects** raw PC logs (11 collectors: system, file, network, process, browser, email, Windows events, USB, clipboard, registry, DNS)
2. **Normalizes** them into a unified `StandardEvent` JSON schema
3. **Enriches** events with user/device context (department, privilege level, asset criticality)
4. **Simulates attacks** by injecting realistic anomalous patterns (MITRE ATT&CK techniques)
5. **Outputs** an enriched event stream for Team 2's Behavior Analysis Agent

**Dataset Coverage:**
- CERT r4.2 (Insider Threat): 100% complete
- UNSW-NB15 (Network Intrusion): 40% complete

---

## 🏗️ Architecture

```
Raw Data Sources → Collectors → StandardEvent Schema → Data Engineering Agent
                                                            ↓
                                              Clean_Events.json (mailbox)
                                                            ↓
                                        Adversarial Agent → Enriched_Attack_Stream.json
                                                            ↓
                                              Team 2 (Behavior Analysis)
```

---

## 🧩 Team Structure

| Team | Agent | Responsibility |
|------|-------|---------------|
| **Team 1 (Us)** | Data Processing + Attack Simulation | Normalize logs, inject attacks, emit enriched event stream |
| Team 2 | Behavior Analysis | Dual-monitor detection (CERT r4.2 + UNSW-NB15) |
| Team 3 | Risk & Decision + Reporting | Risk scoring, incident reports |

---

## 🚀 Quick Start

```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install pywin32 (for new collectors)
pip install pywin32
python .venv\Scripts\pywin32_postinstall.py -install

# 4. Test individual collectors
python -m collectors.system_collector
python -m collectors.email_collector
python -m collectors.dns_collector

# 5. Run the dashboard
python dashboard.py
# Open: http://localhost:5000
```

**Note**: Some collectors require Administrator privileges for full access (Windows Event Log, Registry, USB history).

---

## 📁 Project Structure

```
cybersec_project/
├── pyproject.toml               # Dependencies
├── .env.example                 # API key template
├── pdf_reader.py                # PDF text extraction utility
│
├── collectors/                  # 🔹 Phase 1: Raw data collection (11 collectors)
│   ├── event_schema.py          # StandardEvent Pydantic model (core contract)
│   ├── system_collector.py      # Login/logout, idle time (psutil + ctypes)
│   ├── file_collector.py        # File changes + USB + sensitivity (watchdog)
│   ├── network_collector.py     # TCP/UDP connections (psutil)
│   ├── process_collector.py     # Running processes + LOLBins detection (psutil)
│   ├── browser_collector.py     # Chrome/Edge history (SQLite)
│   ├── email_collector.py       # Outlook sent/received, external recipients
│   ├── windows_event_collector.py # Security events, login failures, privilege escalation
│   ├── usb_device_collector.py  # Complete USB device history from registry
│   ├── clipboard_collector.py   # Clipboard monitoring, sensitive pattern detection
│   ├── registry_collector.py    # Persistence mechanisms (Run keys, services)
│   └── dns_collector.py         # 🆕 DNS queries, C2 detection, DGA patterns
│
├── mcp_servers/                 # 🔹 Phase 2: MCP Tool Servers (TODO)
├── agents/                      # 🔹 Phase 3: Google ADK Agents (TODO)
├── mailbox/                     # Inter-agent communication (JSON files)
├── data/
│   ├── sample_logs/             # Sample log files for testing
│   └── enrichment/
│       └── user_device_map.json # User/device context mapping
├── logs/                        # Agent trace logs
├── webapp/                      # 🔹 Phase 6: Django dashboard (TODO)
└── tests/                       # Test suite
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | Google ADK |
| Sandbox Execution | Daytona |
| LLM Backend | Gemini / OpenAI |
| MCP Protocol | ADK McpToolset |
| Data Collection | psutil, watchdog, sqlite3, pywin32, WMI |
| Validation | Pydantic |
| Web Framework | Django + DRF (Phase 6) |

---

## 📄 Reference Documents

- `threat_detection_260324_130122.pdf` — Full system architecture & inter-team contracts
- `Risk_and_Decision_Agent.pdf` — Team 3's Risk Agent specification
- `DATASET_COMPARISON.md` — CERT r4.2 and UNSW-NB15 dataset coverage analysis
- `NEW_COLLECTORS_SUMMARY.md` — Detailed documentation of 5 new collectors
- `INSTALLATION.md` — Installation and testing guide
- `PROGRESS.md` — Running log of everything implemented
