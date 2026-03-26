# Design Document: MCP Tool Servers

## Overview

This design document specifies the technical architecture for Phase 2 of the Cyber-Data Genesis project: MCP (Model Context Protocol) Tool Servers. The system consists of 5 MCP servers that expose data collection, storage, attack simulation, enrichment, and code execution capabilities to Google Agent Developer Kit (ADK) AI agents via the Model Context Protocol.

### System Context

Phase 2 builds upon the completed Phase 1 data collection layer (11 collectors with 100% CERT r4.2 coverage) by wrapping collectors and related functionality in MCP servers. These servers enable autonomous AI agents in Phase 3 to:

- Execute data collectors on-demand to gather fresh system data
- Store and query collected events persistently
- Inject realistic attack simulations based on MITRE ATT&CK techniques
- Enrich events with user/device context for risk scoring
- Execute Python code safely in a sandboxed environment

### Design Goals

1. **ADK Compatibility**: Use official MCP Python SDK with stdio transport for seamless Google ADK integration
2. **Tool Discoverability**: Expose all capabilities as well-defined tools with JSON Schema definitions
3. **Data Integrity**: Maintain StandardEvent schema consistency across all server boundaries
4. **Security**: Execute untrusted code safely with sandboxing and input validation
5. **Performance**: Handle reasonable data volumes with sub-second response times for most operations
6. **Resilience**: Graceful error handling with structured error responses

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google ADK Agent Layer                        │
│  (Data Engineering Agent, Adversarial Agent - Phase 3)          │
└────────────────────────┬────────────────────────────────────────┘
                         │ JSON-RPC over stdio
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                    MCP Server Layer (Phase 2)                    │
├──────────────┬──────────────┬──────────────┬──────────────┬─────┤
│  Collector   │   Event      │   Attack     │  Enrichment  │Python│
│  Executor    │   Storage    │   Injector   │              │Exec  │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┴─────┘
       │              │              │              │
┌──────┴──────────────┴──────────────┴──────────────┴─────────────┐
│                  Phase 1 Data Collection Layer                   │
│  (11 collectors: system, file, network, process, browser,        │
│   email, windows_event, usb_device, clipboard, registry, dns)    │
└──────────────────────────────────────────────────────────────────┘
```

### Communication Protocol

All MCP servers communicate with ADK agents using:
- **Protocol**: JSON-RPC 2.0
- **Transport**: stdio (standard input/output)
- **Message Format**: JSON-serialized tool invocations and responses
- **Discovery**: Tools registered with JSON Schema definitions for ADK introspection

### Data Flow

```
Agent → MCP Server → Tool Execution → Response → Agent
  │                                                  │
  └──────────────── JSON-RPC ──────────────────────┘

Example Flow (Data Collection):
1. Agent invokes "collect_system_events" tool via JSON-RPC
2. Collector-Executor MCP executes system_collector.py
3. Collector returns StandardEvent objects
4. MCP server serializes to JSON dictionaries
5. Response sent back to agent via stdio
```

### File System Layout

```
mcp_servers/
├── __init__.py
├── collector_executor/
│   ├── __init__.py
│   ├── server.py              # Main MCP server implementation
│   ├── tool_definitions.py    # JSON Schema tool definitions
│   └── README.md              # Usage documentation
├── event_storage/
│   ├── __init__.py
│   ├── server.py
│   ├── storage_engine.py      # JSON Lines storage implementation
│   ├── query_engine.py        # Event filtering and pagination
│   └── README.md
├── attack_injector/
│   ├── __init__.py
│   ├── server.py
│   ├── attack_patterns.py     # MITRE ATT&CK pattern generators
│   └── README.md
├── enrichment/
│   ├── __init__.py
│   ├── server.py
│   ├── enrichment_engine.py   # User/device context lookup
│   ├── correlation_engine.py  # Event correlation logic
│   └── README.md
└── python_executor/
    ├── __init__.py
    ├── server.py
    ├── sandbox_config.py      # Daytona sandbox configuration
    └── README.md
