from datetime import datetime
from intpy.domain.models import Task, TaskPriority, TaskStatus

# ANSI escape codes for colors
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Foreground colors
COLOR_ID = "\033[36m"         # Cyan
COLOR_TITLE = "\033[37m"      # White
COLOR_DESC = "\033[90m"       # Gray
COLOR_TIME = "\033[94m"       # Light Blue

COLOR_PRIO_HIGH = "\033[1;91m"    # Bold Red
COLOR_PRIO_MED = "\033[1;93m"     # Bold Yellow
COLOR_PRIO_LOW = "\033[1;94m"     # Bold Blue

COLOR_STATUS_TODO = "\033[90m"    # Gray
COLOR_STATUS_PROGRESS = "\033[93m"# Yellow
COLOR_STATUS_DONE = "\033[92m"    # Green


def _get_status_colored(status: TaskStatus) -> str:
    color = COLOR_STATUS_TODO
    if status == TaskStatus.IN_PROGRESS:
        color = COLOR_STATUS_PROGRESS
    elif status == TaskStatus.DONE:
        color = COLOR_STATUS_DONE
    return f"{color}{status.value:^11}{RESET}"


def _get_priority_colored(priority: TaskPriority) -> str:
    color = COLOR_PRIO_LOW
    if priority == TaskPriority.MEDIUM:
        color = COLOR_PRIO_MED
    elif priority == TaskPriority.HIGH:
        color = COLOR_PRIO_HIGH
    return f"{color}{priority.value:^8}{RESET}"


def truncate_text(text: str, max_len: int) -> str:
    """Safely truncates text to fit within column limits, replacing overflow with ellipses."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def format_task_table(tasks: list[Task]) -> str:
    """Generates a beautifully styled Unicode table containing tasks."""
    if not tasks:
        return f"\n{BOLD}{COLOR_PRIO_HIGH}No tasks found.{RESET}\n"

    # Define column configurations (header, width)
    # Total table width will be sum of widths + borders
    cols = [
        {"name": "ID", "width": 5},
        {"name": "Title", "width": 25},
        {"name": "Description", "width": 30},
        {"name": "Priority", "width": 10},
        {"name": "Status", "width": 13},
        {"name": "Created At", "width": 21},
    ]

    # Border definitions
    top_left, top_right, top_mid = "┌", "┐", "┬"
    mid_left, mid_right, mid_mid = "├", "┤", "┼"
    bot_left, bot_right, bot_mid = "└", "┘", "┴"
    horiz, vert = "─", "│"

    # Helper to generate horizontal line separators
    def get_sep_line(left: str, mid: str, right: str) -> str:
        parts = [horiz * (c["width"] + 2) for c in cols]
        return f"{left}{mid.join(parts)}{right}"

    lines = []

    # 1. Top border
    lines.append(get_sep_line(top_left, top_mid, top_right))

    # 2. Table Header
    header_parts = []
    for c in cols:
        header_text = f"{c['name']:^{c['width']}}"
        header_parts.append(f" {BOLD}{header_text}{RESET} ")
    lines.append(f"{vert}{vert.join(header_parts)}{vert}")

    # 3. Middle separator
    lines.append(get_sep_line(mid_left, mid_mid, mid_right))

    # 4. Data Rows
    for task in tasks:
        id_str = f"{COLOR_ID}{task.id:^{cols[0]['width']}}{RESET}"
        
        # Truncate and pad text contents
        title_trunc = truncate_text(task.title, cols[1]["width"])
        title_str = f"{COLOR_TITLE}{title_trunc:<{cols[1]['width']}}{RESET}"
        
        desc_trunc = truncate_text(task.description, cols[2]["width"]) if task.description else "---"
        desc_str = f"{COLOR_DESC}{desc_trunc:<{cols[2]['width']}}{RESET}"

        prio_str = f" {_get_priority_colored(task.priority)} "
        status_str = f" {_get_status_colored(task.status)} "

        time_formatted = task.created_at.strftime("%Y-%m-%d %H:%M:%S")
        time_str = f"{COLOR_TIME}{time_formatted:^{cols[5]['width']}}{RESET}"

        row_parts = [
            f" {id_str} ",
            f" {title_str} ",
            f" {desc_str} ",
            prio_str,
            status_str,
            f" {time_str} "
        ]
        lines.append(f"{vert}{vert.join(row_parts)}{vert}")

    # 5. Bottom border
    lines.append(get_sep_line(bot_left, bot_mid, bot_right))

    return "\n" + "\n".join(lines) + "\n"


def format_single_task(task: Task) -> str:
    """Generates a detailed key-value visualization of a single task."""
    prio_color = COLOR_PRIO_LOW
    if task.priority == TaskPriority.MEDIUM:
        prio_color = COLOR_PRIO_MED
    elif task.priority == TaskPriority.HIGH:
        prio_color = COLOR_PRIO_HIGH

    status_color = COLOR_STATUS_TODO
    if task.status == TaskStatus.IN_PROGRESS:
        status_color = COLOR_STATUS_PROGRESS
    elif task.status == TaskStatus.DONE:
        status_color = COLOR_STATUS_DONE

    return f"""
{BOLD}{COLOR_ID}Task #{task.id}{RESET}
{BOLD}Title:{RESET}       {task.title}
{BOLD}Description:{RESET} {task.description or '---'}
{BOLD}Priority:{RESET}    {prio_color}{task.priority.value}{RESET}
{BOLD}Status:{RESET}      {status_color}{task.status.value}{RESET}
{BOLD}Created At:{RESET}  {COLOR_TIME}{task.created_at.strftime('%Y-%m-%d %H:%M:%S')}{RESET}
{BOLD}Updated At:{RESET}  {COLOR_TIME}{task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}{RESET}
"""
