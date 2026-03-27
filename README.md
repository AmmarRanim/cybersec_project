# Insider Threat Detection System

A comprehensive Windows-based insider threat detection system with realistic attack simulations from the CERT r4.2 dataset.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CERT Dataset](https://img.shields.io/badge/dataset-CERT%20r4.2-orange.svg)](https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247)

## 🎯 Overview

This system collects real Windows events and injects realistic attack simulations from CMU's CERT r4.2 dataset for testing insider threat detection algorithms. It provides a complete pipeline from data collection to attack simulation to export for behavioral analysis.

### Key Features

- **11 Windows Collectors**: System, file, network, process, browser, email, Windows events, USB, clipboard, registry, DNS
- **3 MCP Servers**: Collector-Executor, Event-Storage, Attack-Injector
- **30 CERT r4.2 Attack Patterns**: 100% research-based, covering USB exfiltration, data theft, and keylogger attacks
- **Unified Event Schema**: All events validated with Pydantic
- **JSON Lines Storage**: Efficient, scalable, date-organized
- **Clean Export**: Ready for behavioral analysis

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Insider Threat Detection System           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Phase 1: Data Collectors (11 collectors)                   │
│  ├─ system_collector                                         │
│  ├─ file_collector                                           │
│  ├─ network_collector                                        │
│  └─ ... (8 more)                                             │
│                                                              │
│  Phase 2: MCP Servers (3 servers)                           │
│  ├─ Collector-Executor MCP ──> Runs collectors              │
│  ├─ Event-Storage MCP ──────> Stores & queries events       │
│  └─ Attack-Injector MCP ────> Generates attack simulations  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Windows OS (for Windows-specific collectors)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/insider-threat-detection.git
cd insider-threat-detection

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Run Complete Workflow Test

```bash
python test_mcp_full_workflow.py
```

This will:
1. Collect real system events
2. Store events in database
3. Inject CERT attack patterns
4. Export to mailbox for analysis

### Expected Output

```
✓ Collector-Executor MCP: Working
✓ Event-Storage MCP: Working
✓ Attack-Injector MCP: Working
✓ CERT r4.2 Dataset: 30 patterns loaded
✓ Mailbox Export: Ready for Team 2

Total events: 111 (16 real + 95 simulated)
```

## 📁 Project Structure

```
insider-threat-detection/
├── collectors/              # 11 Windows data collectors
│   ├── system_collector.py
│   ├── file_collector.py
│   ├── network_collector.py
│   └── ...
├── mcp_servers/            # 3 MCP servers
│   ├── collector_executor/ # Runs collectors on-demand
│   ├── event_storage/      # Stores and queries events
│   └── attack_injector/    # Generates attack simulations
├── data/attacks/           # CERT r4.2 attack patterns
│   ├── attack_patterns.json  # 30 CERT patterns
│   └── cert_converter.py     # CERT dataset parser
├── tests/                  # Unit tests
├── logs/                   # Event storage (JSON Lines)
├── mailbox/                # Export directory
└── *.md                    # Documentation
```

## 🎓 CERT r4.2 Dataset

This system uses the **CERT Insider Threat Test Dataset r4.2** from Carnegie Mellon University.

### Attack Patterns

- **15 Scenario 1**: USB Exfiltration + Wikileaks (T1052.001, Critical)
- **10 Scenario 2**: Job Hunting + USB Theft (T1052.001, High)
- **5 Scenario 3**: Keylogger + Impersonation (T1056.001, Critical)

### Academic Credibility

- **Source**: CMU Software Engineering Institute
- **Type**: Published research dataset
- **Reproducibility**: All patterns traceable to CERT data
- **Citation**: Available from [CMU KiltHub](https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247)

## 🔧 Usage

### Collect Real Events

```python
from mcp_servers.collector_executor.server import execute_collector

# Collect system events
result = execute_collector("system_collector")
print(f"Collected {result['count']} events")
```

### Store Events

```python
from mcp_servers.event_storage.storage_engine import store_events

# Store events
result = store_events(events)
print(f"Stored {result['stored_count']} events")
```

### Inject Attack

```python
from mcp_servers.attack_injector.attack_generator import inject_attack

# Inject specific CERT attack
result = inject_attack(attack_id="cert_r42_s1_aam0658")
print(f"Generated {result['event_count']} attack events")
```

### Query Events

```python
from mcp_servers.event_storage.query_engine import query_events

# Query system events
result = query_events(event_category="system", page_size=10)
print(f"Found {result['total_matches']} events")
```

### Export to Mailbox

```python
from mcp_servers.event_storage.query_engine import export_to_mailbox

# Export all events
result = export_to_mailbox()
print(f"Exported {result['events_exported']} events")
```

## 📊 Event Schema

All events follow the `StandardEvent` schema:

```json
{
  "event_id": "uuid",
  "timestamp": "2026-03-27T16:43:37",
  "user_id": "username",
  "device_id": "hostname",
  "event_type": "logon",
  "event_category": "system",
  "action": "logon",
  "resource": "",
  "source": "psutil",
  "metadata": {
    "is_simulated": false,
    "attack_type": null,
    "mitre_technique": null
  }
}
```

## 🧪 Testing

```bash
# Run complete workflow test
python test_mcp_full_workflow.py

# Run unit tests
python -m pytest tests/ -v

# Test individual collectors
python -m collectors.system_collector
python -m collectors.file_collector
python -m collectors.network_collector
```

## 📖 Documentation

- **[COMPLETE_SYSTEM_EXPLANATION.md](COMPLETE_SYSTEM_EXPLANATION.md)** - Detailed system explanation
- **[SYSTEM_READY.md](SYSTEM_READY.md)** - System status and overview
- **[DEMO_CHEATSHEET.md](DEMO_CHEATSHEET.md)** - Quick reference for demos
- **[TEST_COMMANDS.md](TEST_COMMANDS.md)** - All available commands
- **[GIT_PUSH_GUIDE.md](GIT_PUSH_GUIDE.md)** - Git push instructions

## 🎯 Use Cases

1. **Testing Detection Algorithms**: Use simulated attacks to test insider threat detection
2. **Training ML Models**: Generate labeled dataset (real vs simulated)
3. **Security Research**: Study insider threat patterns from CERT dataset
4. **System Monitoring**: Collect real Windows events for analysis
5. **Incident Response**: Understand attack patterns and timelines

## 🔒 Security Notes

- All simulated events are marked with `is_simulated=True`
- No real attacks are performed
- Collectors require appropriate permissions (some need admin)
- CERT dataset is for research purposes only

## 📈 Performance

- **Collection**: 60-80ms per collector
- **Storage**: <100ms for batch storage
- **Query**: <50ms for filtered queries
- **Export**: <200ms for full export

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CERT Dataset**: Carnegie Mellon University Software Engineering Institute
- **MITRE ATT&CK**: MITRE Corporation for attack technique taxonomy
- **Python Community**: For excellent libraries (psutil, pydantic, watchdog)

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Built with ❤️ for insider threat detection research**
