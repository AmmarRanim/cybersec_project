# Technical Report — Phase 1: Data Collection & Normalization Layer

**Project:** Cyber-Data Genesis — Autonomous SOC Threat Detection  
**Team:** Team 1 — Data Processing & Attack Simulation Agent  
**Date:** March 25, 2026

---

## 1. Project Context

### 1.1 What is this project?

We are building an **autonomous Security Operations Center (SOC)** using **AI agents**. The system is divided into 3 teams:

| Team | Agent | Role |
|------|-------|------|
| **Team 1 (us)** | Data Processing + Attack Simulation | Collects raw data, normalizes it, injects simulated attacks |
| Team 2 | Behavior Analysis | Detects anomalies using ML (Isolation Forest) on two datasets |
| Team 3 | Risk & Decision | Scores risk, classifies severity, generates incident reports |

The agents communicate via structured JSON messages. Our Team 1 output feeds directly into Team 2's analysis pipeline.

### 1.2 What did we build in Phase 1?

Phase 1 focuses on the **data collection and normalization layer** — the foundation that everything else depends on. We built:

1. A **unified event schema** (the data contract between teams)
2. **5 data collectors** that capture real-time activity from the local PC
3. An **enrichment layer** (static user/device context mapping)
4. A **visualization dashboard** to test and demo the collectors

### 1.3 Technology choices

| Technology | Why we chose it |
|-----------|----------------|
| **Python 3.12** | Standard for cybersecurity tooling and ML |
| **Pydantic** | Data validation — enforces our event schema at runtime, catches bad data before it enters the pipeline |
| **psutil** | Cross-platform process and system monitoring — gives us network connections, running processes, boot time, logged-in users |
| **watchdog** | Real-time filesystem monitoring — fires events when files are created/modified/deleted |
| **ctypes** | Direct Windows API calls for idle time detection (no external dependency needed) |
| **sqlite3** | Read browser history databases directly — Chrome and Edge store history in SQLite |
| **Flask** | Lightweight web framework for the visualization dashboard |

---

## 2. The Event Schema (`collectors/event_schema.py`)

### 2.1 Why a unified schema matters

In a multi-team project, **data format consistency is critical**. If our collectors each output data in different formats, Team 2's Behavior Analysis Agent cannot process it. The event schema is our **contract** — it guarantees that every event, regardless of source, has the same structure.

This is inspired by **ECS (Elastic Common Schema)**, a real-world standard used by Elasticsearch for normalizing security logs.

### 2.2 How it works

We defined two Pydantic models:

**`EventMetadata`** — A flexible container for type-specific fields. Every event type populates different fields:

```python
class EventMetadata(BaseModel):
    # System events
    idle_time_seconds: Optional[float] = None
    session_duration_minutes: Optional[float] = None
    
    # File events  
    file_path: Optional[str] = None
    sensitivity_level: Optional[int] = None   # 0=low, 1=medium, 2=high
    is_usb: Optional[bool] = None
    
    # Network events
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    protocol: Optional[str] = None
    process_name: Optional[str] = None
    
    # Process events
    pid: Optional[int] = None
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    
    # Browser events
    url: Optional[str] = None
    domain: Optional[str] = None
    
    # Attack simulation (Phase 2 — Adversarial Agent will populate these)
    is_simulated: Optional[bool] = False
    attack_type: Optional[str] = None        # e.g., "lateral_movement"
    mitre_technique: Optional[str] = None    # e.g., "T1078"
```

**`StandardEvent`** — The main event model. Every event has these fields:

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `event_id` | UUID | `"3f7312b4-6c5d-..."` | Unique identifier for each event |
| `timestamp` | ISO 8601 | `"2026-03-25T18:05:10"` | When the event occurred |
| `user_id` | string | `"Ranim"` | Who caused the event |
| `device_id` | string | `"DESKTOP-V1QS329"` | Which machine |
| `event_type` | enum | `"logon"`, `"file_access"`, `"network_connection"` | Specific event type |
| `event_category` | enum | `"system"`, `"file"`, `"network"`, `"process"`, `"web"` | High-level category |
| `action` | string | `"connect"`, `"create"`, `"visit"` | What happened |
| `resource` | string | `"192.168.1.13:8009"` | Target resource |
| `metadata` | EventMetadata | *(varies by type)* | Type-specific details |
| `source` | string | `"psutil"`, `"watchdog"` | Which library collected it |

### 2.3 The `create_event()` helper

Instead of manually constructing events, we use a helper function that handles defaults:

```python
event = create_event(
    event_type="network_connection",
    event_category="network",
    action="connect",
    resource="192.168.1.13:8009",
    user_id="Ranim",
    device_id="DESKTOP-V1QS329",
    source="psutil",
    src_ip="192.168.1.23", dst_ip="192.168.1.13",  # these go into metadata
    protocol="TCP", process_name="msedge.exe",
)
```

