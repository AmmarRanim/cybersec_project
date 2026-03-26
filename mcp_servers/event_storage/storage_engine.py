"""
Storage Engine for Event-Storage MCP Server

Handles persistent storage of StandardEvent objects in JSON Lines format.
Organizes events by date in logs/events_YYYY-MM-DD.jsonl files.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from collectors.event_schema import StandardEvent
from mcp_servers.common.utils import create_error_response, create_success_response

logger = logging.getLogger("event_storage")


def store_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Store an array of StandardEvent dictionaries to disk.
    
    Events are organized by date in JSON Lines format:
    logs/events_YYYY-MM-DD.jsonl
    
    Args:
        events: List of StandardEvent dictionaries
    
    Returns:
        Success response with count of stored events
    """
    if not events:
        return create_error_response(
            "validation_error",
            "No events provided",
            {"events_count": 0}
        )
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate and organize events by date
    events_by_date = {}
    validated_count = 0
    validation_errors = []
    
    for idx, event_dict in enumerate(events):
        try:
            # Validate against StandardEvent schema
            validated_event = StandardEvent.model_validate(event_dict)
            
            # Parse timestamp to determine file
            timestamp_str = validated_event.timestamp
            try:
                # Handle ISO 8601 timestamps
                if 'T' in timestamp_str:
                    date_str = timestamp_str.split('T')[0]
                else:
                    # Fallback to current date if timestamp format is unexpected
                    date_str = datetime.now().strftime('%Y-%m-%d')
                
                # Group events by date
                if date_str not in events_by_date:
                    events_by_date[date_str] = []
                
                # Convert to dict for JSON serialization
                events_by_date[date_str].append(validated_event.model_dump(mode='json'))
                validated_count += 1
            
            except Exception as e:
                logger.warning(f"Failed to parse timestamp for event {idx}: {e}")
                validation_errors.append({
                    "index": idx,
                    "error": f"Invalid timestamp format: {str(e)}"
                })
        
        except Exception as e:
            logger.warning(f"Event validation failed for event {idx}: {e}")
            validation_errors.append({
                "index": idx,
                "error": str(e)
            })
    
    # Write events to date-specific files
    files_written = []
    for date_str, date_events in events_by_date.items():
        file_path = logs_dir / f"events_{date_str}.jsonl"
        
        try:
            # Append to existing file or create new one
            with open(file_path, 'a', encoding='utf-8') as f:
                for event in date_events:
                    # JSON Lines format: one event per line, no indentation
                    json_line = json.dumps(event, default=str)
                    f.write(json_line + '\n')
            
            files_written.append(str(file_path))
            logger.info(f"Stored {len(date_events)} events to {file_path}")
        
        except Exception as e:
            logger.error(f"Failed to write events to {file_path}: {e}")
            return create_error_response(
                "internal_error",
                f"Failed to write events: {str(e)}",
                {"file": str(file_path)}
            )
    
    # Build response
    response = {
        "stored_count": validated_count,
        "files_written": files_written,
        "total_events": len(events)
    }
    
    if validation_errors:
        response["validation_errors"] = validation_errors
        response["validation_error_count"] = len(validation_errors)
    
    logger.info(f"Successfully stored {validated_count}/{len(events)} events")
    
    return response
