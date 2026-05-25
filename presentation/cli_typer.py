"""
Typer-based CLI interface for TaskHub.

Usage:
    python -m intpy.presentation.cli_typer [OPTIONS] COMMAND [ARGS]
"""
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer

from intpy.domain.exceptions import TaskError
from intpy.presentation.formatter import format_single_task, format_task_table
from intpy.repository.json_repo import JsonTaskRepository
from intpy.service.printer_service import PrinterService
from intpy.service.task_service import TaskService


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Status(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class SortBy(str, Enum):
    id = "id"
    priority = "priority"
    status = "status"
    created = "created"
    updated = "updated"


app = typer.Typer(
    name="taskhub",
    help="TaskHub CLI — manage your tasks from the terminal (Typer edition).",
    add_completion=False,
)

DB_OPTION = typer.Option("tasks.json", help="Path to the JSON database file.")


def _get_service(db: str) -> TaskService:
    return TaskService(JsonTaskRepository(db))


@app.command()
def add(
    title: str,
    desc: Annotated[str, typer.Option("-d", "--desc", help="Task description.")] = "",
    priority: Annotated[Priority, typer.Option("-p", "--priority")] = Priority.MEDIUM,
    db: str = DB_OPTION,
):
    """Add a new task."""
    service = _get_service(db)
    try:
        task = service.create_task(title=title, description=desc, priority=priority.value)
        typer.secho(f"✔ Task #{task.id} created!", fg=typer.colors.GREEN, bold=True)
        typer.echo(format_single_task(task))
    except TaskError as e:
        typer.secho(f"✖ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def show(
    status: Annotated[Optional[Status], typer.Option("-s", "--status")] = None,
    priority: Annotated[Optional[Priority], typer.Option("-p", "--priority")] = None,
    sort: Annotated[SortBy, typer.Option("--sort")] = SortBy.id,
    db: str = DB_OPTION,
):
    """Show all tasks."""
    service = _get_service(db)
    try:
        tasks = service.list_tasks(
            status=status.value if status else None,
            priority=priority.value if priority else None,
            sort_by=sort.value,
        )
        typer.echo(format_task_table(tasks))
    except TaskError as e:
        typer.secho(f"✖ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def edit(
    task_id: int,
    title: Annotated[Optional[str], typer.Option("-t", "--title")] = None,
    desc: Annotated[Optional[str], typer.Option("-d", "--desc")] = None,
    status: Annotated[Optional[Status], typer.Option("-s", "--status")] = None,
    priority: Annotated[Optional[Priority], typer.Option("-p", "--priority")] = None,
    db: str = DB_OPTION,
):
    """Edit an existing task by ID."""
    service = _get_service(db)
    try:
        task = service.update_task(
            task_id,
            title=title,
            description=desc,
            status=status.value if status else None,
            priority=priority.value if priority else None,
        )
        typer.secho(f"✔ Task #{task.id} updated!", fg=typer.colors.GREEN, bold=True)
        typer.echo(format_single_task(task))
    except TaskError as e:
        typer.secho(f"✖ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def start(
    task_id: int,
    db: str = DB_OPTION,
):
    """Mark a task as IN_PROGRESS."""
    service = _get_service(db)
    try:
        task = service.start_task(task_id)
        typer.secho(f"✔ Task #{task.id} is now IN_PROGRESS!", fg=typer.colors.GREEN, bold=True)
    except TaskError as e:
        typer.secho(f"✖ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def complete(
    task_id: int,
    db: str = DB_OPTION,
):
    """Mark a task as DONE."""
    service = _get_service(db)
    try:
        task = service.complete_task(task_id)
        typer.secho(f"✔ Task #{task.id} completed!", fg=typer.colors.GREEN, bold=True)
    except TaskError as e:
        typer.secho(f"✖ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    task_id: int,
    db: str = DB_OPTION,
):
    """Delete a task by ID."""
    service = _get_service(db)
    try:
        service.delete_task(task_id)
        typer.secho(f"✔ Task #{task_id} deleted!", fg=typer.colors.GREEN, bold=True)
    except TaskError as e:
        typer.secho(f"✖ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command(name="print")
def print_cmd(
    output: Annotated[str, typer.Option("-o", "--output", help="Output PDF path.")] = "tasks_report.pdf",
    db: str = DB_OPTION,
):
    """Generate a PDF report of all tasks."""
    service = _get_service(db)
    printer = PrinterService(service)
    try:
        path = printer.generate_pdf(output)
        typer.secho(f"✔ PDF saved to: {path}", fg=typer.colors.GREEN, bold=True)
    except Exception as e:
        typer.secho(f"✖ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
