import json
from pathlib import Path
from intpy.domain.exceptions import TaskValidationError
from intpy.domain.models import Task
from intpy.repository.interface import TaskRepository


class JsonTaskRepository(TaskRepository):
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensures that the JSON file and its parent directories exist."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_raw({"tasks": [], "next_id": 1})

    def _load_raw(self) -> dict:
        """Loads raw dictionary data from the JSON file with corruption validation."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict) or "tasks" not in data or "next_id" not in data:
                    raise TaskValidationError("Invalid tasks database format.")
                return data
        except json.JSONDecodeError as e:
            raise TaskValidationError(f"Database file is corrupted: {e}")
        except FileNotFoundError:
            self._ensure_file_exists()
            return {"tasks": [], "next_id": 1}

    def _save_raw(self, data: dict) -> None:
        """Atomically saves raw dictionary data using a temporary file to prevent corruption."""
        temp_file = self.file_path.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            # Atomic replace (guaranteed on POSIX/Linux)
            temp_file.replace(self.file_path)
        except Exception as e:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError:
                    pass
            raise TaskValidationError(f"Failed to write to tasks database: {e}")

    def get_all(self) -> list[Task]:
        data = self._load_raw()
        return [Task.from_dict(item) for item in data["tasks"]]

    def get_by_id(self, task_id: int) -> Task | None:
        tasks = self.get_all()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def add(self, task: Task) -> None:
        data = self._load_raw()
        # Verify the ID is set correctly
        tasks = [Task.from_dict(item) for item in data["tasks"]]
        if any(t.id == task.id for t in tasks):
            raise TaskValidationError(f"Task with ID {task.id} already exists.")
        
        data["tasks"].append(task.to_dict())
        # Update the next_id if this added ID is greater than or equal to next_id
        if task.id >= data["next_id"]:
            data["next_id"] = task.id + 1
            
        self._save_raw(data)

    def update(self, task: Task) -> None:
        data = self._load_raw()
        updated = False
        new_tasks = []
        for item in data["tasks"]:
            if item["id"] == task.id:
                new_tasks.append(task.to_dict())
                updated = True
            else:
                new_tasks.append(item)
        
        if not updated:
            raise TaskValidationError(f"Task with ID {task.id} does not exist in database.")
        
        data["tasks"] = new_tasks
        self._save_raw(data)

    def delete(self, task_id: int) -> bool:
        data = self._load_raw()
        initial_count = len(data["tasks"])
        data["tasks"] = [item for item in data["tasks"] if item["id"] != task_id]
        deleted = len(data["tasks"]) < initial_count
        if deleted:
            self._save_raw(data)
        return deleted

    def get_next_id(self) -> int:
        data = self._load_raw()
        next_id = data["next_id"]
        # Double check that next_id isn't occupied, if so auto-increment beyond max
        tasks = data["tasks"]
        if tasks:
            existing_ids = {t["id"] for t in tasks}
            while next_id in existing_ids:
                next_id += 1
        return next_id
