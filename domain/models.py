from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from intpy.domain.exceptions import TaskValidationError


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

    @classmethod
    def from_str(cls, value: str) -> "TaskStatus":
        normalized = value.upper().strip().replace(" ", "_").replace("-", "_")
        try:
            return cls(normalized)
        except ValueError:
            # Try to lookup by attribute name
            try:
                return cls[normalized]
            except KeyError:
                valid_options = ", ".join([status.value for status in cls])
                raise TaskValidationError(
                    f"Invalid status '{value}'. Available options are: {valid_options}"
                )


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @classmethod
    def from_str(cls, value: str) -> "TaskPriority":
        normalized = value.upper().strip()
        try:
            return cls(normalized)
        except ValueError:
            try:
                return cls[normalized]
            except KeyError:
                valid_options = ", ".join([priority.value for priority in cls])
                raise TaskValidationError(
                    f"Invalid priority '{value}'. Available options are: {valid_options}"
                )


@dataclass(slots=True)
class Task:
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> None:
        """Performs domain-level validations."""
        if not self.title or not self.title.strip():
            raise TaskValidationError("Task title cannot be empty.")
        if len(self.title) > 100:
            raise TaskValidationError("Task title cannot exceed 100 characters.")
        if len(self.description) > 500:
            raise TaskValidationError("Task description cannot exceed 500 characters.")

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> None:
        """Updates task state, validating modifications."""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if status is not None:
            self.status = status
        if priority is not None:
            self.priority = priority
        self.validate()
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        try:
            return cls(
                id=data["id"],
                title=data["title"],
                description=data["description"],
                status=TaskStatus(data["status"]),
                priority=TaskPriority(data["priority"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )
        except (KeyError, ValueError) as e:
            raise TaskValidationError(f"Failed to deserialize Task from dict: {e}")
