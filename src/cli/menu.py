"""
CLI Menu - Command-line interface for todo application

Provides menu-driven interaction with numbered options and graceful error handling.
"""

from src.services.todo_service import TodoService
from datetime import datetime


def display_menu(service=None):
    """
    Display the main menu with numbered options.

    Args:
        service (TodoService, optional): Service to check overdue count
    """
    print("\n" + "=" * 30)
    print("===  Todo Application  ===")
    print("=" * 30)

    # Display overdue warning if service provided
    if service:
        overdue_count = service.get_overdue_count()
        if overdue_count > 0:
            print(f"\n! WARNING: You have {overdue_count} overdue task{'s' if overdue_count != 1 else ''}!")

    print("\n1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete/Incomplete")
    print("6. Search/Filter Tasks")
    print("7. Sort Tasks")
    print("8. Filter by Priority")
    print("9. Filter by Tags")
    print("10. View Overdue Tasks")
    print("11. Exit")
    print()


def get_menu_choice():
    """
    Get and validate user menu choice.

    Returns:
        int or None: Valid choice (1-11) or None if invalid
    """
    try:
        choice = input("Enter your choice (1-11): ").strip()
        choice_num = int(choice)
        if 1 <= choice_num <= 11:
            return choice_num
        else:
            print("\nError: Invalid choice. Please enter a number between 1 and 11.")
            return None
    except ValueError:
        print("\n✗ Error: Invalid choice. Please enter a number between 1 and 11.")
        return None


def validate_integer_input(prompt):
    """
    Validate integer input from user.

    Args:
        prompt (str): Input prompt message

    Returns:
        int or None: Valid integer or None if invalid
    """
    try:
        value = input(prompt).strip()
        return int(value)
    except ValueError:
        print("\nError: Invalid task ID. Please enter a number.")
        return None


def validate_priority_input(priority_str):
    """
    Validate and normalize priority input.

    Args:
        priority_str (str): Priority input from user

    Returns:
        str or None: Normalized priority ('high', 'medium', 'low') or None if empty
    """
    priority_str = priority_str.strip().lower()
    if not priority_str:
        return None
    if priority_str in ['high', 'medium', 'low']:
        return priority_str
    print("\nInvalid priority. Must be 'high', 'medium', 'low', or leave empty.")
    return "INVALID"


def parse_tags_input(tags_str):
    """
    Parse comma-separated tags from user input.

    Args:
        tags_str (str): Comma-separated tags

    Returns:
        list: Deduplicated, trimmed tags
    """
    tags_str = tags_str.strip()
    if not tags_str:
        return []

    # Split by comma, trim whitespace, remove empty strings
    tags = [tag.strip() for tag in tags_str.split(',')]
    tags = [tag for tag in tags if tag]  # Filter out empty entries

    # Deduplicate while preserving order
    return list(dict.fromkeys(tags))


def validate_date_input(date_str):
    """
    Validate and parse date input (YYYY-MM-DD format).

    Args:
        date_str (str): Date string from user

    Returns:
        datetime.date, None, or "INVALID": Valid date object, None if empty, or "INVALID" if error
    """
    date_str = date_str.strip()
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("\nInvalid date. Use format: YYYY-MM-DD (example: 2026-01-10)")
        return "INVALID"


def get_filter_choice():
    """
    Get and validate filter choice from user.

    Returns:
        str: 'all', 'pending', or 'completed'
    """
    print("Filter by status:")
    print("  1. All tasks")
    print("  2. Pending only")
    print("  3. Completed only")

    try:
        choice = input("Enter choice (1-3): ").strip()
        choice_num = int(choice)
        if choice_num == 1:
            return "all"
        elif choice_num == 2:
            return "pending"
        elif choice_num == 3:
            return "completed"
        else:
            print("\nError: Invalid choice. Showing all tasks.")
            return "all"
    except ValueError:
        print("\n✗ Error: Invalid choice. Showing all tasks.")
        return "all"