```

## Components and Interfaces

### 1. Collector-Executor MCP Server

**Purpose**: Execute Phase 1 data collectors on-demand and return StandardEvent objects.

**Exposed Tools**:

1. `collect_system_events` - Execute system_collector.py
2. `collect_file_events` - Execute file_collector.py
3. `collect_network_events` - Execute network_collector.py
4. `collect_process_events` - Execute process_collector.py
5. `collect_browser_events` - Execute browser_collector.py (with hours_back parameter)
6. `collect_email_events` - Execute email_collector.py (with hours_back parameter)
7. `collect_windows_events` - Execute windows_event_collector.py (with hours_back parameter)
8. `collect_usb_events` - Execute usb_device_collector.py
9. `collect_clipboard_events` - Execute clipboard_collector.py
10. `collect_registry_events` - Execute registry_collector.py
11. `collect_dns_events` - Execute dns_collector.py (with hours_back parameter)

**Tool Schema Example** (collect_email_events):

```json
{
  "name": "collect_email_events",
  "description": "Collect email metadata from Outlook (sent/received emails, external recipients, attachments)",
  "parameters": {
    "type": "object",
    "properties": {
      "hours_back": {
        "type": "integer",
        "description": "Number of hours to look back for emails",
        "default": 24,
        "minimum": 1,
        "maximum": 720
      }
    }
  },
  "returns": {
    "type": "object",
    "properties": {
      "events": {
        "type": "array",
        "items": { "$ref": "#/definitions/StandardEvent" }
      },
      "count": { "type": "integer" },
      "collector": { "type": "string" },
      "execution_time_ms": { "type": "number" }
    }
  }
}
```

**Return Format**:

```json
{
  "events": [
    {
      "event_id": "uuid",
      "timestamp": "2024-01-15T10:30:00",
      "user_id": "U001",
      "device_id": "WORKSTATION-01",
      "event_type": "email_sent",
      "event_category": "email",
      "action": "send",
      "resource": "email_to_3_recipients",
      "metadata": {
        "recipient_count": 3,
        "external_recipient_count": 1,
        "attachment_count": 2,
        "attachment_size_bytes": 5242880
      },
      "source": "outlook"
    }
  ],
  "count": 1,
  "collector": "email_collector",
  "execution_time_ms": 1250
}
```

**Error Response Format**:

```json
{
  "error": {
    "type": "timeout_error",
    "message": "Collector execution exceeded 30 second timeout",
    "details": {
      "collector": "email_collector",
      "elapsed_time_ms": 30500
    }
  },
  "partial_results": {
    "events": [],
    "count": 0
  }
}
```

**Implementation Details**:

- Use `subprocess.run()` with timeout to execute collector modules
- Capture stdout and parse JSON output from collectors
- Validate returned events against StandardEvent schema using Pydantic
- Log all invocations to `logs/collector_executor.log`
- Maintain execution timeout of 30 seconds per collector
- Return partial results if collector fails mid-execution

### 2. Event-Storage MCP Server

**Purpose**: Persist StandardEvent objects to disk and provide query capabilities.

**Exposed Tools**:

1. `store_events` - Persist array of StandardEvent dictionaries
2. `query_events` - Filter and retrieve events by criteria
3. `get_summary` - Return statistics about stored events
4. `export_to_mailbox` - Write filtered events to mailbox/clean_events.json

**Tool Schema Example** (query_events):

```json
{
  "name": "query_events",
  "description": "Query stored events with filters and pagination",
  "parameters": {
    "type": "object",
    "properties": {
      "event_type": {
        "type": "string",
        "enum": ["logon", "logoff", "file_access", "device_connect", "device_disconnect", 
                 "process_start", "process_stop", "network_connection", "http_request",
                 "email_sent", "email_received"]
      },
      "event_category": {
        "type": "string",
        "enum": ["system", "file", "device", "process", "network", "web", "email"]
      },
      "user_id": { "type": "string" },
      "device_id": { "type": "string" },
      "start_time": { "type": "string", "format": "date-time" },
      "end_time": { "type": "string", "format": "date-time" },
      "page_size": { "type": "integer", "default": 100, "maximum": 1000 },
      "page": { "type": "integer", "default": 1, "minimum": 1 }
    }
  },
  "returns": {
    "type": "object",
    "properties": {
      "events": { "type": "array", "items": { "$ref": "#/definitions/StandardEvent" } },
      "count": { "type": "integer" },
      "total_matches": { "type": "integer" },
      "page": { "type": "integer" },
      "page_size": { "type": "integer" },
      "has_more": { "type": "boolean" }
    }
  }
}
```

**Storage Format**:

Events are stored in JSON Lines format (one event per line) organized by date:

```
logs/
├── events_2024-01-15.jsonl
├── events_2024-01-16.jsonl
└── events_2024-01-17.jsonl
```

Each line in a `.jsonl` file is a complete StandardEvent JSON object:

```jsonl
{"event_id":"uuid1","timestamp":"2024-01-15T10:00:00","user_id":"U001",...}
{"event_id":"uuid2","timestamp":"2024-01-15T10:05:00","user_id":"U002",...}
```

**Query Implementation**:

- Parse ISO 8601 timestamps for time range filtering
- Use generator pattern to stream events from disk (memory efficient)
- Apply filters in sequence: time range → event_type → event_category → user_id → device_id
- Implement pagination by skipping to offset and limiting results
- Return empty array with message if no matches found

**Export Format** (mailbox/clean_events.json):

```json
{
  "metadata": {
    "export_timestamp": "2024-01-15T12:00:00",
    "event_count": 1500,
    "time_range": {
      "start": "2024-01-15T00:00:00",
      "end": "2024-01-15T23:59:59"
    },
    "data_source": "event_storage_mcp",
    "schema_version": "1.0"
  },
  "events": [
    { "event_id": "...", "timestamp": "...", ... }
  ]
}
```

**Implementation Details**:

- Use `json.dumps()` without indentation for `.jsonl` files (one line per event)
- Use `json.dumps(indent=2)` for mailbox exports (human-readable)
- Validate all events against StandardEvent schema before storage
- Create `logs/` and `mailbox/` directories if they don't exist
- Handle concurrent reads with file locking (use `fcntl` on Unix, `msvcrt` on Windows)
- Log storage operations to `logs/event_storage.log`

### 3. Attack-Injector MCP Server

**Purpose**: Generate realistic attack simulations based on MITRE ATT&CK techniques.

**Exposed Tools**:

1. `inject_attack` - Generate synthetic attack event sequence
2. `list_attack_types` - Return available attack types with descriptions

**Supported Attack Types**:

| Attack Type | MITRE Technique | Event Sequence |
|-------------|-----------------|----------------|
| data_exfiltration_usb | T1052 (Exfiltration Over Physical Medium) | file_discovery → file_access (sensitive) → device_connect → file_access (is_usb=True) |
| data_exfiltration_email | T1114 (Email Collection) | file_discovery → file_access (sensitive) → email_sent (external, large attachment) |
| credential_theft | T1555 (Credentials from Password Stores) | file_access (browser profile) → file_access (.env, .key files) → network_connection (external) |
| file_discovery | T1083 (File and Directory Discovery) | file_access (multiple directories) → file_access (sensitive paths) |

**Tool Schema Example** (inject_attack):

```json
{
  "name": "inject_attack",
  "description": "Generate realistic attack simulation events",
  "parameters": {
    "type": "object",
    "properties": {
      "attack_type": {
        "type": "string",
        "enum": ["data_exfiltration_usb", "data_exfiltration_email", 
                 "credential_theft", "file_discovery"]
      },
      "mitre_technique": {
        "type": "string",
        "description": "MITRE ATT&CK technique ID (e.g., T1052)"
      },
      "user_id": {
        "type": "string",
        "description": "User to simulate attack for (optional, random if not provided)"
      },
      "device_id": {
        "type": "string",
        "description": "Device to simulate attack on (optional, random if not provided)"
      }
    },
    "required": ["attack_type"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "events": { "type": "array", "items": { "$ref": "#/definitions/StandardEvent" } },
      "count": { "type": "integer" },
      "attack_type": { "type": "string" },
      "mitre_technique": { "type": "string" },
      "description": { "type": "string" }
    }
  }
}
```

**Attack Pattern Generation**:

Each attack type generates a realistic temporal sequence:

**Example: data_exfiltration_usb**

```python
def generate_usb_exfiltration(user_id: str, device_id: str) -> list[StandardEvent]:
    events = []
    base_time = datetime.now()
    
    # 1. File discovery (T1083) - 5-10 minutes before exfiltration
    events.append(create_event(
        event_type="file_access",
        event_category="file",
        action="read",
        resource="C:\\Users\\user\\Documents\\Financial_Reports",
        timestamp=(base_time - timedelta(minutes=random.randint(5, 10))).isoformat(),
        user_id=user_id,
        device_id=device_id,
        source="attack_simulation",
        sensitivity_level=2,
        is_simulated=True,
        attack_type="data_exfiltration_usb",
        mitre_technique="T1052"
    ))
    
    # 2. USB device connection
    events.append(create_event(
        event_type="device_connect",
        event_category="device",
        action="connect",
        resource="USB_DEVICE_VID_0781_PID_5567",
        timestamp=(base_time - timedelta(minutes=2)).isoformat(),
        user_id=user_id,
        device_id=device_id,
        source="attack_simulation",
        device_type="usb_storage",
        is_simulated=True,
        attack_type="data_exfiltration_usb",
        mitre_technique="T1052"
    ))
    
    # 3. File copy to USB (large file)
    events.append(create_event(
        event_type="file_access",
        event_category="file",
        action="write",
        resource="E:\\Financial_Reports_2024.xlsx",
        timestamp=base_time.isoformat(),
        user_id=user_id,
        device_id=device_id,
        source="attack_simulation",
        file_size_bytes=15728640,  # 15 MB
        is_usb=True,
        sensitivity_level=2,
        is_simulated=True,
        attack_type="data_exfiltration_usb",
        mitre_technique="T1052"
    ))
    
    return events
