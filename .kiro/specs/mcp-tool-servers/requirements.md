# Requirements Document: MCP Tool Servers

## Introduction

This document specifies the requirements for Phase 2 of the Cyber-Data Genesis project: MCP (Model Context Protocol) Tool Servers. Phase 2 builds upon the completed Phase 1 data collection layer (11 collectors with 100% CERT r4.2 coverage) by wrapping collectors and related functionality in MCP servers that expose tools for Google Agent Developer Kit (ADK) AI agents to consume.

The MCP Tool Servers enable autonomous AI agents to execute data collectors on-demand, store and query collected events, inject realistic attack simulations, enrich events with contextual information, and execute Python code safely in a sandboxed environment. These capabilities are essential for Phase 3, where Data Engineering and Adversarial agents will process raw logs, inject MITRE ATT&CK-based attack patterns, and produce enriched event streams for Team 2's Behavior Analysis system.

## Glossary

- **MCP_Server**: A Model Context Protocol server that exposes tools (functions) for AI agents to call via JSON-RPC over stdio
- **ADK**: Google Agent Developer Kit, the framework used to build AI agents in Phase 3
- **StandardEvent**: The unified Pydantic event schema defined in Phase 1 (collectors/event_schema.py)
- **Collector**: A Phase 1 data collection module that captures system, network, file, process, browser, email, Windows event, USB, clipboard, registry, or DNS data
- **Tool**: An MCP-exposed function that an AI agent can discover and invoke
- **Stdio_Transport**: Standard input/output communication channel used by MCP servers to communicate with ADK agents
- **JSON_RPC**: The protocol used for MCP tool invocation (request/response format)
- **MITRE_ATT&CK**: A knowledge base of adversary tactics and techniques used for attack simulation
- **Daytona_Sandbox**: A secure code execution environment for running untrusted Python code
- **Event_Storage**: A JSON file-based storage system for persisted StandardEvent objects
- **Enrichment**: The process of adding user/device context (department, privilege level, asset criticality) to events
- **Attack_Injection**: The process of generating synthetic attack events with realistic behavioral patterns
- **Mailbox**: A shared directory (mailbox/) where JSON files are written for inter-team communication
- **Tool_Schema**: JSON Schema definition that describes a tool's parameters and return type for ADK discovery

## Requirements

### Requirement 1: Collector-Executor MCP Server

**User Story:** As an AI agent, I want to execute Phase 1 data collectors on-demand, so that I can gather fresh system data when needed for analysis.

#### Acceptance Criteria

1. THE Collector_Executor_MCP SHALL expose 11 tools corresponding to the 11 Phase 1 collectors (system, network, process, file, browser, email, windows_event, usb_device, clipboard, registry, dns)
2. WHEN an agent invokes a collector tool, THE Collector_Executor_MCP SHALL execute the corresponding collector module and return StandardEvent objects as JSON-serializable dictionaries
3. WHERE a collector supports time-range parameters (email, browser, windows_event, dns), THE Collector_Executor_MCP SHALL accept an hours_back parameter (integer, default 24, range 1-720)
4. IF a collector execution fails, THEN THE Collector_Executor_MCP SHALL return a partial result with an error field describing the failure
5. THE Collector_Executor_MCP SHALL validate all tool parameters against JSON Schema before execution
6. THE Collector_Executor_MCP SHALL use stdio transport for communication with ADK agents
7. THE Collector_Executor_MCP SHALL register all tools with descriptive names, parameters, and return type schemas for ADK discovery
8. WHEN multiple collectors are invoked sequentially, THE Collector_Executor_MCP SHALL maintain independent execution contexts (no state leakage)
9. THE Collector_Executor_MCP SHALL log all tool invocations with timestamp, tool name, parameters, and execution status
10. THE Collector_Executor_MCP SHALL complete collector execution within 30 seconds or return a timeout error

### Requirement 2: Event-Storage MCP Server

**User Story:** As an AI agent, I want to store collected events persistently and query them by various criteria, so that I can analyze historical data and export results for Team 2.

#### Acceptance Criteria