The `**metadata_kwargs` pattern lets us pass metadata fields as flat keyword arguments — cleaner than nesting dictionaries.

---

## 3. The Collectors

### 3.1 System Collector (`collectors/system_collector.py`)

**Purpose:** Captures login sessions, idle time, and user identity.

**How it works:**
1. Uses `getpass.getuser()` to identify the current user
2. Uses `socket.gethostname()` to identify the machine
3. Uses `psutil.boot_time()` to calculate session duration since boot
4. Uses the **Windows `GetLastInputInfo` API** (via `ctypes`) to measure idle time — this tells us how many milliseconds since the last keyboard/mouse input

**Key technical detail — Windows idle time detection:**
```python
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.UINT),
        ("dwTime", ctypes.wintypes.DWORD),
    ]
lii = LASTINPUTINFO()
lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
```
This is a direct call to the Windows User32 DLL. `GetTickCount()` returns system uptime in milliseconds, and `LASTINPUTINFO.dwTime` stores the tick count at last user input. The difference gives idle time.

**Why this matters for SOC:** Unusual idle patterns can indicate compromised accounts (attacker logged in but not actively using the machine) or automated scripts running unattended.

**Test result:** ✅ 1 event — `Ranim@DESKTOP-V1QS329`, idle 0.15s, session duration 17,730 minutes.

---

### 3.2 Network Collector (`collectors/network_collector.py`)

**Purpose:** Captures all active TCP/UDP connections on the machine.

**How it works:**
1. Calls `psutil.net_connections(kind="inet")` to enumerate all IPv4 connections
2. Filters out listening sockets (connections with no remote address)
3. For each connection, extracts: source IP:port, destination IP:port, protocol (TCP/UDP)
4. Maps each connection to its **owning process** via `psutil.Process(pid).name()`

**Key design decision:** We skip connections without a remote address (`conn.raddr`) because those are just listening sockets — they aren't actual communications, so they don't carry security-relevant data.

**Why this matters for SOC:** Network connections reveal data exfiltration (unusual outbound traffic), command & control channels (connections to suspicious IPs), and lateral movement (internal-to-internal connections on unexpected ports).

**Test result:** ✅ 69 events — captured connections from `msedge.exe`, `NVDisplay.Container.exe`, language server processes, etc.

---

### 3.3 Process Collector (`collectors/process_collector.py`)

**Purpose:** Captures running processes with resource usage, and **flags suspicious LOLBins**.

**What are LOLBins?**
"Living off the Land Binaries" (LOLBins) are **legitimate system tools** that attackers abuse to avoid detection. Instead of dropping custom malware (which antivirus catches), attackers use tools already installed on the system:

| LOLBin | Normal use | Attacker use |
|--------|-----------|-------------|
| `powershell.exe` | System administration | Download & execute malicious scripts |
| `certutil.exe` | Certificate management | Download files from internet |
| `bitsadmin.exe` | Background file transfer | Exfiltrate data |
| `rundll32.exe` | Run DLL functions | Execute malicious DLLs |
| `wmic.exe` | System management | Reconnaissance, lateral movement |

**How we filter:** To avoid collecting hundreds of irrelevant processes, we only capture:
- Processes matching our **LOLBins list** (20 known suspicious binaries)
- Processes with **CPU > 5%** (high computation — possible crypto mining)
- Processes with **memory > 100MB** (high memory — possible data staging)

**Test result:** ✅ 54 events — captured high-memory processes like `msedge.exe` (258MB), `oracle.exe` (509MB), `MemCompression` (1030MB).

---

### 3.4 File Collector (`collectors/file_collector.py`)

**Purpose:** Monitors file system changes and classifies file sensitivity.

**Two modes of operation:**

1. **Real-time monitoring** (`start_file_monitor()`): Uses the `watchdog` library to hook into the OS filesystem notification system. When a file is created, modified, deleted, or moved, we get an immediate callback.

2. **Snapshot mode** (`collect_file_snapshot()`): Scans directories for files modified in the last hour. Useful for initial data collection.

**File sensitivity classification:**
```
HIGH (2): .pem, .key, .env, .sql, .db, .sqlite
          + any path containing "financial", "hr", "confidential", "credentials"
MEDIUM (1): .xlsx, .docx, .pdf, .csv, .json, .xml
LOW (0): everything else
```

**USB detection (Windows):**
```python
drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
return drive_type == 2  # DRIVE_REMOVABLE
```
We check the Windows drive type for each file path. Drive type 2 = removable media (USB).

**Why this matters for SOC:** File monitoring detects data exfiltration (mass file copying), especially to USB drives. The CERT r4.2 dataset (used by Team 2) specifically models scenarios where insiders copy sensitive files to USB before leaving the organization.

---

### 3.5 Browser Collector (`collectors/browser_collector.py`)

**Purpose:** Extracts browsing history from Chrome and Edge.