def get_sort_choice():
    """
    Get and validate sort choice from user.

    Returns:
        tuple: (sort_by: str, reverse: bool)
    """
    print("Sort by:")
    print("  1. ID (ascending)")
    print("  2. ID (descending)")
    print("  3. Title (A-Z)")
    print("  4. Title (Z-A)")
    print("  5. Status (completed first)")
    print("  6. Status (pending first)")
    print("  7. Priority (high to low)")
    print("  8. Priority (low to high)")
    print("  9. Due Date (soonest first)")
    print("  10. Due Date (latest first)")

    try:
        choice = input("Enter choice (1-10): ").strip()
        choice_num = int(choice)

        if choice_num == 1:
            return ("id", False)
        elif choice_num == 2:
            return ("id", True)
        elif choice_num == 3:
            return ("title", False)
        elif choice_num == 4:
            return ("title", True)
        elif choice_num == 5:
            return ("status", True)
        elif choice_num == 6:
            return ("status", False)
        elif choice_num == 7:
            return ("priority", True)
        elif choice_num == 8:
            return ("priority", False)
        elif choice_num == 9:
            return ("due_date", False)
        elif choice_num == 10:
            return ("due_date", True)
        else:
            print("\nError: Invalid sort option. Showing tasks in original order.")
            return (None, False)
    except ValueError:
        print("\n✗ Error: Invalid sort option. Showing tasks in original order.")
        return (None, False)


def handle_add_task(service):
    """
    Handle adding a new task.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Add Task ===")
    print("=" * 30)

    title = input("\nEnter task title: ").strip()
    if not title:
        print("\nError: Task title cannot be empty.")
        return

    description = input("Enter task description (optional, press Enter to skip): ").strip()
    if not description:
        description = None

    # Priority input (Feature 003)
    priority = None
    while True:
        priority_input = input("Set priority (high/medium/low, or press Enter to skip): ").strip()
        priority = validate_priority_input(priority_input)
        if priority != "INVALID":
            break

    # Tags input (Feature 003)
    tags_input = input("Add tags (comma-separated, or press Enter to skip): ").strip()
    tags = parse_tags_input(tags_input)

    # Due date input (Feature 003)
    due_date = None
    while True:
        date_input = input("Set due date (YYYY-MM-DD, or press Enter to skip): ").strip()
        due_date = validate_date_input(date_input)
        if due_date != "INVALID":
            break

    # Recurrence input (Feature 003) - only if due date is set
    recurrence = None
    if due_date:
        while True:
            recurrence_input = input("Set recurrence (daily/weekly/monthly, or press Enter to skip): ").strip().lower()
            if not recurrence_input:
                recurrence = None
                break
            if recurrence_input in ['daily', 'weekly', 'monthly']:
                recurrence = recurrence_input
                break
            print("\nInvalid recurrence. Must be 'daily', 'weekly', 'monthly', or leave empty.")

    try:
        task = service.add_task(title, description, priority=priority, tags=tags,
                               due_date=due_date, recurrence=recurrence)
        print("\n[OK] Task added successfully!")
        print(f"  ID: {task.id}")
        print(f"  Title: {task.title}")
        print(f"  Description: {task.description if task.description else 'None'}")
        if task.priority:
            print(f"  Priority: {task.get_priority_display()}")
        if task.tags:
            print(f"  Tags: {', '.join(task.tags)}")
        if task.due_date:
            print(f"  Due: {task.get_due_date_display()}")
        if task.recurrence:
            print(f"  Recurs: {task.recurrence.capitalize()}")
        print(f"  Status: Pending")
    except ValueError as e:
        print(f"\nError: {e}")


def handle_view_tasks(service):
    """
    Handle viewing all tasks.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== All Tasks ===")
    print("=" * 30)
    print()

    tasks = service.get_all_tasks()

    if not tasks:
        print("No tasks found. Add a task to get started!")
        return

    # Display tasks with extended attributes
    for task in tasks:
        status = "Completed" if task.completed else "Pending"

        # Build title with overdue/due today indicators
        title_display = task.title
        if task.is_overdue():
            title_display += f" [OVERDUE {task.days_overdue()} days]"
        elif task.is_due_today():
            title_display += " [DUE TODAY]"

        print(f"ID: {task.id}")
        print(f"  Title: {title_display}")
        if task.description:
            print(f"  Description: {task.description}")

        # Extended attributes display
        attrs = []
        if task.priority:
            attrs.append(f"Priority: {task.get_priority_display()}")
        if task.tags:
            attrs.append(f"Tags: {', '.join(task.tags)}")
        if task.due_date:
            attrs.append(f"Due: {task.get_due_date_display()}")
        if task.recurrence:
            attrs.append(f"Recurs: {task.recurrence.capitalize()}")

        if attrs:
            print(f"  {' | '.join(attrs)}")

        print(f"  Status: {status}")
        print()

    print(f"Total: {len(tasks)} task{'s' if len(tasks) != 1 else ''}")