1. THE Event_Storage_MCP SHALL expose a store_events tool that accepts an array of StandardEvent dictionaries and persists them to JSON files
2. THE Event_Storage_MCP SHALL organize stored events by date in the format logs/events_YYYY-MM-DD.jsonl (JSON Lines format, one event per line)
3. THE Event_Storage_MCP SHALL expose a query_events tool that accepts filter parameters (event_type, event_category, user_id, device_id, start_time, end_time) and returns matching events
4. THE Event_Storage_MCP SHALL expose a get_summary tool that returns statistics (total event count, events by type, events by category, unique users, unique devices, time range)
5. THE Event_Storage_MCP SHALL expose an export_to_mailbox tool that writes filtered events to mailbox/clean_events.json for Team 2 consumption
6. WHEN querying events with time filters, THE Event_Storage_MCP SHALL parse ISO 8601 timestamps and apply inclusive range filtering
7. WHEN storing events, THE Event_Storage_MCP SHALL validate each event against the StandardEvent schema and reject invalid events with descriptive errors
8. THE Event_Storage_MCP SHALL support pagination for query results (page_size parameter, default 100, maximum 1000)
9. IF a query returns no results, THEN THE Event_Storage_MCP SHALL return an empty array with a message field indicating no matches found
10. THE Event_Storage_MCP SHALL use stdio transport for communication with ADK agents
11. THE Event_Storage_MCP SHALL handle concurrent read operations safely (multiple agents querying simultaneously)
12. WHEN exporting to mailbox, THE Event_Storage_MCP SHALL create the mailbox directory if it does not exist

### Requirement 3: Attack-Injector MCP Server

**User Story:** As an AI agent, I want to inject realistic attack simulations into the event stream, so that I can test detection algorithms and train behavior analysis models.

#### Acceptance Criteria

1. THE Attack_Injector_MCP SHALL expose an inject_attack tool that accepts attack_type and mitre_technique parameters and generates synthetic attack events
2. THE Attack_Injector_MCP SHALL support 4 insider threat attack types: data_exfiltration_usb, data_exfiltration_email, credential_theft, file_discovery
3. THE Attack_Injector_MCP SHALL map attack types to MITRE ATT&CK techniques (T1052 for USB exfiltration, T1114 for email exfiltration, T1555 for credential theft, T1083 for file discovery)
4. WHEN generating attack events, THE Attack_Injector_MCP SHALL create realistic behavioral sequences (e.g., file_discovery → file_access → device_connect → file_access for USB exfiltration)
5. THE Attack_Injector_MCP SHALL mark all generated events with is_simulated=True, attack_type, and mitre_technique in the metadata field
6. THE Attack_Injector_MCP SHALL generate timestamps that follow realistic temporal patterns (e.g., credential theft followed by lateral movement within 5-30 minutes)
7. THE Attack_Injector_MCP SHALL use realistic user_id and device_id values from data/enrichment/user_device_map.json
8. THE Attack_Injector_MCP SHALL expose a list_attack_types tool that returns available attack types with descriptions and MITRE technique mappings
9. THE Attack_Injector_MCP SHALL return generated attack events as StandardEvent dictionaries compatible with Event_Storage_MCP
10. THE Attack_Injector_MCP SHALL use stdio transport for communication with ADK agents
11. WHEN generating email exfiltration attacks, THE Attack_Injector_MCP SHALL include external recipients and large attachment sizes in metadata
12. WHEN generating USB exfiltration attacks, THE Attack_Injector_MCP SHALL include device_connect events followed by file_access events with is_usb=True

### Requirement 4: Enrichment MCP Server

**User Story:** As an AI agent, I want to enrich events with user and device context, so that I can add department, privilege level, and asset criticality information for risk scoring.

#### Acceptance Criteria

1. THE Enrichment_MCP SHALL expose an enrich_events tool that accepts an array of StandardEvent dictionaries and returns enriched versions with additional metadata
2. THE Enrichment_MCP SHALL load user and device mappings from data/enrichment/user_device_map.json at startup
3. WHEN enriching events, THE Enrichment_MCP SHALL add department, privilege_level, and asset_criticality fields to the metadata based on user_id and device_id lookups
4. THE Enrichment_MCP SHALL expose a correlate_events tool that identifies related events (same user, same device, within time window) and adds correlation_id to metadata
5. WHEN a user_id or device_id is not found in the mapping file, THE Enrichment_MCP SHALL add unknown values for department, privilege_level, and asset_criticality
6. THE Enrichment_MCP SHALL support time-based correlation with a configurable time_window_minutes parameter (default 10, range 1-60)
7. THE Enrichment_MCP SHALL expose an add_user_device_mapping tool that allows agents to add new user/device entries to the mapping file
8. THE Enrichment_MCP SHALL validate that enriched events still conform to the StandardEvent schema
9. THE Enrichment_MCP SHALL use stdio transport for communication with ADK agents
10. WHEN correlating events, THE Enrichment_MCP SHALL generate a unique correlation_id (UUID format) for each event group
11. THE Enrichment_MCP SHALL preserve all original event fields when adding enrichment metadata

