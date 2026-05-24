from intpy.domain.exceptions import TaskNotFoundError, TaskValidationError
from intpy.domain.models import Task, TaskPriority, TaskStatus
from intpy.repository.interface import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str | TaskPriority = TaskPriority.MEDIUM,
    ) -> Task:
        """Creates and saves a new task, returning the created instance."""
        # Convert priority if it is a string
        if isinstance(priority, str):
            priority_enum = TaskPriority.from_str(priority)
        else:
            priority_enum = priority

        next_id = self.repository.get_next_id()
        task = Task(
            id=next_id,
            title=title.strip() if title else "",
            description=description.strip() if description else "",
            status=TaskStatus.TODO,
            priority=priority_enum,
        )
        # Validation before adding
        task.validate()
        self.repository.add(task)
        return task

    def get_task(self, task_id: int) -> Task:
        """Retrieves a single task by its ID. Raises TaskNotFoundError if not found."""
        task = self.repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found.")
        return task

    def list_tasks(
        self,
        status: str | TaskStatus | None = None,
        priority: str | TaskPriority | None = None,
        sort_by: str | None = None,
    ) -> list[Task]:
        """Retrieves and optionally filters/sorts all tasks."""
        tasks = self.repository.get_all()

        # Filtering by status
        if status is not None:
            status_enum = TaskStatus.from_str(status) if isinstance(status, str) else status
            tasks = [t for t in tasks if t.status == status_enum]

        # Filtering by priority
        if priority is not None:
            priority_enum = (
                TaskPriority.from_str(priority) if isinstance(priority, str) else priority
            )
            tasks = [t for t in tasks if t.priority == priority_enum]

        # Sorting
        if sort_by is not None:
            match sort_by.lower().strip():
                case "id":
                    tasks.sort(key=lambda t: t.id)
                case "priority":
                    # Priority order: HIGH (0), MEDIUM (1), LOW (2)
                    priority_order = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
                    tasks.sort(key=lambda t: priority_order.get(t.priority, 3))
                case "status":
                    # Status order: TODO (0), IN_PROGRESS (1), DONE (2)
                    status_order = {TaskStatus.TODO: 0, TaskStatus.IN_PROGRESS: 1, TaskStatus.DONE: 2}
                    tasks.sort(key=lambda t: status_order.get(t.status, 3))
                case "created":
                    tasks.sort(key=lambda t: t.created_at)
                case "updated":
                    tasks.sort(key=lambda t: t.updated_at, reverse=True)
                case _:
                    raise TaskValidationError(
                        f"Invalid sort criterion '{sort_by}'. Available options: id, priority, status, created, updated"
                    )

        return tasks

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        status: str | TaskStatus | None = None,
        priority: str | TaskPriority | None = None,
    ) -> Task:
        """Updates attributes of an existing task by its ID."""
        task = self.get_task(task_id)

        # Map optional string params to actual domain enums
        status_enum = None
        if status is not None:
            status_enum = TaskStatus.from_str(status) if isinstance(status, str) else status

        priority_enum = None
        if priority is not None:
            priority_enum = (
                TaskPriority.from_str(priority) if isinstance(priority, str) else priority
            )

        task.update(
            title=title.strip() if title is not None else None,
            description=description.strip() if description is not None else None,
            status=status_enum,
            priority=priority_enum,
        )
        self.repository.update(task)
        return task

    def complete_task(self, task_id: int) -> Task:
        """Shortcut to mark a task as DONE."""
        return self.update_task(task_id, status=TaskStatus.DONE)

    def start_task(self, task_id: int) -> Task:
        """Shortcut to mark a task as IN_PROGRESS."""
        return self.update_task(task_id, status=TaskStatus.IN_PROGRESS)

    def delete_task(self, task_id: int) -> None:
        """Deletes a task by ID. Raises TaskNotFoundError if task doesn't exist."""
        deleted = self.repository.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"Task with ID {task_id} not found.")
