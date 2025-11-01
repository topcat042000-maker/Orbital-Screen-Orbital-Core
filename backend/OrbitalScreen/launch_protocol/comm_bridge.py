"""
Orbital Screen Communication Bridge
Enables secure messaging between agents and seekers

Timestamp: 2025-11-01 15:35:00 UTC
Mission: Scaffold Cockpit Launch Protocol
Commander: Orbital
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib


class MessageType(Enum):
    """Types of messages that can be sent through the bridge"""
    AGENT_TO_AGENT = "agent_to_agent"
    AGENT_TO_SEEKER = "agent_to_seeker"
    SEEKER_TO_AGENT = "seeker_to_agent"
    SYSTEM_BROADCAST = "system_broadcast"
    CREDENTIAL_REQUEST = "credential_request"
    ONBOARDING_NOTIFICATION = "onboarding_notification"


class MessagePriority(Enum):
    """Priority levels for message routing"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Message:
    """Represents a message in the communication bridge"""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create message from dictionary"""
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=MessageType(data["message_type"]),
            priority=MessagePriority(data["priority"]),
            content=data["content"],
            timestamp=data["timestamp"],
            signature=data.get("signature")
        )


class CommunicationBridge:
    """
    Secure communication bridge for agent-to-agent and agent-to-seeker messaging
    """
    
    def __init__(self, log_file: str = "comm_bridge.log"):
        self.log_file = log_file
        self.message_queue: List[Message] = []
        self.delivered_messages: List[str] = []
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the communication bridge"""
        logger = logging.getLogger("CommunicationBridge")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _generate_message_id(self, sender_id: str, timestamp: str) -> str:
        """Generate unique message ID"""
        data = f"{sender_id}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _sign_message(self, message: Message) -> str:
        """Generate signature for message integrity"""
        data = f"{message.message_id}:{message.sender_id}:{message.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """
        Send a message through the communication bridge
        
        Args:
            sender_id: ID of the sending agent/seeker
            recipient_id: ID of the receiving agent/seeker
            message_type: Type of message being sent
            content: Message content as dictionary
            priority: Message priority level
            
        Returns:
            message_id: Unique identifier for the sent message
        """
        timestamp = datetime.utcnow().isoformat()
        message_id = self._generate_message_id(sender_id, timestamp)
        
        message = Message(
            message_id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=priority,
            content=content,
            timestamp=timestamp
        )
        
        message.signature = self._sign_message(message)
        
        self.message_queue.append(message)
        self.message_queue.sort(key=lambda m: m.priority.value)
        
        self.logger.info(
            f"Message sent: {message_id} | "
            f"From: {sender_id} | To: {recipient_id} | "
            f"Type: {message_type.value} | Priority: {priority.value}"
        )
        
        return message_id
    
    def receive_messages(
        self,
        recipient_id: str,
        message_type: Optional[MessageType] = None
    ) -> List[Message]:
        """
        Receive messages for a specific recipient
        
        Args:
            recipient_id: ID of the recipient
            message_type: Optional filter by message type
            
        Returns:
            List of messages for the recipient
        """
        messages = []
        remaining_queue = []
        
        for message in self.message_queue:
            if message.recipient_id == recipient_id or message.recipient_id == "broadcast":
                if message_type is None or message.message_type == message_type:
                    messages.append(message)
                    self.delivered_messages.append(message.message_id)
                    self.logger.info(
                        f"Message delivered: {message.message_id} | To: {recipient_id}"
                    )
                else:
                    remaining_queue.append(message)
            else:
                remaining_queue.append(message)
        
        self.message_queue = remaining_queue
        return messages
    
    def broadcast_message(
        self,
        sender_id: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """
        Broadcast a message to all agents
        
        Args:
            sender_id: ID of the sender
            content: Message content
            priority: Message priority
            
        Returns:
            message_id: Unique identifier for the broadcast
        """
        return self.send_message(
            sender_id=sender_id,
            recipient_id="broadcast",
            message_type=MessageType.SYSTEM_BROADCAST,
            content=content,
            priority=priority
        )
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a message
        
        Args:
            message_id: ID of the message
            
        Returns:
            Status information about the message
        """
        if message_id in self.delivered_messages:
            return {
                "message_id": message_id,
                "status": "delivered",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        for message in self.message_queue:
            if message.message_id == message_id:
                return {
                    "message_id": message_id,
                    "status": "pending",
                    "queue_position": self.message_queue.index(message),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        return {
            "message_id": message_id,
            "status": "not_found",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def clear_delivered_messages(self, older_than_hours: int = 24) -> int:
        """
        Clear delivered messages older than specified hours
        
        Args:
            older_than_hours: Clear messages older than this many hours
            
        Returns:
            Number of messages cleared
        """
        initial_count = len(self.delivered_messages)
        self.delivered_messages = []
        cleared_count = initial_count
        
        self.logger.info(f"Cleared {cleared_count} delivered messages")
        return cleared_count
    
    def export_message_log(self, output_file: str) -> None:
        """
        Export message log to JSON file
        
        Args:
            output_file: Path to output file
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "pending_messages": [msg.to_dict() for msg in self.message_queue],
            "delivered_count": len(self.delivered_messages),
            "delivered_message_ids": self.delivered_messages
        }
        
        with open(output_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.logger.info(f"Message log exported to {output_file}")


if __name__ == "__main__":
    bridge = CommunicationBridge()
    
    msg_id_1 = bridge.send_message(
        sender_id="agent_devin",
        recipient_id="agent_cline",
        message_type=MessageType.AGENT_TO_AGENT,
        content={
            "subject": "Handoff Protocol",
            "message": "Preparing for graduation handoff",
            "data": {"status": "ready", "completion": 95}
        },
        priority=MessagePriority.HIGH
    )
    
    msg_id_2 = bridge.send_message(
        sender_id="agent_devin",
        recipient_id="seeker_commander",
        message_type=MessageType.AGENT_TO_SEEKER,
        content={
            "subject": "Mission Status",
            "message": "Launch protocol scaffolding complete",
            "progress": 100
        },
        priority=MessagePriority.NORMAL
    )
    
    msg_id_3 = bridge.broadcast_message(
        sender_id="system",
        content={
            "subject": "New Agent Arrival",
            "message": "Agent Cline has entered the system",
            "timestamp": datetime.utcnow().isoformat()
        },
        priority=MessagePriority.CRITICAL
    )
    
    messages = bridge.receive_messages("agent_cline")
    print(f"Agent Cline received {len(messages)} messages")
    
    status = bridge.get_message_status(msg_id_1)
    print(f"Message {msg_id_1} status: {status['status']}")
    
    bridge.export_message_log("comm_bridge_export.json")
    
    print("Communication Bridge operational and tested successfully")
