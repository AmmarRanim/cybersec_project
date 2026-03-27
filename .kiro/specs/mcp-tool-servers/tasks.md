# Implementation Plan: MCP Tool Servers

## Overview

This implementation plan breaks down Phase 2 of the Cyber-Data Genesis project into discrete coding tasks. The plan implements 5 MCP servers that expose data collection, storage, attack simulation, enrichment, and code execution capabilities to Google ADK AI agents via the Model Context Protocol.

The implementation follows this sequence:
1. Set up infrastructure and shared utilities
2. Implement each MCP server with its core functionality
3. Add testing and validation
4. Create integration tests and documentation

## Tasks

- [x] 1. Set up MCP server infrastructure
  - Create mcp_servers/ directory structure with __init__.py files
  - Install MCP Python SDK and Daytona dependencies in requirements.txt
  - Create shared utilities module (mcp_servers/common/utils.py) for logging, error handling, and validation
  - Create mcp_config.json in project root with all 5 server registrations
  - _Requirements: 6.1, 6.2, 6.10, 8.9_

- [ ]* 1.1 Write property test for MCP server initialization
  - **Property 21: Collector Execution Isolation**
  - **Validates: Requirements 1.8**

- [x] 2. Implement Collector-Executor MCP Server
  - [x] 2.1 Create collector_executor/server.py with MCP SDK setup
    - Implement stdio transport and JSON-RPC handling
    - Set up logging to logs/collector_executor.log
    - _Requirements: 1.1, 1.6, 1.9, 6.6_

  - [x] 2.2 Define tool schemas for all 11 collectors
    - Create collector_executor/tool_definitions.py with JSON Schema definitions
    - Include hours_back parameter for time-range collectors (email, browser, windows_event, dns)
    - _Requirements: 1.1, 1.3, 1.7_

  - [x] 2.3 Implement collector execution logic
    - Use subprocess.run() with 30-second timeout to execute collector modules
    - Parse JSON output and validate against StandardEvent schema
    - Return structured responses with events, count, collector name, execution_time_ms
    - _Requirements: 1.2, 1.10_

  - [x] 2.4 Add error handling for collector failures
    - Handle timeout errors, module not found, permission errors
    - Return partial results with error field for failures
    - _Requirements: 1.4, 10.1, 10.2, 10.3, 10.7_

  - [ ]* 2.5 Write property test for collector invocation
    - **Property 1: Collector Invocation Returns Valid Events**
    - **Validates: Requirements 1.2, 1.9**

  - [ ]* 2.6 Write property test for time-range parameters
    - **Property 2: Time-Range Parameter Acceptance**
    - **Validates: Requirements 1.3**

  - [ ]* 2.7 Write property test for collector failure handling
    - **Property 3: Collector Failure Returns Structured Error**
    - **Validates: Requirements 1.4**

  - [ ]* 2.8 Write property test for parameter validation
    - **Property 4: Invalid Parameters Rejected Before Execution**
    - **Validates: Requirements 1.5**

  - [ ]* 2.9 Write property test for timeout enforcement
    - **Property 22: Timeout Enforcement**
    - **Validates: Requirements 1.10**

  - [x] 2.10 Create collector_executor/README.md with usage examples
    - Document all 11 tools with parameters and return types
    - Include ADK agent invocation examples
    - _Requirements: 6.8, 8.7_