### Requirement 5: Python-Executor MCP Server

**User Story:** As an AI agent, I want to execute Python code safely in a sandboxed environment, so that I can perform custom data transformations and analysis without compromising system security.

#### Acceptance Criteria

1. THE Python_Executor_MCP SHALL expose an execute_code tool that accepts Python code as a string parameter and returns execution results
2. THE Python_Executor_MCP SHALL execute code in a Daytona sandbox with restricted permissions (no file system write access outside /tmp, no network access by default)
3. THE Python_Executor_MCP SHALL whitelist allowed imports (json, datetime, re, math, statistics, collections, itertools, functools)
4. THE Python_Executor_MCP SHALL enforce a 10-second execution timeout and terminate code that exceeds this limit
5. IF code execution raises an exception, THEN THE Python_Executor_MCP SHALL return the exception type, message, and traceback in the error field
6. THE Python_Executor_MCP SHALL capture stdout and stderr from executed code and return them in the result
7. THE Python_Executor_MCP SHALL expose a list_allowed_imports tool that returns the whitelist of permitted Python modules
8. THE Python_Executor_MCP SHALL reject code that attempts to import non-whitelisted modules with a descriptive error message
9. THE Python_Executor_MCP SHALL use stdio transport for communication with ADK agents
10. WHEN code execution completes successfully, THE Python_Executor_MCP SHALL return a result object containing stdout, stderr, return_value, and execution_time_ms
11. THE Python_Executor_MCP SHALL sanitize code input to prevent injection attacks (e.g., removing shell command execution attempts)
12. THE Python_Executor_MCP SHALL log all code execution attempts with timestamp, code hash, execution status, and agent identifier

### Requirement 6: MCP Server Infrastructure

**User Story:** As a developer, I want all MCP servers to follow consistent patterns and integrate seamlessly with Google ADK, so that agents can discover and use tools reliably.

#### Acceptance Criteria

1. THE MCP_Servers SHALL use the official MCP Python SDK (not FastMCP) for Google ADK compatibility
2. THE MCP_Servers SHALL communicate via stdio transport (standard input/output) for ADK subprocess communication
3. THE MCP_Servers SHALL define tool schemas using JSON Schema format for ADK discovery
4. THE MCP_Servers SHALL return JSON-serializable dictionaries (not Pydantic model instances directly) from all tool functions
5. THE MCP_Servers SHALL implement graceful error handling that returns structured error responses (error field with type, message, details)
6. THE MCP_Servers SHALL log all operations to logs/mcp_server_name.log with timestamp, log level, and message
7. THE MCP_Servers SHALL validate all tool parameters against their JSON Schema definitions before execution
8. THE MCP_Servers SHALL include a README.md file in each server directory documenting available tools, parameters, return types, and usage examples
9. THE MCP_Servers SHALL be executable as standalone Python modules (python -m mcp_servers.server_name)
10. THE MCP_Servers SHALL register with ADK via an mcp_config.json file that lists all server names, executable paths, and transport types
11. WHEN an MCP server starts, THE MCP_Server SHALL log its initialization status and available tools
12. THE MCP_Servers SHALL handle SIGTERM and SIGINT signals gracefully by cleaning up resources and exiting

### Requirement 7: ADK Integration and Testing

**User Story:** As a developer, I want to validate that all MCP servers work correctly with Google ADK, so that I can ensure Phase 3 agents will function properly.

#### Acceptance Criteria

1. THE Project SHALL include an mcp_config.json file in the root directory that registers all 5 MCP servers for ADK discovery
2. THE Project SHALL include a test agent (tests/test_adk_agent.py) that invokes at least one tool from each MCP server
3. WHEN the test agent runs, THE Test_Agent SHALL successfully discover all 5 MCP servers and their tools
4. THE Test_Agent SHALL execute a sample workflow: collect events → store events → inject attack → enrich events → query events → export to mailbox
5. THE Test_Agent SHALL validate that all tool invocations return expected response formats (no schema violations)
6. THE Test_Agent SHALL log all tool invocations and responses for debugging
7. THE Project SHALL include a test script (tests/run_mcp_tests.sh or tests/run_mcp_tests.bat) that starts all MCP servers and runs the test agent
8. WHEN all tests pass, THE Test_Script SHALL output a success message with summary statistics (tools tested, invocations, pass/fail counts)
9. IF any test fails, THEN THE Test_Script SHALL output detailed error information and exit with a non-zero status code
10. THE Project SHALL document the testing process in a TESTING.md file with step-by-step instructions