def handle_update_task(service):
    """
    Handle updating an existing task.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Update Task ===")
    print("=" * 30)
    print()

    task_id = validate_integer_input("Enter task ID to update: ")
    if task_id is None:
        return

    task = service.get_task_by_id(task_id)
    if not task:
        print(f"\nError: Task with ID {task_id} not found.")
        return

    # Show current values
    print(f"\nCurrent title: {task.title}")
    new_title = input("Enter new title (press Enter to keep current): ").strip()

    print(f"Current description: {task.description if task.description else 'None'}")
    new_description = input("Enter new description (press Enter to keep current): ").strip()

    # Priority update
    print(f"Current priority: {task.priority if task.priority else 'None'}")
    new_priority = "KEEP_CURRENT"
    while True:
        priority_input = input("Set priority (high/medium/low/none, or press Enter to keep current): ").strip()
        if not priority_input:
            break
        if priority_input.lower() == 'none':
            new_priority = None
            break
        validated = validate_priority_input(priority_input)
        if validated != "INVALID":
            new_priority = validated
            break

    # Tags update
    print(f"Current tags: {', '.join(task.tags) if task.tags else 'None'}")
    tags_input = input("Set tags (comma-separated, 'none' to clear, or press Enter to keep current): ").strip()
    new_tags = "KEEP_CURRENT"
    if tags_input:
        if tags_input.lower() == 'none':
            new_tags = []
        else:
            new_tags = parse_tags_input(tags_input)

    # Due date update
    print(f"Current due date: {task.get_due_date_display() if task.due_date else 'None'}")
    new_due_date = "KEEP_CURRENT"
    while True:
        date_input = input("Set due date (YYYY-MM-DD, 'none' to clear, or press Enter to keep current): ").strip()
        if not date_input:
            break
        if date_input.lower() == 'none':
            new_due_date = None
            break
        validated_date = validate_date_input(date_input)
        if validated_date != "INVALID":
            new_due_date = validated_date
            break

    # Recurrence update (only if due date is set or will be set)
    new_recurrence = "KEEP_CURRENT"
    has_due_date = task.due_date or (new_due_date not in ["KEEP_CURRENT", None])
    if has_due_date:
        print(f"Current recurrence: {task.recurrence if task.recurrence else 'None'}")
        while True:
            recurrence_input = input("Set recurrence (daily/weekly/monthly/none, or press Enter to keep current): ").strip().lower()
            if not recurrence_input:
                break
            if recurrence_input == 'none':
                new_recurrence = None
                break
            if recurrence_input in ['daily', 'weekly', 'monthly']:
                new_recurrence = recurrence_input
                break
            print("\nInvalid recurrence. Must be 'daily', 'weekly', 'monthly', 'none', or leave empty.")

    # Update only if values provided
    update_title = new_title if new_title else None
    update_description = new_description if new_description else None

    if (update_title is None and update_description is None and
        new_priority == "KEEP_CURRENT" and new_tags == "KEEP_CURRENT" and
        new_due_date == "KEEP_CURRENT" and new_recurrence == "KEEP_CURRENT"):
        print("\nNo changes made.")
        return

    success, message = service.update_task(task_id, update_title, update_description,
                                          new_priority, new_tags, new_due_date, new_recurrence)

    if success:
        print(f"\n[OK] {message}!")
        updated_task = service.get_task_by_id(task_id)
        print(f"  ID: {updated_task.id}")
        print(f"  Title: {updated_task.title}")
        print(f"  Description: {updated_task.description if updated_task.description else 'None'}")

        # Display extended attributes
        attrs = []
        if updated_task.priority:
            attrs.append(f"Priority: {updated_task.get_priority_display()}")
        if updated_task.tags:
            attrs.append(f"Tags: {', '.join(updated_task.tags)}")
        if updated_task.due_date:
            attrs.append(f"Due: {updated_task.get_due_date_display()}")
        if updated_task.recurrence:
            attrs.append(f"Recurs: {updated_task.recurrence.capitalize()}")

        if attrs:
            print(f"  {' | '.join(attrs)}")

        status = "Completed" if updated_task.completed else "Pending"
        print(f"  Status: {status}")
    else:
        print(f"\nError: {message}")


def handle_delete_task(service):
    """
    Handle deleting a task.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Delete Task ===")
    print("=" * 30)
    print()

    task_id = validate_integer_input("Enter task ID to delete: ")
    if task_id is None:
        return

    task = service.get_task_by_id(task_id)
    if not task:
        print(f"\nError: Task with ID {task_id} not found.")
        return

    # Confirm deletion
    confirmation = input(f"\nAre you sure you want to delete task \"{task.title}\"? (y/n): ").strip().lower()

    if confirmation in ['y', 'yes']:
        success, message = service.delete_task(task_id)
        if success:
            print(f"\n[OK] {message}!")
        else:
            print(f"\nError: {message}")
    else:
        print("\nDelete cancelled.")