- [x] 3. Checkpoint - Verify Collector-Executor MCP
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Event-Storage MCP Server
  - [x] 4.1 Create event_storage/server.py with MCP SDK setup
    - Implement stdio transport and JSON-RPC handling
    - Set up logging to logs/event_storage.log
    - _Requirements: 2.10, 6.6_

  - [x] 4.2 Implement storage engine (event_storage/storage_engine.py)
    - Create store_events function that writes to logs/events_YYYY-MM-DD.jsonl
    - Use JSON Lines format (one event per line, no indentation)
    - Validate events against StandardEvent schema before storage
    - Create logs/ directory if it doesn't exist
    - _Requirements: 2.1, 2.2, 2.7, 13.1, 13.2, 13.9_

  - [x] 4.3 Implement query engine (event_storage/query_engine.py)
    - Create query_events function with filters (event_type, event_category, user_id, device_id, start_time, end_time)
    - Parse ISO 8601 timestamps and apply inclusive range filtering
    - Implement pagination with page_size and page parameters
    - Use generator pattern for memory-efficient streaming
    - Return empty array with message if no matches found
    - _Requirements: 2.3, 2.6, 2.8, 2.9_

  - [x] 4.4 Implement summary statistics (get_summary tool)
    - Calculate total event count, events by type, events by category
    - Count unique users and unique devices
    - Determine time range (earliest and latest timestamps)
    - _Requirements: 2.4_

  - [x] 4.5 Implement mailbox export (export_to_mailbox tool)
    - Write filtered events to mailbox/clean_events.json with metadata
    - Use JSON format with indent=2 for human readability
    - Sort events by timestamp in ascending order
    - Create mailbox/ directory if it doesn't exist
    - Create mailbox/clean_events_metadata.json with export details
    - _Requirements: 2.5, 2.12, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9_

  - [x] 4.6 Add concurrent read safety
    - Implement file locking for safe concurrent queries
    - Handle corrupted event files gracefully (skip and log warning)
    - _Requirements: 2.11, 10.8_

  - [ ]* 4.7 Write property test for storage round-trip
    - **Property 5: Event Storage Round-Trip Preservation**
    - **Validates: Requirements 2.1, 2.5, 13.3**

  - [ ]* 4.8 Write property test for query filtering
    - **Property 6: Query Filtering Returns Only Matching Events**
    - **Validates: Requirements 2.3, 2.6**

  - [ ]* 4.9 Write property test for summary statistics
    - **Property 7: Summary Statistics Accuracy**
    - **Validates: Requirements 2.4**

  - [ ]* 4.10 Write property test for pagination
    - **Property 19: Pagination Returns Correct Subsets**
    - **Validates: Requirements 2.8**

  - [ ]* 4.11 Write property test for concurrent reads
    - **Property 20: Concurrent Reads Maintain Data Integrity**
    - **Validates: Requirements 2.11**

  - [x] 4.12 Create event_storage/README.md with usage examples
    - Document all 4 tools with parameters and return types
    - Include query filter examples and pagination usage
    - _Requirements: 6.8, 8.7_

- [x] 5. Checkpoint - Verify Event-Storage MCP
  - Ensure all tests pass, ask the user if questions arise.

- [-] 6. Implement Attack-Injector MCP Server
  - [x] 6.1 Create attack_injector/server.py with MCP SDK setup
    - Implement stdio transport and JSON-RPC handling
    - Set up logging to logs/attack_injector.log
    - _Requirements: 3.10, 6.6_

  - [-] 6.2 Create attack pattern dataset (data/attacks/attack_patterns.json)
    - Define attack pattern schema with event sequences
    - Create initial dataset with 16 attack patterns (6 custom + 10 CERT r4.2) ✓ COMPLETE
    - Include MITRE ATT&CK technique mappings
    - Support randomization parameters (timing, file sizes, resources)
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 6.3 Implement dataset loader (attack_injector/dataset_loader.py)
    - Load attack patterns from JSON dataset
    - Cache patterns in memory for performance
    - Validate pattern schema on load
    - Support filtering by category, MITRE technique, severity
    - _Requirements: 3.1, 3.8_

  - [x] 6.4 Implement attack generator (attack_injector/attack_generator.py)
    - Generate events from dataset pattern definitions
    - Apply realistic temporal patterns (5-30 minute windows)
    - Randomize resources, file sizes, timing variations
    - Load user/device mappings from data/enrichment/user_device_map.json
    - Mark all events with is_simulated=True, attack_type, mitre_technique
    - _Requirements: 3.4, 3.5, 3.6, 3.7, 3.11, 3.12_

  - [x] 6.5 Implement inject_attack tool
    - Accept attack_id, category, or mitre_technique parameters
    - Support optional user_id/device_id (random if not provided)
    - Support randomize flag for timing/resource variations
    - Return StandardEvent dictionaries compatible with Event-Storage MCP
    - _Requirements: 3.1, 3.9_

  - [x] 6.6 Implement list_attack_patterns tool
    - Return all available attack patterns from dataset
    - Support filtering by category, MITRE technique, severity
    - Include pattern metadata (event count, description, technique)
    - _Requirements: 3.8_

  - [x] 6.7 Implement add_attack_pattern tool (optional)
    - Allow agents to add new attack patterns to dataset
    - Validate pattern schema before adding
    - Persist to data/attacks/attack_patterns.json
    - _Requirements: 3.1_

  - [x] 6.8 Create CERT dataset converter (data/attacks/cert_converter.py)
    - Parse CERT r4.2 answers/ directory for labeled attack scenarios ✓ COMPLETE
    - Convert CERT attack sequences to attack_patterns.json format ✓ COMPLETE
    - Map CERT event types to StandardEvent schema ✓ COMPLETE
    - Extract attack metadata (user, dates, scenario description) ✓ COMPLETE
    - Support both custom patterns and CERT patterns in dataset ✓ COMPLETE
    - Successfully converted 10 real insider threat instances from CERT r4.2
    - _Requirements: 3.1, 3.2, 3.3, 3.7_

  - [ ]* 6.9 Write property test for attack simulation metadata
    - **Property 8: Attack Events Marked with Simulation Metadata**
    - **Validates: Requirements 3.3, 3.5, 3.9**

  - [ ]* 6.10 Write property test for attack sequence patterns
    - **Property 9: Attack Sequences Follow Realistic Patterns**
    - **Validates: Requirements 3.4, 3.6, 3.11, 3.12**

  - [ ]* 6.11 Write property test for user/device ID validity
    - **Property 10: Attack Events Use Valid User/Device IDs**
    - **Validates: Requirements 3.7**

  - [x] 6.12 Create attack_injector/README.md with usage examples
    - Document dataset-driven architecture
    - Explain attack pattern schema
    - Include example tool invocations for all 3 tools
    - Document how to add custom attack patterns
    - Document CERT r4.2 dataset integration
    - _Requirements: 6.8, 8.7_