### Requirement 8: Documentation and Code Quality

**User Story:** As a developer, I want comprehensive documentation and clean code, so that I can understand, maintain, and extend the MCP servers easily.

#### Acceptance Criteria

1. THE Project SHALL include a Phase 2 summary document (PHASE_2_COMPLETE.md) that describes all implemented MCP servers, tools, and integration points
2. THE MCP_Servers SHALL include docstrings for all classes, functions, and tool definitions following Google Python style guide
3. THE MCP_Servers SHALL use type hints for all function parameters and return values
4. THE Project SHALL include a README.md in the mcp_servers/ directory that provides an overview of all servers and their purposes
5. THE MCP_Servers SHALL follow consistent naming conventions (snake_case for functions/variables, PascalCase for classes)
6. THE MCP_Servers SHALL include inline comments for complex logic (e.g., attack sequence generation, event correlation algorithms)
7. THE Project SHALL include example usage snippets in each server's README.md showing how to invoke tools from ADK agents
8. THE MCP_Servers SHALL handle edge cases gracefully (empty input arrays, missing files, invalid parameters) with descriptive error messages
9. THE Project SHALL include a requirements.txt entry for the MCP Python SDK and Daytona sandbox dependencies
10. THE Project SHALL maintain consistency with Phase 1 documentation style (clear, concise, developer-friendly)

### Requirement 9: Data Format and Inter-Team Communication

**User Story:** As Team 2, I want to receive enriched event data in a consistent JSON format, so that I can build behavior analysis models without worrying about data parsing issues.

#### Acceptance Criteria

1. THE Event_Storage_MCP SHALL export events to mailbox/clean_events.json in JSON array format (one array of StandardEvent dictionaries)
2. THE Exported_Events SHALL include all StandardEvent fields (event_id, timestamp, user_id, device_id, event_type, event_category, action, resource, metadata, source)
3. THE Exported_Events SHALL include enrichment metadata (department, privilege_level, asset_criticality, correlation_id) when available
4. THE Exported_Events SHALL include attack simulation metadata (is_simulated, attack_type, mitre_technique) for injected attacks
5. THE Event_Storage_MCP SHALL create a metadata file (mailbox/clean_events_metadata.json) with export timestamp, event count, time range, and data source information
6. THE Exported_Events SHALL use ISO 8601 format for all timestamps
7. THE Exported_Events SHALL use consistent field naming (snake_case) across all event types
8. THE Event_Storage_MCP SHALL validate exported data against StandardEvent schema before writing to mailbox
9. WHEN exporting events, THE Event_Storage_MCP SHALL sort events by timestamp in ascending order
10. THE Event_Storage_MCP SHALL support incremental exports (export only events since last export timestamp)

### Requirement 10: Error Handling and Resilience

**User Story:** As an AI agent, I want MCP servers to handle errors gracefully and provide useful feedback, so that I can recover from failures and continue processing.

#### Acceptance Criteria

1. WHEN a tool invocation fails due to invalid parameters, THE MCP_Server SHALL return an error response with error_type="validation_error" and a descriptive message
2. WHEN a tool invocation fails due to missing dependencies (e.g., collector module not found), THE MCP_Server SHALL return an error response with error_type="dependency_error"
3. WHEN a tool invocation fails due to timeout, THE MCP_Server SHALL return an error response with error_type="timeout_error" and the elapsed time
4. WHEN a tool invocation fails due to an unexpected exception, THE MCP_Server SHALL return an error response with error_type="internal_error" and a sanitized stack trace
5. THE MCP_Servers SHALL log all errors to their respective log files with ERROR level
6. THE MCP_Servers SHALL continue running after non-fatal errors (tool invocation failures SHALL NOT crash the server)
7. WHEN a collector returns partial results due to permission errors, THE Collector_Executor_MCP SHALL include the partial data in the response with a warning field
8. WHEN the Event_Storage_MCP encounters a corrupted event file, THE Event_Storage_MCP SHALL skip the corrupted file and log a warning
9. WHEN the Enrichment_MCP cannot load the user_device_map.json file, THE Enrichment_MCP SHALL return events without enrichment and log a warning
10. THE MCP_Servers SHALL implement retry logic for transient failures (e.g., file system locks) with exponential backoff (3 retries, 1s/2s/4s delays)