```

**User/Device Selection**:

- Load realistic user/device mappings from `data/enrichment/user_device_map.json`
- If user_id/device_id not provided, randomly select from mapping
- Ensure selected user has appropriate privilege level for attack type

**Implementation Details**:

- Generate timestamps with realistic temporal patterns (5-30 minute windows)
- Mark all events with `is_simulated=True`, `attack_type`, and `mitre_technique`
- Return events compatible with Event-Storage MCP (StandardEvent dictionaries)
- Log all attack injections to `logs/attack_injector.log`

### 4. Enrichment MCP Server

**Purpose**: Add user/device context and correlate related events.

**Exposed Tools**:

1. `enrich_events` - Add department, privilege_level, asset_criticality
2. `correlate_events` - Identify related events and add correlation_id
3. `add_user_device_mapping` - Add new user/device entries to mapping file

**Tool Schema Example** (enrich_events):

```json
{
  "name": "enrich_events",
  "description": "Enrich events with user and device context",
  "parameters": {
    "type": "object",
    "properties": {
      "events": {
        "type": "array",
        "items": { "$ref": "#/definitions/StandardEvent" }
      }
    },
    "required": ["events"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "enriched_events": { "type": "array", "items": { "$ref": "#/definitions/StandardEvent" } },
      "count": { "type": "integer" },
      "enrichment_stats": {
        "type": "object",
        "properties": {
          "users_found": { "type": "integer" },
          "users_unknown": { "type": "integer" },
          "devices_found": { "type": "integer" },
          "devices_unknown": { "type": "integer" }
        }
      }
    }
  }
}
```

**Enrichment Process**:

1. Load user/device mappings from `data/enrichment/user_device_map.json` at startup
2. For each event, lookup user_id and device_id in mappings
3. Add enrichment fields to metadata:
   - `department` (from user mapping)
   - `privilege_level` (from user mapping: "low", "medium", "high")
   - `asset_criticality` (from device mapping: "low", "high", "critical")
4. If user_id or device_id not found, set values to "unknown"
5. Preserve all original event fields

**Enriched Event Example**:

```json
{
  "event_id": "uuid",
  "timestamp": "2024-01-15T10:30:00",
  "user_id": "U001",
  "device_id": "WORKSTATION-01",
  "event_type": "file_access",
  "event_category": "file",
  "action": "read",
  "resource": "C:\\Financial\\Q4_Report.xlsx",
  "metadata": {
    "file_path": "C:\\Financial\\Q4_Report.xlsx",
    "sensitivity_level": 2,
    "department": "IT",
    "privilege_level": "high",
    "asset_criticality": "high"
  },
  "source": "file_collector"
}
```

**Correlation Process**:

1. Sort events by timestamp
2. Group events by (user_id, device_id) within time_window_minutes
3. Assign unique correlation_id (UUID) to each group
4. Add correlation_id to metadata for all events in group

**Tool Schema Example** (correlate_events):

```json
{
  "name": "correlate_events",
  "description": "Identify related events and add correlation IDs",
  "parameters": {
    "type": "object",
    "properties": {
      "events": {
        "type": "array",
        "items": { "$ref": "#/definitions/StandardEvent" }
      },
      "time_window_minutes": {
        "type": "integer",
        "default": 10,
        "minimum": 1,
        "maximum": 60
      }
    },
    "required": ["events"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "correlated_events": { "type": "array", "items": { "$ref": "#/definitions/StandardEvent" } },
      "correlation_groups": { "type": "integer" }
    }
  }
}
```

**Implementation Details**:

- Cache user_device_map.json in memory at startup
- Reload mapping file if modified (check mtime)
- Validate enriched events still conform to StandardEvent schema
- Log enrichment operations to `logs/enrichment.log`
- Handle missing mapping file gracefully (return events without enrichment + warning)

### 5. Python-Executor MCP Server

**Purpose**: Execute Python code safely in a sandboxed environment.

**Exposed Tools**:

1. `execute_code` - Run Python code in Daytona sandbox
2. `list_allowed_imports` - Return whitelist of permitted modules

**Tool Schema Example** (execute_code):

```json
{
  "name": "execute_code",
  "description": "Execute Python code in a sandboxed environment",
  "parameters": {
    "type": "object",
    "properties": {
      "code": {
        "type": "string",
        "description": "Python code to execute"
      },
      "timeout_seconds": {
        "type": "integer",
        "default": 10,
        "minimum": 1,
        "maximum": 30
      }
    },
    "required": ["code"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "stdout": { "type": "string" },
      "stderr": { "type": "string" },
      "return_value": { "type": "string" },
      "execution_time_ms": { "type": "number" },
      "success": { "type": "boolean" }
    }
  }
}
```

**Allowed Imports Whitelist**:

```python
ALLOWED_IMPORTS = {
    "json", "datetime", "re", "math", "statistics",
    "collections", "itertools", "functools", "typing",
    "decimal", "fractions", "random", "string"
}
```

**Sandbox Configuration**:

```python
SANDBOX_CONFIG = {
    "timeout_seconds": 10,
    "memory_limit_mb": 100,
    "file_system_access": {
        "read": ["/tmp"],
        "write": ["/tmp"],
        "deny": ["*"]  # Deny all other paths
    },
    "network_access": False,
    "allowed_imports": ALLOWED_IMPORTS,
    "blocked_builtins": ["open", "eval", "exec", "compile", "__import__"]
}
```

**Code Sanitization**:

Before execution, scan code for dangerous patterns:

```python
DANGEROUS_PATTERNS = [
    r"__import__",
    r"eval\s*\(",
    r"exec\s*\(",
    r"compile\s*\(",
    r"os\.",
    r"subprocess\.",
    r"sys\.",
    r"socket\.",
    r"requests\.",
    r"urllib\."
]

