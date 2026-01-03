from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class TaskState(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: str
    entity_id: str
    type: str
    state: TaskState
    assigned_to: Optional[str] = None
    data: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "type": self.type,
            "state": self.state.value,
            "assigned_to": self.assigned_to,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
