# Research: Advanced Task Management - Technical Decisions

**Feature**: 003-advanced-task-mgmt
**Created**: 2026-01-04
**Purpose**: Document all technical decisions and rationale for Feature 003 implementation

## Overview

This document captures research findings and technical decisions for implementing advanced task management features (priorities, tags, due dates, recurring tasks) using Python standard library only.

---

## 1. Python datetime Module Usage

### Decision
Use `datetime.date` for due dates (date-only values, no time component).

### Rationale
- **Simplicity**: Date-only tracking (no time-of-day) matches CLI use case
- **Standard library**: No external dependencies required
- **Performance**: Lightweight compared to full datetime objects
- **Comparison**: Built-in operators (<, >, ==) work naturally for overdue detection

### Implementation Details

**Parsing user input (YYYY-MM-DD)**:
```python
from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None  # Invalid date
```

**Overdue detection**:
```python
from datetime import date

def is_overdue(task_due_date):
    return task_due_date < date.today()
```

**Date arithmetic for recurring tasks**:
```python
from datetime import timedelta

new_due_date = current_due_date + timedelta(days=7)  # weekly
```

**Human-readable formatting**:
```python
formatted = due_date.strftime("%b %d, %Y")  # "Jan 10, 2026"
```

### Alternatives Considered
- **Full datetime objects**: Rejected - adds unnecessary time component complexity
- **String storage**: Rejected - requires parsing for every comparison, error-prone
- **Unix timestamps**: Rejected - less readable, requires conversion for display

---

## 2. Date Validation Strategy

### Decision
Two-phase validation: format validation + value validation with clear error messages.

### Rationale
- **User-friendly**: Separate errors for format vs invalid dates (e.g., "2026-13-45")
- **Fail-fast**: Catch errors at input time, not during task operations
- **Clear guidance**: Error messages include examples of valid format

### Implementation Details

**Validation function**:
```python
def validate_date_input(date_str):
    """
    Validate date input from user.

    Returns:
        datetime.date: Valid date object
        None: Empty input (user skipped)
        "INVALID": Format or value error
    """
    date_str = date_str.strip()

    if not date_str:
        return None  # User skipped, optional field

    try:
        # This validates both format and value (e.g., catches Feb 30)
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "INVALID"  # Signal to show error message
```

**Error message template**:
```
"Invalid date. Use format: YYYY-MM-DD (example: 2026-01-10)"
```

### Edge Cases Handled
- **Empty input**: Accepted (due date is optional)
- **Invalid format**: "January 10" → Error with format example
- **Invalid date**: "2026-02-30" → Caught by datetime validation
- **Invalid month/day**: "2026-13-01" → Caught by datetime validation
- **Leap years**: Handled automatically by datetime module

### Alternatives Considered
- **Regex validation**: Rejected - doesn't validate actual date values (can't catch Feb 30)
- **dateutil.parser**: Rejected - external dependency, violates constitution
- **Try multiple formats**: Rejected - adds complexity, spec requires YYYY-MM-DD only

---

## 3. Tag Parsing and Storage

### Decision
Store as list of strings, deduplicate on input, case-sensitive matching.

### Rationale
- **Simplicity**: List comprehension for parsing, `set()` for deduplication
- **Flexibility**: Multiple tags per task, order-independent
- **Performance**: O(n) iteration acceptable for typical tag counts (<10 per task)
- **User control**: Case-sensitive allows "Work" vs "work" distinction

### Implementation Details

**Parsing comma-separated input**:
```python
def parse_tags_input(tags_str):
    """
    Parse comma-separated tags from user input.

    Returns:
        list[str]: Deduplicated, trimmed tags
    """
    tags_str = tags_str.strip()

    if not tags_str:
        return []  # No tags entered

    # Split by comma, trim whitespace, remove empty strings
    tags = [tag.strip() for tag in tags_str.split(',')]
    tags = [tag for tag in tags if tag]  # Filter out empty entries

    # Deduplicate while preserving order (Python 3.7+ dicts maintain insertion order)
    return list(dict.fromkeys(tags))
```

