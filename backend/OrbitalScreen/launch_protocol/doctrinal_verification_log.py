"""
Orbital Screen Doctrinal Verification Log
Logs all launch maneuvers and credential events

Timestamp: 2025-11-01 15:35:00 UTC
Mission: Scaffold Cockpit Launch Protocol
Commander: Orbital
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse


class EventType(Enum):
    """Types of events that can be logged"""
    AGENT_ARRIVAL = "agent_arrival"
    ORIENTATION_START = "orientation_start"
    ORIENTATION_COMPLETE = "orientation_complete"
    CREDENTIAL_ASSIGNED = "credential_assigned"
    CREDENTIAL_MODIFIED = "credential_modified"
    CREDENTIAL_REVOKED = "credential_revoked"
    LAUNCH_INITIATED = "launch_initiated"
    LAUNCH_COMPLETE = "launch_complete"
    HANDOFF_INITIATED = "handoff_initiated"
    HANDOFF_COMPLETE = "handoff_complete"
    GRADUATION = "graduation"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    SECURITY_VIOLATION = "security_violation"
    SYSTEM_ERROR = "system_error"
    CHECKPOINT_CREATED = "checkpoint_created"


class EventSeverity(Enum):
    """Severity levels for logged events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class VerificationEvent:
    """Represents a verification event in the log"""
    event_id: str
    timestamp: str
    event_type: EventType
    severity: EventSeverity
    agent_id: str
    action: str
    details: Dict[str, Any]
    verification_hash: str
    logged_by: str
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "agent_id": self.agent_id,
            "action": self.action,
            "details": self.details,
            "verification_hash": self.verification_hash,
            "logged_by": self.logged_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VerificationEvent':
        """Create event from dictionary"""
        return cls(
            event_id=data["event_id"],
            timestamp=data["timestamp"],
            event_type=EventType(data["event_type"]),
            severity=EventSeverity(data["severity"]),
            agent_id=data["agent_id"],
            action=data["action"],
            details=data["details"],
            verification_hash=data["verification_hash"],
            logged_by=data["logged_by"]
        )