- [x] 7. Checkpoint - Verify Attack-Injector MCP
  - All tests pass ✓
  - 16 attack patterns loaded (6 custom + 10 CERT r4.2) ✓
  - CERT converter successfully extracts real insider threat patterns ✓

- [ ] 8. Implement Enrichment MCP Server
  - [ ] 8.1 Create enrichment/server.py with MCP SDK setup
    - Implement stdio transport and JSON-RPC handling
    - Set up logging to logs/enrichment.log
    - Load user_device_map.json at startup with caching
    - _Requirements: 4.2, 4.9, 6.6_

  - [ ] 8.2 Implement enrichment engine (enrichment/enrichment_engine.py)
    - Create enrich_events function that adds department, privilege_level, asset_criticality
    - Lookup user_id and device_id in cached mappings
    - Set "unknown" values for missing user_id/device_id
    - Preserve all original event fields
    - Validate enriched events against StandardEvent schema
    - _Requirements: 4.1, 4.3, 4.5, 4.8, 4.11_

  - [ ] 8.3 Implement correlation engine (enrichment/correlation_engine.py)
    - Create correlate_events function with time_window_minutes parameter
    - Sort events by timestamp
    - Group events by (user_id, device_id) within time window
    - Generate unique correlation_id (UUID) for each group
    - Add correlation_id to metadata
    - _Requirements: 4.4, 4.6, 4.10_

  - [ ] 8.4 Implement add_user_device_mapping tool
    - Accept new user/device entries and update data/enrichment/user_device_map.json
    - Validate input format before updating file
    - Reload cached mappings after update
    - _Requirements: 4.7_

  - [ ] 8.5 Add error handling for missing mapping file
    - Return events without enrichment if mapping file missing
    - Log warning for missing file
    - _Requirements: 10.9_

  - [ ]* 8.6 Write property test for enrichment without modification
    - **Property 11: Enrichment Adds Context Without Modifying Original Fields**
    - **Validates: Requirements 4.1, 4.3, 4.11**

  - [ ]* 8.7 Write property test for event correlation
    - **Property 12: Event Correlation Groups Related Events**
    - **Validates: Requirements 4.4, 4.6, 4.10**

  - [ ]* 8.8 Write property test for schema compliance
    - **Property 13: Enriched Events Maintain Schema Compliance**
    - **Validates: Requirements 4.8**

  - [ ] 8.9 Create enrichment/README.md with usage examples
    - Document enrichment and correlation tools
    - Include examples of enriched event output
    - _Requirements: 6.8, 8.7_

- [ ] 9. Checkpoint - Verify Enrichment MCP
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement Python-Executor MCP Server
  - [ ] 10.1 Create python_executor/server.py with MCP SDK setup
    - Implement stdio transport and JSON-RPC handling
    - Set up logging to logs/python_executor.log with code hash logging
    - _Requirements: 5.9, 5.12, 6.6_

  - [ ] 10.2 Implement sandbox configuration (python_executor/sandbox_config.py)
    - Define ALLOWED_IMPORTS whitelist (json, datetime, re, math, statistics, collections, itertools, functools)
    - Define DANGEROUS_PATTERNS for code sanitization
    - Configure Daytona sandbox with timeout, memory limit, file system restrictions
    - _Requirements: 5.2, 5.3, 5.4, 12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ] 10.3 Implement code sanitization
    - Scan code for dangerous patterns (__import__, eval, exec, os., subprocess., etc.)
    - Reject code with blocked patterns before execution
    - _Requirements: 5.8, 5.11, 12.4_

  - [ ] 10.4 Implement execute_code tool
    - Validate code is not empty
    - Sanitize code for dangerous patterns
    - Execute in Daytona sandbox with timeout
    - Capture stdout, stderr, return_value, execution_time_ms
    - Return structured response with all output
    - _Requirements: 5.1, 5.6, 5.10_

  - [ ] 10.5 Add exception handling for code execution
    - Catch execution exceptions and return error with type, message, traceback
    - Handle timeout errors separately
    - _Requirements: 5.5, 10.3_

  - [ ] 10.6 Implement list_allowed_imports tool
    - Return whitelist of permitted Python modules
    - _Requirements: 5.7_

  - [ ]* 10.7 Write property test for sandbox restrictions
    - **Property 14: Sandbox Blocks Restricted Operations**
    - **Validates: Requirements 5.2, 5.3, 5.8, 5.11**

  - [ ]* 10.8 Write property test for output capture
    - **Property 15: Code Execution Captures Output**
    - **Validates: Requirements 5.6, 5.10**

  - [ ]* 10.9 Write property test for exception handling
    - **Property 16: Code Execution Exceptions Return Structured Errors**
    - **Validates: Requirements 5.5**

  - [ ]* 10.10 Write property test for execution logging
    - **Property 17: Code Execution Logging**
    - **Validates: Requirements 5.12**

  - [ ] 10.11 Create python_executor/README.md with usage examples
    - Document allowed imports and sandbox restrictions
    - Include example code snippets and expected output
    - _Requirements: 6.8, 8.7_

