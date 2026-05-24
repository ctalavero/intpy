class TaskError(Exception):
    """Base exception for all TaskHub CLI errors."""
    pass


class TaskValidationError(TaskError):
    """Exception raised when task validation fails (e.g. empty title, invalid status)."""
    pass


class TaskNotFoundError(TaskError):
    """Exception raised when a requested task cannot be found by ID."""
    pass