def handle_toggle_completion(service):
    """
    Handle toggling task completion status.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Mark Task Complete/Incomplete ===")
    print("=" * 30)
    print()

    task_id = validate_integer_input("Enter task ID: ")
    if task_id is None:
        return

    success, message, new_status, new_task = service.toggle_task_completion(task_id)

    if success:
        task = service.get_task_by_id(task_id)
        status_text = "Completed" if new_status else "Pending"
        print(f"\n[OK] Task marked as {status_text.lower()}!")
        print(f"  ID: {task.id}")
        print(f"  Title: {task.title}")
        print(f"  Status: {status_text}")

        # Display recurring task creation message
        if new_task:
            print(f"\n[OK] Creating next occurrence...")
            print(f"  New Task ID: {new_task.id}")
            print(f"  Title: {new_task.title}")
            print(f"  Due: {new_task.get_due_date_display()}")
            print(f"  Recurs: {new_task.recurrence.capitalize()}")
    else:
        print(f"\nError: {message}")


def handle_search_filter_tasks(service):
    """
    Handle searching and filtering tasks.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Search/Filter Tasks ===")
    print("=" * 30)
    print()

    # Get search keyword
    keyword = input("Enter keyword to search (or press Enter to skip): ").strip()
    if not keyword:
        keyword = None

    # Get filter choice
    status_filter = get_filter_choice()

    # Execute combined search and filter
    results = service.search_and_filter(keyword, status_filter)

    # Display results
    if not results:
        if keyword and status_filter != 'all':
            print(f"\nNo tasks found matching '{keyword}' ({status_filter} only).")
        elif keyword:
            print(f"\nNo tasks found matching '{keyword}'.")
        elif status_filter == 'pending':
            print("\nNo pending tasks found.")
        elif status_filter == 'completed':
            print("\nNo completed tasks found.")
        else:
            print("\nNo tasks found. Add a task to get started!")
        return

    # Display header based on what was applied
    if keyword and status_filter != 'all':
        print(f"\nFound {len(results)} task{'s' if len(results) != 1 else ''} matching '{keyword}' ({status_filter} only):\n")
    elif keyword:
        print(f"\nFound {len(results)} task{'s' if len(results) != 1 else ''} matching '{keyword}':\n")
    elif status_filter == 'pending':
        print(f"\nShowing {len(results)} pending task{'s' if len(results) != 1 else ''}:\n")
    elif status_filter == 'completed':
        print(f"\nShowing {len(results)} completed task{'s' if len(results) != 1 else ''}:\n")
    else:
        print(f"\nShowing all {len(results)} task{'s' if len(results) != 1 else ''}:\n")

    # Display table
    print(f"{'ID':<5} | {'Title':<30} | {'Status'}")
    print("-" * 50)

    for task in results:
        status = "Completed" if task.completed else "Pending"
        title_display = task.title[:30] if len(task.title) > 30 else task.title
        print(f"{task.id:<5} | {title_display:<30} | {status}")

    print(f"\nTotal: {len(results)} task{'s' if len(results) != 1 else ''}")


