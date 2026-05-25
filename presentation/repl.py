"""
REPL (Read-Eval-Print Loop) interface for TaskHub.

Interactive command shell with support for:
add, show, edit, delete, start, complete, print, help, exit.
"""
import sys
from pathlib import Path

from intpy.domain.exceptions import TaskError
from intpy.domain.models import TaskPriority, TaskStatus
from intpy.presentation.formatter import format_single_task, format_task_table
from intpy.repository.json_repo import JsonTaskRepository
from intpy.service.printer_service import PrinterService
from intpy.service.task_service import TaskService

HELP_TEXT = """
Available commands:
  add <title> [--desc <description>] [--priority LOW|MEDIUM|HIGH]
  show [--status TODO|IN_PROGRESS|DONE] [--sort id|priority|status]
  edit <id> [--title <title>] [--desc <desc>] [--status <status>] [--priority <priority>]
  start <id>
  complete <id>
  delete <id>
  print [<output_path>]    — Generate PDF report (default: tasks_report.pdf)
  help                     — Show this help
  exit / quit              — Exit REPL
"""

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _parse_args(raw: str) -> list[str]:
    """Simple argument parser that handles quoted strings."""
    tokens = []
    current = []
    in_quote = None
    for ch in raw:
        if ch in ('"', "'") and in_quote is None:
            in_quote = ch
        elif ch == in_quote:
            in_quote = None
        elif ch == " " and in_quote is None:
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def _get_flag(args: list[str], *flags: str) -> str | None:
    """Extract value for a flag like --desc or --priority from arg list."""
    for flag in flags:
        if flag in args:
            idx = args.index(flag)
            if idx + 1 < len(args):
                val = args[idx + 1]
                args.pop(idx)  # remove flag
                args.pop(idx)  # remove value
                return val
    return None


def run_repl(db_path: str = "tasks.json") -> None:
    """Launch the interactive REPL."""
    repo = JsonTaskRepository(db_path)
    service = TaskService(repo)
    printer = PrinterService(service)

    print(f"\n{BOLD}{CYAN}TaskHub REPL{RESET} — interactive task manager")
    print(f"Type {BOLD}help{RESET} for available commands.\n")

    while True:
        try:
            raw_input = input(f"{CYAN}taskhub>{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not raw_input:
            continue

        args = _parse_args(raw_input)
        command = args[0].lower()
        rest = args[1:]

        try:
            if command in ("exit", "quit"):
                print("Bye!")
                break

            elif command == "help":
                print(HELP_TEXT)

            elif command == "add":
                if not rest:
                    print(f"{RED}Usage: add <title> [--desc ...] [--priority ...]{RESET}")
                    continue
                desc = _get_flag(rest, "--desc", "-d") or ""
                prio = _get_flag(rest, "--priority", "-p") or "MEDIUM"
                title = " ".join(rest)
                task = service.create_task(title=title, description=desc, priority=prio)
                print(f"{GREEN}✔ Task #{task.id} created!{RESET}")
                print(format_single_task(task))

            elif command == "show":
                status = _get_flag(rest, "--status", "-s")
                sort_by = _get_flag(rest, "--sort") or "id"
                tasks = service.list_tasks(status=status, sort_by=sort_by)
                print(format_task_table(tasks))

            elif command == "edit":
                if not rest:
                    print(f"{RED}Usage: edit <id> [--title ...] [--desc ...] [--status ...] [--priority ...]{RESET}")
                    continue
                task_id = int(rest.pop(0))
                title = _get_flag(rest, "--title", "-t")
                desc = _get_flag(rest, "--desc", "-d")
                status = _get_flag(rest, "--status", "-s")
                prio = _get_flag(rest, "--priority", "-p")
                task = service.update_task(task_id, title=title, description=desc, status=status, priority=prio)
                print(f"{GREEN}✔ Task #{task.id} updated!{RESET}")
                print(format_single_task(task))

            elif command == "start":
                if not rest:
                    print(f"{RED}Usage: start <id>{RESET}")
                    continue
                task = service.start_task(int(rest[0]))
                print(f"{GREEN}✔ Task #{task.id} is now IN_PROGRESS!{RESET}")

            elif command == "complete":
                if not rest:
                    print(f"{RED}Usage: complete <id>{RESET}")
                    continue
                task = service.complete_task(int(rest[0]))
                print(f"{GREEN}✔ Task #{task.id} completed!{RESET}")

            elif command == "delete":
                if not rest:
                    print(f"{RED}Usage: delete <id>{RESET}")
                    continue
                service.delete_task(int(rest[0]))
                print(f"{GREEN}✔ Task #{rest[0]} deleted!{RESET}")

            elif command == "print":
                output = rest[0] if rest else "tasks_report.pdf"
                path = printer.generate_pdf(output)
                print(f"{GREEN}✔ PDF saved to: {path}{RESET}")

            else:
                print(f"{RED}Unknown command: '{command}'. Type 'help' for a list of commands.{RESET}")

        except TaskError as e:
            print(f"{RED}✖ Error: {e}{RESET}")
        except ValueError as e:
            print(f"{RED}✖ Invalid input: {e}{RESET}")
        except Exception as e:
            print(f"{RED}✖ Unexpected error: {e}{RESET}")


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "tasks.json"
    run_repl(db)