def sanitize_code(code: str) -> tuple[bool, str]:
    """Returns (is_safe, error_message)"""
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            return False, f"Blocked dangerous pattern: {pattern}"
    return True, ""
```

**Execution Flow**:

1. Validate code is not empty
2. Sanitize code for dangerous patterns
3. Check imports against whitelist
4. Execute in Daytona sandbox with timeout
5. Capture stdout, stderr, return value
6. Return results or error response

**Error Response Example**:

```json
{
  "error": {
    "type": "validation_error",
    "message": "Blocked dangerous pattern: __import__",
    "details": {
      "code_hash": "sha256_hash"
    }
  },
  "stdout": "",
  "stderr": "",
  "execution_time_ms": 0,
  "success": false
}
```

**Implementation Details**:

- Use Daytona SDK for sandbox execution
- Log all code execution attempts to `logs/python_executor.log` with code hash
- Enforce 10-second timeout (configurable up to 30 seconds)
- Capture and return both stdout and stderr
- Hash code for audit trail (SHA-256)

## Data Models

### StandardEvent Schema

The core data model is defined in `collectors/event_schema.py`. All MCP servers must maintain compatibility with this schema.

**Core Fields** (required):

```python
class StandardEvent(BaseModel):
    event_id: str                    # UUID
    timestamp: str                   # ISO 8601 format
    user_id: str                     # User identifier
    device_id: str                   # Device/hostname identifier
    event_type: Literal[...]         # Specific event type
    event_category: Literal[...]     # High-level category
    action: str                      # Specific action
    resource: str                    # Target resource
    metadata: EventMetadata          # Flexible metadata
    source: str                      # Collection source