class DoctrinealVerificationLog:
    """
    Logs all launch maneuvers and credential events with verification
    """
    
    def __init__(
        self,
        log_file: str = "doctrinal_verification.log",
        json_log_file: str = "doctrinal_verification.json"
    ):
        self.log_file = log_file
        self.json_log_file = json_log_file
        self.events: List[VerificationEvent] = []
        self.logger = self._setup_logger()
        self._load_existing_logs()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for verification events"""
        logger = logging.getLogger("DoctrinealVerificationLog")
        logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(self.log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _generate_event_id(self, agent_id: str, timestamp: str) -> str:
        """Generate unique event ID"""
        data = f"{agent_id}:{timestamp}:{len(self.events)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_verification_hash(self, event: VerificationEvent) -> str:
        """Generate verification hash for event integrity"""
        data = f"{event.event_id}:{event.timestamp}:{event.agent_id}:{event.action}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _load_existing_logs(self) -> None:
        """Load existing logs from JSON file"""
        json_path = Path(self.json_log_file)
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    self.events = [
                        VerificationEvent.from_dict(event_data)
                        for event_data in data.get("events", [])
                    ]
                self.logger.info(f"Loaded {len(self.events)} existing events")
            except Exception as e:
                self.logger.error(f"Failed to load existing logs: {e}")
    
    def _save_logs(self) -> None:
        """Save logs to JSON file"""
        try:
            log_data = {
                "metadata": {
                    "version": "1.0.0",
                    "last_updated": datetime.utcnow().isoformat(),
                    "total_events": len(self.events)
                },
                "events": [event.to_dict() for event in self.events]
            }
            
            with open(self.json_log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.events)} events to {self.json_log_file}")
        except Exception as e:
            self.logger.error(f"Failed to save logs: {e}")
    
    def log_event(
        self,
        event_type: EventType,
        agent_id: str,
        action: str,
        details: Dict[str, Any],
        severity: EventSeverity = EventSeverity.INFO,
        logged_by: str = "system"
    ) -> str:
        """
        Log a verification event
        
        Args:
            event_type: Type of event
            agent_id: ID of the agent involved
            action: Action being performed
            details: Additional details about the event
            severity: Severity level of the event
            logged_by: Who logged this event
            
        Returns:
            event_id: Unique identifier for the logged event
        """
        timestamp = datetime.utcnow().isoformat()
        event_id = self._generate_event_id(agent_id, timestamp)
        
        event = VerificationEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            severity=severity,
            agent_id=agent_id,
            action=action,
            details=details,
            verification_hash="",
            logged_by=logged_by
        )
        
        event.verification_hash = self._generate_verification_hash(event)
        
        self.events.append(event)
        self._save_logs()
        
        log_message = (
            f"Event: {event_type.value} | "
            f"Agent: {agent_id} | "
            f"Action: {action} | "
            f"Severity: {severity.value}"
        )
        
        if severity == EventSeverity.INFO:
            self.logger.info(log_message)
        elif severity == EventSeverity.WARNING:
            self.logger.warning(log_message)
        elif severity == EventSeverity.ERROR:
            self.logger.error(log_message)
        elif severity == EventSeverity.CRITICAL:
            self.logger.critical(log_message)
        
        return event_id
    
    def log_agent_arrival(self, agent_id: str, agent_name: str, agent_type: str) -> str:
        """Log agent arrival event"""
        return self.log_event(
            event_type=EventType.AGENT_ARRIVAL,
            agent_id=agent_id,
            action="agent_arrived",
            details={
                "agent_name": agent_name,
                "agent_type": agent_type,
                "arrival_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_orientation_start(self, agent_id: str) -> str:
        """Log orientation start event"""
        return self.log_event(
            event_type=EventType.ORIENTATION_START,
            agent_id=agent_id,
            action="orientation_started",
            details={
                "start_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_orientation_complete(self, agent_id: str, modules_completed: List[str]) -> str:
        """Log orientation completion event"""
        return self.log_event(
            event_type=EventType.ORIENTATION_COMPLETE,
            agent_id=agent_id,
            action="orientation_completed",
            details={
                "modules_completed": modules_completed,
                "completion_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_credential_assigned(
        self,
        agent_id: str,
        clearance_level: str,
        permissions: List[str]
    ) -> str:
        """Log credential assignment event"""
        return self.log_event(
            event_type=EventType.CREDENTIAL_ASSIGNED,
            agent_id=agent_id,
            action="credentials_assigned",
            details={
                "clearance_level": clearance_level,
                "permissions": permissions,
                "assigned_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO,
            logged_by="credential_system"
        )
    
    def log_credential_modified(
        self,
        agent_id: str,
        old_clearance: str,
        new_clearance: str,
        reason: str
    ) -> str:
        """Log credential modification event"""
        return self.log_event(
            event_type=EventType.CREDENTIAL_MODIFIED,
            agent_id=agent_id,
            action="credentials_modified",
            details={
                "old_clearance_level": old_clearance,
                "new_clearance_level": new_clearance,
                "reason": reason,
                "modified_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.WARNING,
            logged_by="credential_system"
        )
    
    def log_launch_initiated(self, agent_id: str, launch_checklist_complete: bool) -> str:
        """Log launch initiation event"""
        return self.log_event(
            event_type=EventType.LAUNCH_INITIATED,
            agent_id=agent_id,
            action="launch_initiated",
            details={
                "checklist_complete": launch_checklist_complete,
                "initiated_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_launch_complete(self, agent_id: str, status: str) -> str:
        """Log launch completion event"""
        return self.log_event(
            event_type=EventType.LAUNCH_COMPLETE,
            agent_id=agent_id,
            action="launch_completed",
            details={
                "status": status,
                "completed_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_handoff_initiated(
        self,
        from_agent: str,
        to_agent: str,
        handoff_data: Dict[str, Any]
    ) -> str:
        """Log handoff initiation event"""
        return self.log_event(
            event_type=EventType.HANDOFF_INITIATED,
            agent_id=from_agent,
            action="handoff_initiated",
            details={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "handoff_data": handoff_data,
                "initiated_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_handoff_complete(self, from_agent: str, to_agent: str) -> str:
        """Log handoff completion event"""
        return self.log_event(
            event_type=EventType.HANDOFF_COMPLETE,
            agent_id=from_agent,
            action="handoff_completed",
            details={
                "from_agent": from_agent,
                "to_agent": to_agent,
                "completed_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_graduation(self, agent_id: str, successor_agent: str) -> str:
        """Log agent graduation event"""
        return self.log_event(
            event_type=EventType.GRADUATION,
            agent_id=agent_id,
            action="agent_graduated",
            details={
                "graduating_agent": agent_id,
                "successor_agent": successor_agent,
                "graduation_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_access_granted(
        self,
        agent_id: str,
        resource: str,
        permission: str
    ) -> str:
        """Log access granted event"""
        return self.log_event(
            event_type=EventType.ACCESS_GRANTED,
            agent_id=agent_id,
            action="access_granted",
            details={
                "resource": resource,
                "permission": permission,
                "granted_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def log_access_denied(
        self,
        agent_id: str,
        resource: str,
        reason: str
    ) -> str:
        """Log access denied event"""
        return self.log_event(
            event_type=EventType.ACCESS_DENIED,
            agent_id=agent_id,
            action="access_denied",
            details={
                "resource": resource,
                "reason": reason,
                "denied_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.WARNING
        )
    
    def log_security_violation(
        self,
        agent_id: str,
        violation_type: str,
        details: Dict[str, Any]
    ) -> str:
        """Log security violation event"""
        return self.log_event(
            event_type=EventType.SECURITY_VIOLATION,
            agent_id=agent_id,
            action="security_violation",
            details={
                "violation_type": violation_type,
                "violation_details": details,
                "detected_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.CRITICAL
        )
    
    def log_checkpoint(
        self,
        agent_id: str,
        checkpoint_type: str,
        checkpoint_data: Dict[str, Any]
    ) -> str:
        """Log checkpoint creation event"""
        return self.log_event(
            event_type=EventType.CHECKPOINT_CREATED,
            agent_id=agent_id,
            action="checkpoint_created",
            details={
                "checkpoint_type": checkpoint_type,
                "checkpoint_data": checkpoint_data,
                "created_timestamp": datetime.utcnow().isoformat()
            },
            severity=EventSeverity.INFO
        )
    
    def get_agent_events(
        self,
        agent_id: str,
        event_type: Optional[EventType] = None
    ) -> List[VerificationEvent]:
        """Get all events for a specific agent"""
        events = [e for e in self.events if e.agent_id == agent_id]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events
    
    def get_recent_events(self, limit: int = 10) -> List[VerificationEvent]:
        """Get most recent events"""
        return sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    def verify_event_integrity(self, event_id: str) -> bool:
        """Verify the integrity of an event"""
        event = next((e for e in self.events if e.event_id == event_id), None)
        if not event:
            return False
        
        expected_hash = self._generate_verification_hash(event)
        return event.verification_hash == expected_hash
    
    def export_report(self, output_file: str, agent_id: Optional[str] = None) -> None:
        """Export verification report"""
        events_to_export = self.events
        if agent_id:
            events_to_export = self.get_agent_events(agent_id)
        
        report_data = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_events": len(events_to_export),
                "agent_filter": agent_id
            },
            "events": [event.to_dict() for event in events_to_export]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.logger.info(f"Report exported to {output_file}")


def main():
    """Command-line interface for doctrinal verification log"""
    parser = argparse.ArgumentParser(
        description="Orbital Screen Doctrinal Verification Log"
    )
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--action", required=True, help="Action to log")
    parser.add_argument("--status", help="Status (for launch complete)")
    parser.add_argument("--details", help="Additional details as JSON string")
    
    args = parser.parse_args()
    
    log = DoctrinealVerificationLog()
    
    details = {}
    if args.details:
        try:
            details = json.loads(args.details)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in --details")
            return
    
    if args.action == "pre_launch_verification":
        event_id = log.log_launch_initiated(args.agent_id, True)
        print(f"Pre-launch verification logged: {event_id}")
    
    elif args.action == "launch_complete":
        status = args.status or "operational"
        event_id = log.log_launch_complete(args.agent_id, status)
        print(f"Launch complete logged: {event_id}")
    
    elif args.action == "agent_arrival":
        event_id = log.log_agent_arrival(
            args.agent_id,
            details.get("agent_name", "Unknown"),
            details.get("agent_type", "autonomous_ai")
        )
        print(f"Agent arrival logged: {event_id}")
    
    else:
        print(f"Unknown action: {args.action}")


if __name__ == "__main__":
    main()
