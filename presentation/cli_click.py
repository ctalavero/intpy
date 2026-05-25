"""
Click-based CLI interface for TaskHub.

Usage:
    python -m intpy.presentation.cli_click [OPTIONS] COMMAND [ARGS]
"""
import sys
from pathlib import Path

import click

from intpy.domain.exceptions import TaskError
from intpy.presentation.formatter import format_single_task, format_task_table
from intpy.repository.json_repo import JsonTaskRepository
from intpy.service.printer_service import PrinterService
from intpy.service.task_service import TaskService


def _get_service(db: str) -> TaskService:
    return TaskService(JsonTaskRepository(db))


@click.group()
@click.option("--db", default="tasks.json", help="Path to the JSON database file.")
@click.pass_context
def cli(ctx, db: str):
    """TaskHub CLI — manage your tasks from the terminal (Click edition)."""
    ctx.ensure_object(dict)
    ctx.obj["db"] = db


@cli.command()
@click.argument("title")
@click.option("-d", "--desc", default="", help="Task description.")
@click.option("-p", "--priority", type=click.Choice(["LOW", "MEDIUM", "HIGH"], case_sensitive=False), default="MEDIUM")
@click.pass_context
def add(ctx, title: str, desc: str, priority: str):
    """Add a new task."""
    service = _get_service(ctx.obj["db"])
    try:
        task = service.create_task(title=title, description=desc, priority=priority)
        click.secho(f"✔ Task #{task.id} created!", fg="green", bold=True)
        click.echo(format_single_task(task))
    except TaskError as e:
        click.secho(f"✖ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.option("-s", "--status", type=click.Choice(["TODO", "IN_PROGRESS", "DONE"], case_sensitive=False), default=None)
@click.option("-p", "--priority", type=click.Choice(["LOW", "MEDIUM", "HIGH"], case_sensitive=False), default=None)
@click.option("--sort", type=click.Choice(["id", "priority", "status", "created", "updated"]), default="id")
@click.pass_context
def show(ctx, status, priority, sort):
    """Show all tasks."""
    service = _get_service(ctx.obj["db"])
    try:
        tasks = service.list_tasks(status=status, priority=priority, sort_by=sort)
        click.echo(format_task_table(tasks))
    except TaskError as e:
        click.secho(f"✖ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("task_id", type=int)
@click.option("-t", "--title", default=None)
@click.option("-d", "--desc", default=None)
@click.option("-s", "--status", type=click.Choice(["TODO", "IN_PROGRESS", "DONE"], case_sensitive=False), default=None)
@click.option("-p", "--priority", type=click.Choice(["LOW", "MEDIUM", "HIGH"], case_sensitive=False), default=None)
@click.pass_context
def edit(ctx, task_id: int, title, desc, status, priority):
    """Edit an existing task by ID."""
    service = _get_service(ctx.obj["db"])
    try:
        task = service.update_task(task_id, title=title, description=desc, status=status, priority=priority)
        click.secho(f"✔ Task #{task.id} updated!", fg="green", bold=True)
        click.echo(format_single_task(task))
    except TaskError as e:
        click.secho(f"✖ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("task_id", type=int)
@click.pass_context
def start(ctx, task_id: int):
    """Mark a task as IN_PROGRESS."""
    service = _get_service(ctx.obj["db"])
    try:
        task = service.start_task(task_id)
        click.secho(f"✔ Task #{task.id} is now IN_PROGRESS!", fg="green", bold=True)
    except TaskError as e:
        click.secho(f"✖ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("task_id", type=int)
@click.pass_context
def complete(ctx, task_id: int):
    """Mark a task as DONE."""
    service = _get_service(ctx.obj["db"])
    try:
        task = service.complete_task(task_id)
        click.secho(f"✔ Task #{task.id} completed!", fg="green", bold=True)
    except TaskError as e:
        click.secho(f"✖ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("task_id", type=int)
@click.pass_context
def delete(ctx, task_id: int):
    """Delete a task by ID."""
    service = _get_service(ctx.obj["db"])
    try:
        service.delete_task(task_id)
        click.secho(f"✔ Task #{task_id} deleted!", fg="green", bold=True)
    except TaskError as e:
        click.secho(f"✖ Error: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command(name="print")
@click.option("-o", "--output", default="tasks_report.pdf", help="Output PDF file path.")
@click.pass_context
def print_cmd(ctx, output: str):
    """Generate a PDF report of all tasks."""
    service = _get_service(ctx.obj["db"])
    printer = PrinterService(service)
    try:
        path = printer.generate_pdf(output)
        click.secho(f"✔ PDF saved to: {path}", fg="green", bold=True)
    except Exception as e:
        click.secho(f"✖ Error generating PDF: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