```

**Metadata Fields** (optional, varies by event type):

```python
class EventMetadata(BaseModel):
    # System events
    idle_time_seconds: Optional[float]
    session_duration_minutes: Optional[float]
    
    # File events
    file_path: Optional[str]
    file_extension: Optional[str]
    file_size_bytes: Optional[int]
    is_usb: Optional[bool]
    sensitivity_level: Optional[int]  # 0=low, 1=medium, 2=high
    
    # Network events
    src_ip: Optional[str]
    dst_ip: Optional[str]
    protocol: Optional[str]
    bytes_sent: Optional[int]
    bytes_received: Optional[int]
    
    # Email events
    recipient_count: Optional[int]
    external_recipient_count: Optional[int]
    attachment_count: Optional[int]
    attachment_size_bytes: Optional[int]
    
    # Attack simulation fields
    is_simulated: Optional[bool] = False
    attack_type: Optional[str]
    mitre_technique: Optional[str]
    
    # Enrichment fields (added by Enrichment MCP)
    department: Optional[str]
    privilege_level: Optional[str]
    asset_criticality: Optional[str]
    correlation_id: Optional[str]
```

### User-Device Mapping Schema

Stored in `data/enrichment/user_device_map.json`:

```json
{
  "users": {
    "U001": {
      "username": "admin_user",
      "department": "IT",
      "role": "System Administrator",
      "privilege_level": "high",
      "devices": ["WORKSTATION-01", "SERVER-DC01"]
    }
  },
  "devices": {
    "WORKSTATION-01": {
      "type": "workstation",
      "os": "Windows 11",
      "criticality": "high"
    }
  }
}
```

### MCP Configuration Schema

Stored in `mcp_config.json` (root directory):

```json
{
  "mcpServers": {
    "collector-executor": {
      "command": "python",
      "args": ["-m", "mcp_servers.collector_executor.server"],
      "transport": "stdio"
    },
    "event-storage": {
      "command": "python",
      "args": ["-m", "mcp_servers.event_storage.server"],
      "transport": "stdio"
    },
    "attack-injector": {
      "command": "python",
      "args": ["-m", "mcp_servers.attack_injector.server"],
      "transport": "stdio"
    },
    "enrichment": {
      "command": "python",
      "args": ["-m", "mcp_servers.enrichment.server"],
      "transport": "stdio"
    },
    "python-executor": {
      "command": "python",
      "args": ["-m", "mcp_servers.python_executor.server"],
      "transport": "stdio"
    }
  }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies and consolidations:

**Redundancies Eliminated:**
- Requirements 1.2 and 1.9 both test collector invocation behavior - consolidated into Property 1
- Requirements 2.1 and 2.5 both test storage round-trip - consolidated into Property 5
- Requirements 3.5, 3.9, 3.11, 3.12 all test attack event generation - consolidated into Properties 8 and 9
- Requirements 4.3 and 4.11 both test enrichment behavior - consolidated into Property 11
- Requirements 5.6 and 5.10 both test output capture - consolidated into Property 15
- Requirements 13.3, 13.4, 13.6, 13.7, 13.10 all test serialization - consolidated into Property 18

**Properties Combined:**
- Time-based filtering (2.6) and query filtering (2.3) combined into Property 6
- Attack sequence generation (3.4) and temporal patterns (3.6) combined into Property 9
- Enrichment field addition (4.3) and field preservation (4.11) combined into Property 11

### Property 1: Collector Invocation Returns Valid Events

*For any* collector tool invocation with valid parameters, the response SHALL contain an array of events where each event conforms to the StandardEvent schema.

**Validates: Requirements 1.2, 1.9**

### Property 2: Time-Range Parameter Acceptance

*For any* collector that supports time-range parameters (email, browser, windows_event, dns), invoking the tool with an hours_back parameter (1-720) SHALL execute successfully and return events within that time range.

**Validates: Requirements 1.3**

### Property 3: Collector Failure Returns Structured Error

*For any* collector execution that fails, the response SHALL contain an error object with type, message, and details fields, plus a partial_results object.

**Validates: Requirements 1.4**

### Property 4: Invalid Parameters Rejected Before Execution

*For any* tool invocation with parameters that violate the JSON Schema definition, the MCP server SHALL reject the request with a validation_error before executing the tool logic.

**Validates: Requirements 1.5, 2.7**

### Property 5: Event Storage Round-Trip Preservation

*For any* array of valid StandardEvent objects, storing them via store_events and then querying them back SHALL return events that are equivalent to the original events (all fields preserved).

**Validates: Requirements 2.1, 2.5, 13.3**

### Property 6: Query Filtering Returns Only Matching Events

*For any* query_events invocation with filter parameters (event_type, event_category, user_id, device_id, start_time, end_time), all returned events SHALL match ALL specified filter criteria, and the time range filtering SHALL be inclusive.

**Validates: Requirements 2.3, 2.6**

### Property 7: Summary Statistics Accuracy

*For any* set of stored events, the get_summary tool SHALL return statistics (total count, counts by type/category, unique users/devices) that accurately reflect the stored data.

**Validates: Requirements 2.4**

### Property 8: Attack Events Marked with Simulation Metadata

*For any* attack injection (any attack_type), all generated events SHALL have metadata fields is_simulated=True, attack_type matching the requested type, and mitre_technique matching the correct MITRE ATT&CK technique for that attack type.

**Validates: Requirements 3.3, 3.5, 3.9**

### Property 9: Attack Sequences Follow Realistic Patterns

*For any* attack injection, the generated event sequence SHALL follow the expected behavioral pattern for that attack type (correct event order, realistic timestamps within 5-30 minute windows, appropriate metadata for each event).

**Validates: Requirements 3.4, 3.6, 3.11, 3.12**

### Property 10: Attack Events Use Valid User/Device IDs

*For any* attack injection without explicit user_id/device_id parameters, the generated events SHALL use user_id and device_id values that exist in data/enrichment/user_device_map.json.

**Validates: Requirements 3.7**

### Property 11: Enrichment Adds Context Without Modifying Original Fields

*For any* array of StandardEvent objects passed to enrich_events, the returned enriched events SHALL contain all original fields with unchanged values, plus additional metadata fields (department, privilege_level, asset_criticality) populated from the user/device mapping.

**Validates: Requirements 4.1, 4.3, 4.11**

### Property 12: Event Correlation Groups Related Events

*For any* array of events passed to correlate_events with a time_window_minutes parameter, events with the same (user_id, device_id) and timestamps within the time window SHALL receive the same correlation_id (valid UUID format), and events outside the window SHALL receive different correlation_ids.

**Validates: Requirements 4.4, 4.6, 4.10**

### Property 13: Enriched Events Maintain Schema Compliance

*For any* array of events enriched by enrich_events, all returned events SHALL validate successfully against the StandardEvent schema.

**Validates: Requirements 4.8**

### Property 14: Sandbox Blocks Restricted Operations

*For any* Python code that attempts restricted operations (file system access outside /tmp, network access, importing non-whitelisted modules), the execute_code tool SHALL reject the code with a validation_error or return an execution error.

**Validates: Requirements 5.2, 5.3, 5.8, 5.11**

### Property 15: Code Execution Captures Output

*For any* valid Python code executed successfully, the response SHALL contain stdout (all print output), stderr (all error output), return_value (final expression value), and execution_time_ms (elapsed time).

**Validates: Requirements 5.6, 5.10**

### Property 16: Code Execution Exceptions Return Structured Errors

*For any* Python code that raises an exception during execution, the response SHALL contain an error object with type (exception class name), message (exception message), and details (traceback).

**Validates: Requirements 5.5**

### Property 17: Code Execution Logging

*For any* code execution attempt (successful or failed), a log entry SHALL be created in logs/python_executor.log containing timestamp, code hash (SHA-256), execution status, and execution time.

**Validates: Requirements 5.12**

### Property 18: Serialization Round-Trip Preserves All Fields

*For any* valid StandardEvent object, the operation serialize(event) → parse(json) → deserialize(event') SHALL produce an event' that is equivalent to the original event, with all fields (including optional metadata fields with None values) preserved, and all datetime objects converted to ISO 8601 strings.

**Validates: Requirements 13.3, 13.4, 13.6, 13.7, 13.10**

### Property 19: Pagination Returns Correct Subsets

*For any* query with pagination parameters (page_size, page), the returned events SHALL be a subset of the total matching events, starting at offset (page-1)*page_size and containing at most page_size events, with has_more=true if more pages exist.

**Validates: Requirements 2.8**

### Property 20: Concurrent Reads Maintain Data Integrity

*For any* set of concurrent query_events invocations on the same event storage, all queries SHALL return consistent results with no data corruption or missing events.

**Validates: Requirements 2.11**

### Property 21: Collector Execution Isolation

*For any* sequence of collector tool invocations, state from one invocation (variables, file handles, cached data) SHALL NOT affect subsequent invocations.

**Validates: Requirements 1.8**

### Property 22: Timeout Enforcement

*For any* collector execution that exceeds 30 seconds, the Collector-Executor MCP SHALL terminate the execution and return a timeout_error with the elapsed time.

**Validates: Requirements 1.10**

## Error Handling

### Error Response Structure

All MCP servers follow a consistent error response format:

```json
{
  "error": {
    "type": "error_category",
    "message": "Human-readable description",
    "details": {
      "additional_context": "value"
    }
  }
}
```

### Error Types

| Error Type | Description | Example Scenario |
|------------|-------------|------------------|
| validation_error | Invalid parameters or schema violations | Missing required field, out-of-range value |
| dependency_error | Missing dependencies or resources | Collector module not found, mapping file missing |
| timeout_error | Operation exceeded time limit | Collector execution > 30s, code execution > 10s |
| internal_error | Unexpected exception | Unhandled Python exception, file system error |
| permission_error | Insufficient permissions | Cannot read Windows Event Log without admin |

### Error Handling Strategies

**Collector-Executor MCP**:
- Timeout: Terminate subprocess after 30 seconds, return timeout_error with partial results
- Module not found: Return dependency_error with module name
- Permission denied: Return partial results with warning field

**Event-Storage MCP**:
- Invalid event schema: Reject event, return validation_error with field details
- Corrupted file: Skip file, log warning, continue with other files
- Disk full: Return internal_error with disk space details

**Attack-Injector MCP**:
- Invalid attack_type: Return validation_error with list of valid types
- Missing user_device_map.json: Return dependency_error with file path

**Enrichment MCP**:
- Missing mapping file: Return events without enrichment + warning
- Unknown user_id/device_id: Add "unknown" values, continue processing

**Python-Executor MCP**:
- Dangerous code pattern: Return validation_error before execution
- Import blocked module: Return validation_error with module name
- Execution timeout: Terminate sandbox, return timeout_error
- Runtime exception: Return error with exception type, message, traceback

### Retry Logic

For transient failures (file locks, temporary network issues), MCP servers implement exponential backoff:

```python
def retry_with_backoff(func, max_retries=3):
    delays = [1, 2, 4]  # seconds
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt < max_retries - 1:
                time.sleep(delays[attempt])
            else:
                raise
```

Applied to:
- File system operations (Event-Storage MCP)
- User/device mapping file reads (Enrichment MCP)

## Testing Strategy

### Dual Testing Approach

The MCP Tool Servers require both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Tool registration and schema validation
- Specific attack sequences (e.g., USB exfiltration generates exactly 3 events)
- Error handling for specific failure modes
- File format validation (JSONL structure, mailbox JSON format)
- Edge cases: empty input arrays, missing files, unknown user IDs

**Property-Based Tests**: Verify universal properties across all inputs
- Collector invocations return valid StandardEvent objects (Property 1)
- Storage round-trip preserves all fields (Property 5)
- Query filtering returns only matching events (Property 6)
- Attack events always marked with simulation metadata (Property 8)
- Enrichment preserves original fields (Property 11)
- Serialization round-trip maintains equivalence (Property 18)

### Property-Based Testing Configuration

**Framework**: Use `hypothesis` for Python property-based testing

**Configuration**:
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)  # Minimum 100 iterations per property test
@given(events=st.lists(standard_event_strategy(), min_size=1, max_size=50))
def test_storage_roundtrip(events):
    """
    Feature: mcp-tool-servers, Property 5: Event Storage Round-Trip Preservation
    
    For any array of valid StandardEvent objects, storing them via store_events
    and then querying them back SHALL return events that are equivalent to the
    original events (all fields preserved).
    """
    # Store events
    storage.store_events(events)
    
    # Query all events back
    retrieved = storage.query_events()
    
    # Verify equivalence
    assert len(retrieved) == len(events)
    for original, retrieved_event in zip(events, retrieved):
        assert original.model_dump() == retrieved_event.model_dump()
```

**Test Tagging**: Each property test includes a comment referencing the design property:

```python
"""
Feature: mcp-tool-servers, Property {number}: {property_text}
"""
```

### Test Data Generators

**StandardEvent Generator**:
```python
def standard_event_strategy():
    return st.builds(
        StandardEvent,
        event_id=st.uuids().map(str),
        timestamp=st.datetimes().map(lambda dt: dt.isoformat()),
        user_id=st.sampled_from(["U001", "U002", "U003"]),
        device_id=st.sampled_from(["WORKSTATION-01", "LAPTOP-MKT-01"]),
        event_type=st.sampled_from(["logon", "file_access", "email_sent"]),
        event_category=st.sampled_from(["system", "file", "email"]),
        action=st.text(min_size=1, max_size=20),
        resource=st.text(min_size=1, max_size=100),
        source=st.text(min_size=1, max_size=20),
        metadata=event_metadata_strategy()
    )
```

### Integration Testing

**Test Agent** (tests/test_adk_agent.py):

Implements a complete workflow using all 5 MCP servers:

1. Collect events (Collector-Executor MCP)
2. Store events (Event-Storage MCP)
3. Inject attack (Attack-Injector MCP)
4. Enrich events (Enrichment MCP)
5. Query events (Event-Storage MCP)
6. Export to mailbox (Event-Storage MCP)

**Test Script** (tests/run_mcp_tests.sh):

```bash
#!/bin/bash

# Start all MCP servers in background
python -m mcp_servers.collector_executor.server &
PID1=$!
python -m mcp_servers.event_storage.server &
PID2=$!
python -m mcp_servers.attack_injector.server &
PID3=$!
python -m mcp_servers.enrichment.server &
PID4=$!
python -m mcp_servers.python_executor.server &
PID5=$!

# Wait for servers to initialize
sleep 2

# Run test agent
python tests/test_adk_agent.py

# Capture exit code
EXIT_CODE=$?

# Cleanup: kill all MCP servers
kill $PID1 $PID2 $PID3 $PID4 $PID5

# Exit with test result
exit $EXIT_CODE
```

### Test Coverage Goals

- Unit tests: 80% code coverage minimum
- Property tests: All 22 correctness properties implemented
- Integration tests: Complete workflow (collect → store → inject → enrich → export)
- Error handling: All error types tested with specific failure scenarios

### Performance Testing

Validate performance requirements from Requirement 11:

```python
def test_collector_execution_time():
    """Collector execution completes within 30 seconds"""
    start = time.time()
    result = collector_executor.collect_system_events()
    elapsed = time.time() - start
    assert elapsed < 30.0

def test_storage_performance():
    """Store 1000 events within 5 seconds"""
    events = [generate_random_event() for _ in range(1000)]
    start = time.time()
    storage.store_events(events)
    elapsed = time.time() - start
    assert elapsed < 5.0

def test_query_performance():
    """Query 10,000 events within 3 seconds"""
    # Pre-populate storage with 10,000 events
    populate_storage(10000)
    start = time.time()
    results = storage.query_events(event_type="file_access")
    elapsed = time.time() - start
    assert elapsed < 3.0
```

## Implementation Notes

### MCP SDK Usage

All servers use the official MCP Python SDK:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("server-name")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="tool_name",
            description="Tool description",
            inputSchema={
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "tool_name":
        result = execute_tool(arguments)
        return [TextContent(
            type="text",
            text=json.dumps(result)
        )]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Logging Configuration

All servers use Python's logging module with consistent format:

```python
import logging

logging.basicConfig(
    filename=f"logs/{server_name}.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(server_name)
```

### Pydantic Serialization

Convert Pydantic models to JSON-serializable dictionaries:

```python
# Serialize
event_dict = event.model_dump()

# Deserialize
event = StandardEvent.model_validate(event_dict)

# Validate
try:
    StandardEvent.model_validate(data)
except ValidationError as e:
    return {"error": {"type": "validation_error", "message": str(e)}}
```

### File System Operations

Ensure directories exist before writing:

```python
import os

def ensure_directory(path: str):
    os.makedirs(path, exist_ok=True)

# Usage
ensure_directory("logs")
ensure_directory("mailbox")
```

### Subprocess Execution

Execute collectors with timeout:

```python
import subprocess
import json

def execute_collector(collector_name: str, timeout: int = 30) -> dict:
    try:
        result = subprocess.run(
            ["python", "-m", f"collectors.{collector_name}"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        events = json.loads(result.stdout)
        return {"events": events, "count": len(events)}
    except subprocess.TimeoutExpired:
        return {"error": {"type": "timeout_error", "message": f"Execution exceeded {timeout}s"}}
    except json.JSONDecodeError as e:
        return {"error": {"type": "internal_error", "message": f"Invalid JSON output: {e}"}}
```

### Daytona Sandbox Configuration

Configure sandbox for Python execution:

```python
from daytona import Sandbox

sandbox = Sandbox(
    timeout=10,
    memory_limit_mb=100,
    allowed_imports=["json", "datetime", "re", "math", "statistics"],
    network_enabled=False,
    filesystem_access={
        "read": ["/tmp"],
        "write": ["/tmp"]
    }
)

result = sandbox.execute(code)
```

## Security Considerations

### Input Validation

All MCP servers validate inputs before processing:

1. **JSON Schema Validation**: Parameters validated against tool schema
2. **Path Traversal Prevention**: Reject paths containing `../`
3. **SQL Injection Prevention**: No SQL used (JSON file storage)
4. **Code Injection Prevention**: Sanitize Python code before execution

### Sandboxing

Python-Executor MCP uses Daytona sandbox with:
- No network access
- Restricted file system (read/write only /tmp)
- Whitelisted imports only
- 10-second timeout
- 100MB memory limit

### Logging Security Events

Log all security-relevant events:
- Code execution attempts (with code hash)
- Validation failures
- Permission errors
- Blocked operations

### Data Privacy

- Truncate sensitive fields in logs (email subjects, file paths)
- Hash code before logging (SHA-256)
- Sanitize error messages (no stack traces with sensitive data)

## Deployment

### Prerequisites

- Python 3.10+
- MCP Python SDK: `pip install mcp`
- Daytona sandbox: `pip install daytona`
- Phase 1 collectors installed and functional

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify MCP servers are executable
python -m mcp_servers.collector_executor.server --version
python -m mcp_servers.event_storage.server --version
python -m mcp_servers.attack_injector.server --version
python -m mcp_servers.enrichment.server --version
python -m mcp_servers.python_executor.server --version
```

### Configuration

Create `mcp_config.json` in project root:

```json
{
  "mcpServers": {
    "collector-executor": {
      "command": "python",
      "args": ["-m", "mcp_servers.collector_executor.server"],
      "transport": "stdio"
    },
    "event-storage": {
      "command": "python",
      "args": ["-m", "mcp_servers.event_storage.server"],
      "transport": "stdio"
    },
    "attack-injector": {
      "command": "python",
      "args": ["-m", "mcp_servers.attack_injector.server"],
      "transport": "stdio"
    },
    "enrichment": {
      "command": "python",
      "args": ["-m", "mcp_servers.enrichment.server"],
      "transport": "stdio"
    },
    "python-executor": {
      "command": "python",
      "args": ["-m", "mcp_servers.python_executor.server"],
      "transport": "stdio"
    }
  }
}
```

### Running MCP Servers

MCP servers are started automatically by ADK agents. For manual testing:

```bash
# Start individual server
python -m mcp_servers.collector_executor.server

# Server listens on stdio and waits for JSON-RPC messages
```

### Testing

```bash
# Run all tests
pytest tests/

# Run property-based tests only
pytest tests/ -k property

# Run integration tests
bash tests/run_mcp_tests.sh
```

## Future Enhancements

### Phase 3 Integration

- ADK agents will consume MCP tools for autonomous data processing
- Data Engineering Agent: collect → store → enrich → export
- Adversarial Agent: inject attacks → store → enrich → export

### Potential Extensions

1. **Additional Attack Types**: Lateral movement, privilege escalation, data destruction
2. **Real-time Event Streaming**: WebSocket transport for live event feeds
3. **Advanced Correlation**: Machine learning-based event correlation
4. **Distributed Storage**: Replace JSON files with database (PostgreSQL, MongoDB)
5. **Performance Optimization**: Caching, indexing, parallel processing

### Monitoring and Observability

- Prometheus metrics for tool invocation rates, latencies, error rates
- Grafana dashboards for MCP server health monitoring
- Distributed tracing for multi-server workflows