- [ ] 11. Checkpoint - Verify Python-Executor MCP
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement JSON serialization utilities
  - [ ] 12.1 Create serialization utilities in mcp_servers/common/serialization.py
    - Implement serialize_event function using model.model_dump()
    - Implement deserialize_event function using StandardEvent.model_validate()
    - Handle datetime to ISO 8601 string conversion
    - _Requirements: 13.1, 13.2, 13.6, 13.7_

  - [ ] 12.2 Add validation for required fields
    - Validate required fields (event_id, timestamp, user_id, device_id, event_type, event_category, action, resource, source)
    - Reject events missing required fields with descriptive errors
    - _Requirements: 13.5_

  - [ ]* 12.3 Write property test for serialization round-trip
    - **Property 18: Serialization Round-Trip Preserves All Fields**
    - **Validates: Requirements 13.3, 13.4, 13.6, 13.7, 13.10**

- [ ] 13. Create integration tests
  - [ ] 13.1 Create test ADK agent (tests/test_adk_agent.py)
    - Implement workflow: collect → store → inject → enrich → query → export
    - Validate tool discovery for all 5 MCP servers
    - Validate response formats against JSON schemas
    - Log all tool invocations and responses
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ] 13.2 Create test script (tests/run_mcp_tests.sh for Unix, tests/run_mcp_tests.bat for Windows)
    - Start all 5 MCP servers in background
    - Run test agent
    - Capture exit code and output summary
    - Kill all MCP servers on completion
    - _Requirements: 7.7, 7.8, 7.9_

  - [ ] 13.3 Create TESTING.md documentation
    - Document step-by-step testing process
    - Include prerequisites and setup instructions
    - Explain how to run individual tests and full test suite
    - _Requirements: 7.10_

- [ ] 14. Add performance tests
  - [ ]* 14.1 Write performance test for collector execution time
    - Validate collectors complete within 30 seconds
    - _Requirements: 11.1_

  - [ ]* 14.2 Write performance test for event storage
    - Validate storing 1000 events within 5 seconds
    - _Requirements: 11.2_

  - [ ]* 14.3 Write performance test for event queries
    - Validate querying 10,000 events within 3 seconds
    - _Requirements: 11.3_

  - [ ]* 14.4 Write performance test for attack injection
    - Validate generating attack sequence within 1 second
    - _Requirements: 11.4_

  - [ ]* 14.5 Write performance test for enrichment
    - Validate enriching 1000 events within 2 seconds
    - _Requirements: 11.5_

- [ ] 15. Create documentation
  - [ ] 15.1 Create mcp_servers/README.md
    - Provide overview of all 5 MCP servers and their purposes
    - Include architecture diagram and communication flow
    - Document installation and configuration steps
    - _Requirements: 8.4_

  - [ ] 15.2 Create PHASE_2_COMPLETE.md
    - Summarize all implemented MCP servers and tools
    - Document integration points with Phase 1 collectors
    - Include statistics (number of tools, servers, test coverage)
    - Provide next steps for Phase 3 integration
    - _Requirements: 8.1_

  - [ ] 15.3 Add docstrings to all code
    - Follow Google Python style guide for docstrings
    - Include type hints for all function parameters and return values
    - Add inline comments for complex logic
    - _Requirements: 8.2, 8.3, 8.6_

- [ ] 16. Final checkpoint - Complete integration test
  - Run full test suite (unit tests, property tests, integration tests, performance tests)
  - Verify all 5 MCP servers start successfully
  - Validate complete workflow from collection to mailbox export
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each major component
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- All MCP servers use stdio transport for Google ADK compatibility
- All events must conform to StandardEvent schema from Phase 1