def handle_sort_tasks(service):
    """
    Handle sorting tasks.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("===    Sort Tasks    ===")
    print("=" * 30)
    print()

    # Get sort choice
    sort_by, reverse = get_sort_choice()

    # Execute sort
    if sort_by is None:
        results = service.get_all_tasks()
    else:
        results = service.sort_tasks(sort_by, reverse)

    # Display results
    if not results:
        print("\nNo tasks found. Add a task to get started!")
        return

    # Display header based on sort criteria
    if sort_by == "id":
        direction = "descending" if reverse else "ascending"
        print(f"\nTasks sorted by ID ({direction}):\n")
    elif sort_by == "title":
        direction = "Z-A" if reverse else "A-Z"
        print(f"\nTasks sorted by Title ({direction}):\n")
    elif sort_by == "status":
        direction = "completed first" if reverse else "pending first"
        print(f"\nTasks sorted by Status ({direction}):\n")
    elif sort_by == "priority":
        direction = "high to low" if reverse else "low to high"
        print(f"\nTasks sorted by Priority ({direction}):\n")
    elif sort_by == "due_date":
        direction = "latest first" if reverse else "soonest first"
        print(f"\nTasks sorted by Due Date ({direction}):\n")
    else:
        print("\nShowing tasks in original order:\n")

    # Display table
    print(f"{'ID':<5} | {'Title':<30} | {'Status'}")
    print("-" * 50)

    for task in results:
        status = "Completed" if task.completed else "Pending"
        title_display = task.title[:30] if len(task.title) > 30 else task.title
        print(f"{task.id:<5} | {title_display:<30} | {status}")

    print(f"\nTotal: {len(results)} task{'s' if len(results) != 1 else ''}")


def handle_filter_by_priority(service):
    """
    Handle filtering tasks by priority.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Filter by Priority ===")
    print("=" * 30)
    print()

    print("Select priority level:")
    print("  1. High")
    print("  2. Medium")
    print("  3. Low")

    try:
        choice = input("Enter choice (1-3): ").strip()
        choice_num = int(choice)

        if choice_num == 1:
            priority = 'high'
        elif choice_num == 2:
            priority = 'medium'
        elif choice_num == 3:
            priority = 'low'
        else:
            print("\nError: Invalid choice.")
            return
    except ValueError:
        print("\n✗ Error: Invalid choice.")
        return

    results = service.filter_by_priority(priority)

    if not results:
        print(f"\nNo tasks found with {priority} priority.")
        return

    print(f"\nFound {len(results)} task{'s' if len(results) != 1 else ''} with {priority} priority:\n")

    # Display tasks with full details
    for task in results:
        status = "Completed" if task.completed else "Pending"
        title_display = task.title
        if task.is_overdue():
            title_display += f" [OVERDUE {task.days_overdue()} days]"
        elif task.is_due_today():
            title_display += " [DUE TODAY]"

        print(f"ID: {task.id}")
        print(f"  Title: {title_display}")
        if task.description:
            print(f"  Description: {task.description}")

        attrs = []
        attrs.append(f"Priority: {task.get_priority_display()}")
        if task.tags:
            attrs.append(f"Tags: {', '.join(task.tags)}")
        if task.due_date:
            attrs.append(f"Due: {task.get_due_date_display()}")
        if task.recurrence:
            attrs.append(f"Recurs: {task.recurrence.capitalize()}")

        print(f"  {' | '.join(attrs)}")
        print(f"  Status: {status}")
        print()

    print(f"Total: {len(results)} task{'s' if len(results) != 1 else ''}")