**Tag matching for filtering**:
```python
def has_tag(task, search_tag):
    """Check if task contains the search tag (case-sensitive)."""
    return search_tag in task.tags
```

**Display formatting**:
```python
def format_tags_display(tags):
    """Format tags for display."""
    if not tags:
        return ""
    return " [" + ", ".join(tags) + "]"
```

### Edge Cases Handled
- **Empty input**: Returns empty list
- **Only commas**: ",,," → Empty list after filtering
- **Duplicates**: "work, work, work" → ["work"]
- **Whitespace**: "  work  , home  " → ["work", "home"]
- **Special characters**: Accepted ("project#1", "work@home" valid)
- **Mixed case**: "Work" and "work" treated as different tags

### Alternatives Considered
- **Case-insensitive**: Rejected - reduces user control, requires normalization logic
- **Single tag only**: Rejected - limits categorization capability
- **Predefined tags**: Rejected - adds complexity, reduces flexibility
- **Tag validation**: Rejected - accept all non-empty strings for simplicity

---

## 4. Recurring Task Logic

### Decision
Trigger on task completion, create new instance with day-offset calculation.

### Rationale
- **User control**: Recurring only triggers when user marks task complete
- **Simplicity**: Fixed day offsets (daily: 1, weekly: 7, monthly: 30) avoid calendar complexity
- **Predictable**: No timezone issues, no daylight saving complications
- **Atomic**: Single creation event, no background processing

### Implementation Details

**Day offset mapping**:
```python
RECURRENCE_OFFSETS = {
    'daily': 1,
    'weekly': 7,
    'monthly': 30  # Simple 30-day month approximation
}
```

**Recurring instance creation**:
```python
def create_recurring_instance(original_task, next_id):
    """
    Create new task instance from recurring task.

    Args:
        original_task: Completed task with recurrence pattern
        next_id: ID for new task instance

    Returns:
        Task: New task instance with updated due date
    """
    from datetime import timedelta

    offset = RECURRENCE_OFFSETS[original_task.recurrence]
    new_due_date = original_task.due_date + timedelta(days=offset)

    return Task(
        task_id=next_id,
        title=original_task.title,
        description=original_task.description,
        completed=False,  # New instance starts incomplete
        priority=original_task.priority,
        tags=original_task.tags.copy(),  # Deep copy list
        due_date=new_due_date,
        recurrence=original_task.recurrence
    )
```

**Integration into toggle_completion**:
```python
def toggle_task_completion(self, task_id):
    task = self.get_task_by_id(task_id)

    # Toggle status
    task.completed = not task.completed

    # If completing a recurring task, create next instance
    if task.completed and task.recurrence and task.due_date:
        new_task = self.create_recurring_instance(task, self._next_id)
        self.add_task_object(new_task)  # Add to internal storage

    return task.completed
```

### Edge Cases Handled
- **No due date**: Validation prevents recurrence without due date (enforced in Add/Update handlers)
- **Creation failure**: If add_task_object fails, original task remains complete, error logged
- **Un-completing**: Toggling a completed recurring task back to incomplete does NOT delete the created instance
- **Monthly overflow**: 30-day offset may not align with calendar months (acceptable simplification)

### Alternatives Considered
- **Calendar-aware recurrence**: Rejected - requires dateutil or complex calendar logic
- **Background scheduling**: Rejected - requires persistent storage or daemon process
- **Advanced patterns**: "every 2nd Tuesday" Rejected - scope creep, adds significant complexity
- **Preserve original**: Rejected - original task is complete, new instance is semantically correct approach

---

## 5. Priority/Tag Filtering

### Decision
Use list comprehension for filtering, O(n) iteration acceptable.

