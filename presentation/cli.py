import argparse
import sys
from pathlib import Path
from intpy.domain.exceptions import TaskError, TaskValidationError
from intpy.domain.models import TaskPriority, TaskStatus
from intpy.presentation.formatter import format_single_task, format_task_table
from intpy.repository.json_repo import JsonTaskRepository
from intpy.service.printer_service import PrinterService
from intpy.service.task_service import TaskService


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TaskHub CLI - A premium console utility to manage your daily tasks.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    # Global database option
    parser.add_argument(
        "--db",
        type=str,
        default="tasks.json",
        help="Path to the JSON database file."
    )

    subparsers = parser.add_subparsers(dest="command", title="commands", required=True)

    # ADD command
    add_parser = subparsers.add_parser("add", help="Add a new task to your task hub.")
    add_parser.add_argument("title", type=str, help="Title of the task (required).")
    add_parser.add_argument(
        "-d", "--desc", "--description",
        dest="description",
        type=str,
        default="",
        help="Optional description of the task."
    )
    add_parser.add_argument(
        "-p", "--priority",
        type=str,
        choices=[p.value for p in TaskPriority],
        default=TaskPriority.MEDIUM.value,
        help="Task priority level."
    )

    # SHOW command
    show_parser = subparsers.add_parser("show", help="Show the list of tasks.")
    show_parser.add_argument(
        "-s", "--status",
        type=str,
        choices=[s.value for s in TaskStatus],
        default=None,
        help="Filter tasks by status."
    )
    show_parser.add_argument(
        "-p", "--priority",
        type=str,
        choices=[p.value for p in TaskPriority],
        default=None,
        help="Filter tasks by priority."
    )
    show_parser.add_argument(
        "--sort",
        type=str,
        choices=["id", "priority", "status", "created", "updated"],
        default="id",
        help="Sort criteria for tasks."
    )

    # EDIT command
    edit_parser = subparsers.add_parser("edit", help="Edit details of an existing task.")
    edit_parser.add_argument("id", type=int, help="Numerical ID of the task.")
    edit_parser.add_argument("-t", "--title", type=str, default=None, help="New title for the task.")
    edit_parser.add_argument("-d", "--desc", "--description", dest="description", type=str, default=None, help="New description.")
    edit_parser.add_argument(
        "-s", "--status",
        type=str,
        choices=[s.value for s in TaskStatus],
        default=None,
        help="New status."
    )
    edit_parser.add_argument(
        "-p", "--priority",
        type=str,
        choices=[p.value for p in TaskPriority],
        default=None,
        help="New priority."
    )

    # COMPLETE command
    complete_parser = subparsers.add_parser("complete", help="Shortcut to mark a task as DONE.")
    complete_parser.add_argument("id", type=int, help="ID of the task to complete.")

    # START command
    start_parser = subparsers.add_parser("start", help="Shortcut to mark a task as IN_PROGRESS.")
    start_parser.add_argument("id", type=int, help="ID of the task to start.")

    # DELETE command
    delete_parser = subparsers.add_parser("delete", help="Delete a task from the hub.")
    delete_parser.add_argument("id", type=int, help="ID of the task to delete.")

    # PRINT command (PDF generation)
    print_parser = subparsers.add_parser("print", help="Generate a PDF report of all tasks.")
    print_parser.add_argument(
        "-o", "--output",
        type=str,
        default="tasks_report.pdf",
        help="Output PDF file path."
    )

    return parser


def run_cli(args_list: list[str] | None = None) -> int:
    """Executes CLI command loop. Returns exit code (0 for success, 1 for failure)."""
    parser = create_parser()
    parsed_args = parser.parse_args(args_list)

    # Bootstrap layers
    try:
        repo = JsonTaskRepository(parsed_args.db)
        service = TaskService(repo)
    except TaskError as e:
        print(f"\033[91mError initializing application:\033[0m {e}", file=sys.stderr)
        return 1

    try:
        # Dispatch command
        match parsed_args.command:
            case "add":
                task = service.create_task(
                    title=parsed_args.title,
                    description=parsed_args.description,
                    priority=parsed_args.priority,
                )
                print(f"\033[92m✔ Task successfully added! \033[0m")
                print(format_single_task(task))

            case "show":
                tasks = service.list_tasks(
                    status=parsed_args.status,
                    priority=parsed_args.priority,
                    sort_by=parsed_args.sort,
                )
                print(format_task_table(tasks))

            case "edit":
                # Ensure at least one update flag was supplied
                if (parsed_args.title is None and parsed_args.description is None and 
                        parsed_args.status is None and parsed_args.priority is None):
                    raise TaskValidationError(
                        "Please specify at least one attribute to update (e.g. --title, --desc, --status, --priority)"
                    )
                task = service.update_task(
                    task_id=parsed_args.id,
                    title=parsed_args.title,
                    description=parsed_args.description,
                    status=parsed_args.status,
                    priority=parsed_args.priority,
                )
                print(f"\033[92m✔ Task #{task.id} successfully updated!\033[0m")
                print(format_single_task(task))

            case "complete":
                task = service.complete_task(parsed_args.id)
                print(f"\033[92m✔ Task #{task.id} completed successfully!\033[0m")
                print(format_single_task(task))

            case "start":
                task = service.start_task(parsed_args.id)
                print(f"\033[92m✔ Task #{task.id} is now in progress!\033[0m")
                print(format_single_task(task))

            case "delete":
                service.delete_task(parsed_args.id)
                print(f"\033[92m✔ Task #{parsed_args.id} deleted successfully.\033[0m")

            case "print":
                printer = PrinterService(service)
                path = printer.generate_pdf(parsed_args.output)
                print(f"\033[92m✔ PDF report saved to: {path}\033[0m")

            case _:
                parser.print_help()
                return 1

        return 0

    except TaskError as e:
        print(f"\033[91m✖ Error:\033[0m {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\033[1;91m✖ Critical System Error:\033[0m {e}", file=sys.stderr)
        return 1