### Requirement 11: Performance and Scalability

**User Story:** As an AI agent, I want MCP servers to respond quickly and handle reasonable data volumes, so that I can process events efficiently without long wait times.

#### Acceptance Criteria

1. THE Collector_Executor_MCP SHALL complete collector execution within 30 seconds for all collectors
2. THE Event_Storage_MCP SHALL store 1000 events within 5 seconds
3. THE Event_Storage_MCP SHALL query 10,000 events with filters within 3 seconds
4. THE Attack_Injector_MCP SHALL generate a complete attack sequence (5-10 events) within 1 second
5. THE Enrichment_MCP SHALL enrich 1000 events within 2 seconds
6. THE Python_Executor_MCP SHALL enforce a 10-second timeout for code execution
7. THE MCP_Servers SHALL use efficient data structures (dictionaries for lookups, generators for large result sets)
8. THE Event_Storage_MCP SHALL use JSON Lines format (one event per line) for efficient append operations
9. THE MCP_Servers SHALL limit memory usage to 500MB per server under normal operation
10. THE MCP_Servers SHALL support concurrent tool invocations from multiple agents (thread-safe operations)

### Requirement 12: Security and Sandboxing

**User Story:** As a system administrator, I want MCP servers to execute untrusted code safely, so that malicious agents cannot compromise the system.

#### Acceptance Criteria

1. THE Python_Executor_MCP SHALL execute all code in a Daytona sandbox with restricted file system access
2. THE Python_Executor_MCP SHALL block network access by default (no socket operations)
3. THE Python_Executor_MCP SHALL whitelist allowed imports and reject attempts to import os, subprocess, sys, socket, requests, urllib
4. THE Python_Executor_MCP SHALL sanitize code input to prevent shell injection attacks
5. THE Python_Executor_MCP SHALL enforce resource limits (10-second timeout, 100MB memory limit)
6. THE MCP_Servers SHALL validate all file paths to prevent directory traversal attacks (e.g., reject paths containing ../)
7. THE MCP_Servers SHALL sanitize user_id and device_id inputs to prevent injection attacks in file names
8. THE Event_Storage_MCP SHALL restrict file operations to the logs/ and mailbox/ directories
9. THE Enrichment_MCP SHALL restrict file operations to the data/enrichment/ directory
10. THE MCP_Servers SHALL log all security-relevant events (code execution, file access, validation failures) with WARNING or ERROR level

## Special Requirements Guidance

### Parser and Serializer Requirements

This feature includes JSON parsing and serialization for StandardEvent objects. The following requirements ensure correctness:

**Requirement 13: JSON Serialization and Parsing**

**User Story:** As a developer, I want StandardEvent objects to serialize and deserialize correctly, so that data integrity is maintained across MCP server boundaries.

#### Acceptance Criteria

1. THE Event_Storage_MCP SHALL serialize StandardEvent Pydantic models to JSON dictionaries using model.model_dump()
2. THE Event_Storage_MCP SHALL parse JSON dictionaries to StandardEvent Pydantic models using StandardEvent.model_validate()
3. THE Event_Storage_MCP SHALL include a round-trip test that verifies: parse(serialize(event)) produces an equivalent event
4. WHEN serializing events, THE Event_Storage_MCP SHALL preserve all metadata fields including optional fields with None values
5. WHEN parsing events, THE Event_Storage_MCP SHALL validate required fields (event_id, timestamp, user_id, device_id, event_type, event_category, action, resource, source) and reject events missing these fields
6. THE Event_Storage_MCP SHALL handle datetime objects by converting them to ISO 8601 strings during serialization
7. THE Event_Storage_MCP SHALL parse ISO 8601 timestamp strings during deserialization
8. THE MCP_Servers SHALL use json.dumps() with indent=2 for human-readable output when writing to mailbox files
9. THE MCP_Servers SHALL use json.dumps() without indentation for JSON Lines format (logs/events_*.jsonl)
10. THE Event_Storage_MCP SHALL validate that serialized JSON can be parsed by standard JSON parsers (no custom extensions)

## Iteration and Feedback Rules

This requirements document is subject to review and iteration. Modifications will be made based on user feedback to ensure all requirements are clear, testable, and aligned with project goals.

## Phase Completion

This requirements document represents the complete specification for Phase 2: MCP Tool Servers. Upon approval, the next phase will be the design document, which will specify the technical architecture, API contracts, and implementation details for each MCP server.