### Rationale
- **Performance**: O(n) scan is fast enough for 1000 tasks (<1ms on modern hardware)
- **Simplicity**: One-line list comprehensions, easy to understand and maintain
- **Flexibility**: Easy to combine filters (priority AND tags) if needed later
- **Readability**: Clear, Pythonic code

### Implementation Details

**Filter by priority**:
```python
def filter_by_priority(self, priority):
    """
    Filter tasks by priority level.

    Args:
        priority: 'high', 'medium', 'low', or 'all'

    Returns:
        list[Task]: Tasks matching priority
    """
    if priority == 'all':
        return self._tasks.copy()
    return [task for task in self._tasks if task.priority == priority]
```

**Filter by tag** (match tasks containing the tag):
```python
def filter_by_tag(self, tag):
    """
    Filter tasks containing the specified tag.

    Args:
        tag: Tag to search for

    Returns:
        list[Task]: Tasks containing the tag
    """
    return [task for task in self._tasks if tag in task.tags]
```

**Filter overdue tasks**:
```python
def get_overdue_tasks(self):
    """Get all incomplete tasks with past due dates."""
    return [task for task in self._tasks if task.is_overdue()]
```

### Performance Analysis
- **Time complexity**: O(n) where n = task count
- **Space complexity**: O(k) where k = filtered result count
- **Expected performance**: 1000 tasks × simple comparison = <2ms
- **Worst case**: All tasks match filter → full copy, still acceptable

### Alternatives Considered
- **Indexed filtering**: Rejected - adds complexity, not needed for 1000 tasks
- **Generator expressions**: Considered - but list needed for display, materialization required anyway
- **filter() function**: Considered - list comprehension more Pythonic and readable

---

## 6. Menu Extension Strategy

### Decision
Extend existing menu from 8 options to 11 options, group related features.

### Rationale
- **Usability**: 11 options still scannable, numbered for direct access
- **Grouping**: Related features adjacent (filter/sort/overdue together)
- **Backward compatible**: Existing options unchanged in position
- **Minimal disruption**: Exit option stays at bottom (option 11)

### Proposed Menu Structure

```
==============================
===  Todo Application  ===
==============================

! You have 3 overdue tasks     [Only shown if overdue tasks exist]

1. Add Task                    [EXTENDED: Now prompts for priority, tags, due date, recurrence]
2. View Tasks                  [EXTENDED: Now shows priority, tags, due date, recurrence, overdue indicators]
3. Update Task                 [EXTENDED: Can update priority, tags, due date, recurrence]
4. Delete Task                 [UNCHANGED]
5. Mark Task Complete/Incomplete [EXTENDED: Triggers recurring task creation if applicable]
6. Search/Filter Tasks         [UNCHANGED: Feature 002]
7. Sort Tasks                  [EXTENDED: Add priority and due date sort options]
8. Filter by Priority          [NEW]
9. Filter by Tags              [NEW]
10. View Overdue Tasks         [NEW]
11. Exit                       [MOVED from option 8]
```

### Menu Flow Design

**Option 8 - Filter by Priority**:
1. Prompt: "Filter by priority (high/medium/low/all): "
2. Validate input
3. Display filtered tasks in table format
4. Return to main menu

**Option 9 - Filter by Tags**:
1. Prompt: "Enter tag to filter by: "
2. Search for tasks containing tag
3. Display matching tasks in table format
4. Show "No tasks with tag '[tag]'" if empty
5. Return to main menu

**Option 10 - View Overdue Tasks**:
1. Get all overdue tasks
2. Display with "[OVERDUE]" indicator and days overdue
3. Show "No overdue tasks. Great job staying on track!" if empty
4. Return to main menu

### Implementation Impact

**menu.py changes**:
```python
def get_menu_choice():
    """Validate user menu choice (now 1-11 instead of 1-8)."""
    # Update validation range
    if 1 <= choice_num <= 11:
        return choice_num
```

