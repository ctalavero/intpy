from abc import ABC, abstractmethod
from intpy.domain.models import Task


class TaskRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Task]:
        """Retrieve all tasks."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Task | None:
        """Retrieve task by ID."""
        pass

    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a new task."""
        pass

    @abstractmethod
    def update(self, task: Task) -> None:
        """Update an existing task."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete task by ID. Return True if deleted, False otherwise."""
        pass

    @abstractmethod
    def get_next_id(self) -> int:
        """Get the next auto-incrementing ID."""
        pass