def handle_filter_by_tags(service):
    """
    Handle filtering tasks by tag.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Filter by Tags ===")
    print("=" * 30)
    print()

    tag = input("Enter tag to filter by: ").strip()
    if not tag:
        print("\n✗ Error: Tag cannot be empty.")
        return

    results = service.filter_by_tag(tag)

    if not results:
        print(f"\nNo tasks found with tag '{tag}'.")
        return

    print(f"\nFound {len(results)} task{'s' if len(results) != 1 else ''} with tag '{tag}':\n")

    # Display tasks with full details
    for task in results:
        status = "Completed" if task.completed else "Pending"
        title_display = task.title
        if task.is_overdue():
            title_display += f" [OVERDUE {task.days_overdue()} days]"
        elif task.is_due_today():
            title_display += " [DUE TODAY]"

        print(f"ID: {task.id}")
        print(f"  Title: {title_display}")
        if task.description:
            print(f"  Description: {task.description}")

        attrs = []
        if task.priority:
            attrs.append(f"Priority: {task.get_priority_display()}")
        attrs.append(f"Tags: {', '.join(task.tags)}")
        if task.due_date:
            attrs.append(f"Due: {task.get_due_date_display()}")
        if task.recurrence:
            attrs.append(f"Recurs: {task.recurrence.capitalize()}")

        print(f"  {' | '.join(attrs)}")
        print(f"  Status: {status}")
        print()

    print(f"Total: {len(results)} task{'s' if len(results) != 1 else ''}")


def handle_view_overdue(service):
    """
    Handle viewing overdue tasks.

    Args:
        service (TodoService): Todo service instance
    """
    print("\n" + "=" * 30)
    print("=== Overdue Tasks ===")
    print("=" * 30)
    print()

    results = service.get_overdue_tasks()

    if not results:
        print("No overdue tasks found. Great job staying on top of deadlines!")
        return

    print(f"! WARNING: You have {len(results)} overdue task{'s' if len(results) != 1 else ''}:\n")

    # Display tasks with full details
    for task in results:
        status = "Completed" if task.completed else "Pending"
        days_count = task.days_overdue()
        title_display = f"{task.title} [OVERDUE {days_count} day{'s' if days_count != 1 else ''}]"

        print(f"ID: {task.id}")
        print(f"  Title: {title_display}")
        if task.description:
            print(f"  Description: {task.description}")

        attrs = []
        if task.priority:
            attrs.append(f"Priority: {task.get_priority_display()}")
        if task.tags:
            attrs.append(f"Tags: {', '.join(task.tags)}")
        attrs.append(f"Due: {task.get_due_date_display()}")
        if task.recurrence:
            attrs.append(f"Recurs: {task.recurrence.capitalize()}")

        print(f"  {' | '.join(attrs)}")
        print(f"  Status: {status}")
        print()

    print(f"Total: {len(results)} overdue task{'s' if len(results) != 1 else ''}")


def handle_exit():
    """
    Handle application exit.

    Returns:
        bool: True to signal exit
    """
    print("\nGoodbye! All tasks have been cleared.")
    return True


def run_menu():
    """
    Run the main application menu loop.

    Initializes the service and continuously displays menu until user exits.
    """
    service = TodoService()
    exit_requested = False

    while not exit_requested:
        display_menu(service)
        choice = get_menu_choice()

        if choice is None:
            continue

        if choice == 1:
            handle_add_task(service)
        elif choice == 2:
            handle_view_tasks(service)
        elif choice == 3:
            handle_update_task(service)
        elif choice == 4:
            handle_delete_task(service)
        elif choice == 5:
            handle_toggle_completion(service)
        elif choice == 6:
            handle_search_filter_tasks(service)
        elif choice == 7:
            handle_sort_tasks(service)
        elif choice == 8:
            handle_filter_by_priority(service)
        elif choice == 9:
            handle_filter_by_tags(service)
        elif choice == 10:
            handle_view_overdue(service)
        elif choice == 11:
            exit_requested = handle_exit()