**Option routing**:
```python
def run_menu():
    # ... existing routing ...
    elif choice == 8:
        handle_filter_by_priority(service)
    elif choice == 9:
        handle_filter_by_tags(service)
    elif choice == 10:
        handle_view_overdue(service)
    elif choice == 11:
        exit_requested = handle_exit()
```

### Alternatives Considered
- **Submenus**: Rejected - adds navigation complexity, breaks CLI simplicity
- **Combine filters**: Rejected - separate options clearer for independent features
- **Fewer options**: Rejected - each feature deserves dedicated access for usability
- **More options**: Rejected - 11 is already approaching cognitive limit, avoid overload

---

## 7. Backward Compatibility Strategy

### Decision
All extended attributes optional with safe defaults, existing code paths unchanged.

### Rationale
- **Zero-impact**: Existing tasks continue to work without modification
- **Graceful defaults**: None/empty values handled transparently
- **Display logic**: Extended attributes only shown when present
- **API compatibility**: Existing service methods unchanged in behavior

### Implementation Details

**Task initialization with defaults**:
```python
class Task:
    def __init__(self, task_id, title, description=None, completed=False,
                 priority=None, tags=None, due_date=None, recurrence=None):
        # Core attributes (unchanged)
        self._id = task_id
        self.title = title
        self.description = description
        self.completed = completed

        # Extended attributes (default to None/empty)
        self.priority = priority  # None if not set
        self.tags = tags if tags is not None else []  # Empty list if not set
        self.due_date = due_date  # None if not set
        self.recurrence = recurrence  # None if not set
```

**Safe display logic**:
```python
def display_task(task):
    # Always show core info
    print(f"{task.id}: {task.title}")

    # Only show extended info if present
    if task.priority:
        print(f"  Priority: [{task.priority.upper()}]")
    if task.tags:
        print(f"  Tags: {', '.join(task.tags)}")
    if task.due_date:
        print(f"  Due: {task.due_date.strftime('%b %d, %Y')}")
    if task.recurrence:
        print(f"  Recurs: {task.recurrence.capitalize()}")
```

**Existing tasks work unchanged**:
- Tasks created before Feature 003: All extended attributes None/empty
- View operations: Skip extended attribute display (None/empty values)
- Update operations: Can add extended attributes to old tasks
- Filter/sort: Tasks without attributes handled gracefully (None sorts to end)

### Validation

**Test scenario**:
1. Load application with tasks from Phase I (no extended attributes)
2. Verify all tasks display correctly (no errors, no None/empty labels)
3. Add new task with extended attributes
4. Verify both old and new tasks coexist
5. Update old task to add extended attributes
6. Verify gradual migration works

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Date handling** | datetime.date, YYYY-MM-DD format | Simple, standard library, sufficient for CLI use case |
| **Date validation** | Two-phase: format + value with clear errors | User-friendly, catches all invalid dates |
| **Tag storage** | List of strings, deduplicated, case-sensitive | Simple, flexible, performant |
| **Recurring logic** | Trigger on completion, day-offset calculation | User-controlled, predictable, no background processing |
| **Filtering** | List comprehension, O(n) iteration | Simple, performant for 1000 tasks, Pythonic |
| **Menu structure** | 11 options total, grouped by feature type | Scannable, logical grouping, Exit stays at bottom |
| **Backward compat** | Optional attributes, safe defaults | Zero-impact on existing tasks, graceful migration |

## Constitutional Compliance

All decisions comply with Phase I constitution v1.2.0:
- ✅ Python standard library only (datetime module)
- ✅ No external dependencies
- ✅ In-memory storage (no persistence)
- ✅ CLI only (no GUI/web)
- ✅ Simple, readable code
- ✅ Maintains three-layer architecture

---

**Research Complete**: All technical decisions documented and justified.
**Next Phase**: Generate data-model.md, contracts/cli-interface.md, quickstart.md (Phase 1)