**How it works:**
1. Locates the browser's SQLite `History` database at its default path:
   - Chrome: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\History`
   - Edge: `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History`
2. **Copies the database to a temp file** before reading (because the browser holds a lock on it)
3. Queries the `urls` table for recent entries

**Chrome timestamp conversion:**
Chrome stores timestamps as **microseconds since January 1, 1601** (Windows epoch). To convert to Unix timestamp:
```python
chrome_epoch_offset = 11644473600  # seconds between 1601 and 1970
unix_ts = (chrome_timestamp / 1_000_000) - chrome_epoch_offset
```

**Suspicious domain detection:**
We maintain a list of threat-indicative domains grouped by category:
- **File sharing / exfiltration:** mega.nz, mediafire.com, transfer.sh
- **Anonymization:** torproject.org, tails.boum.org
- **Data dumps:** pastebin.com, ghostbin.com
- **Hacking tools:** exploit-db.com, 0day.today
- **Job search (insider threat indicator):** indeed.com, glassdoor.com

The CERT insider threat dataset specifically models scenarios where employees browse job search sites before stealing data — that's why we flag them.

**Test result:** ✅ Captured Edge browsing history (Google account logins, various pages).

---

## 4. Enrichment Layer (`data/enrichment/user_device_map.json`)

A static JSON mapping that provides **context** about users and devices. When events are processed, we can look up:

- **User context:** department, role, privilege level (high/medium/low)
- **Device context:** type (workstation/laptop/server), OS, criticality (critical/high/medium/low)

This is necessary because raw log data only contains usernames and hostnames — the enrichment layer adds the **organizational context** that Team 3's Risk Agent needs for impact scoring.

---

## 5. Visualization Dashboard (`dashboard.py`)

A Flask web application for testing and demonstrating the collectors.

**Features:**
- 6 buttons: System, Network, Process, File, Browser, Collect All
- Real-time data display in a sortable table
- Color-coded category badges (cyan=system, green=network, orange=process, red=file, purple=web)
- Smart detail column that formats metadata differently per event type
- Dark theme with modern glassmorphism design

**Architecture:**
```
Browser → GET /api/collect/<type> → Flask route → calls collector function → 
   returns JSON → JavaScript renders table
```

Each button triggers a `fetch()` call to the API, the server runs the appropriate collector, serializes the `StandardEvent` objects to JSON via Pydantic's `.model_dump()`, and the frontend renders them.

---

## 6. Project Structure Summary

```
cybersec_project/
├── pyproject.toml                  # All project dependencies
├── .env.example                    # API key template (for Phases 2-3)
├── dashboard.py                    # Flask visualization dashboard
├── pdf_reader.py                   # Utility to read project PDFs
│
├── collectors/                     # ⭐ Phase 1 — Data collection
│   ├── event_schema.py             #   Core data contract (Pydantic models)
│   ├── system_collector.py         #   Login/idle (psutil + Windows ctypes)
│   ├── network_collector.py        #   TCP/UDP connections (psutil)
│   ├── process_collector.py        #   Processes + LOLBins (psutil)
│   ├── file_collector.py           #   File monitoring (watchdog + ctypes)
│   └── browser_collector.py        #   Chrome/Edge history (sqlite3)
│
├── data/enrichment/
│   └── user_device_map.json        #   User/device context mapping
│
├── agents/                         # Phase 3 (TODO)
├── mcp_servers/                    # Phase 2 (TODO)
├── mailbox/                        # Inter-agent communication
├── logs/                           # Agent trace logs
├── webapp/                         # Phase 6 — Django (TODO)
└── tests/                          # Test suite
```

---

## 7. Test Results Summary

| Collector | Events | Key observations |
|-----------|--------|-----------------|
| System | 1 | Correctly identified user `Ranim`, device `DESKTOP-V1QS329`, idle time, session duration |
| Network | 69 | Captured TCP connections from Edge, Antigravity, NVDisplay, language servers |
| Process | 54 | Detected high-memory processes: msedge (258MB), oracle (509MB), MemCompression (1GB) |
| File | ✅ | Built and verified — two modes: real-time watchdog + snapshot scan |
| Browser | ✅ | Captured Edge browsing history with timestamps, URLs, domains, visit counts |

**All events conform to the StandardEvent schema** — validated at creation time by Pydantic.

---

## 8. How This Connects to the Next Phases

```
Phase 1 (DONE)          Phase 2 (NEXT)           Phase 3              Phase 4+
─────────────        ─────────────────        ──────────────        ────────────
Collectors    ──→    MCP Tool Servers   ──→   AI Agents       ──→  Integration
event_schema         log_reader_server        Data Agent            Testing
system_collector     web_scraper_server       Adversarial Agent     Django UI
network_collector    python_executor          Orchestrator
process_collector    attack_injector
file_collector       sequential_thinking
browser_collector
```

**Phase 2** will wrap our collectors in MCP (Model Context Protocol) servers so the AI agents can discover and use them as tools. The agents will then autonomously decide which collectors to run, process the data, and inject attack simulations — making the system truly **agentic**.
