# Data Model: Advanced Task Management

**Feature**: 003-advanced-task-mgmt
**Created**: 2026-01-04
**Purpose**: Define extended Task entity with priorities, tags, due dates, and recurrence

## Overview

This document defines the extended Task entity for Feature 003. The Task model is enhanced with four new optional attributes while maintaining full backward compatibility with existing Phase I tasks.

---

## Task Entity

### Core Attributes (Unchanged from Phase I)

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | int | Yes | Auto-increment | Unique, immutable, positive | Task identifier |
| `title` | str | Yes | None | Non-empty after trim | Task name |
| `description` | str \| None | No | None | Any string or None | Detailed task information |
| `completed` | bool | Yes | False | True \| False | Completion status |

### Extended Attributes (Feature 003)

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `priority` | str \| None | No | None | 'high', 'medium', 'low', or None | Task urgency level |
| `tags` | list[str] | No | [] | List of non-empty strings | Task categories/labels |
| `due_date` | datetime.date \| None | No | None | Valid date or None | Task deadline |
| `recurrence` | str \| None | No | None | 'daily', 'weekly', 'monthly', or None | Repetition pattern |

---

## Validation Rules

### Priority Validation

**Constraint**: Must be one of: `'high'`, `'medium'`, `'low'`, or `None`

```python
def validate_priority(priority):
    """Validate priority value."""
    if priority is None:
        return True
    return priority in ['high', 'medium', 'low']
```

**Error handling**: Reject invalid values with error message:
```
"Invalid priority. Must be 'high', 'medium', 'low', or leave empty."
```

### Tags Validation

**Constraint**: Must be list of non-empty strings (empty list allowed)

```python
def validate_tags(tags):
    """Validate tags list."""
    if not isinstance(tags, list):
        return False
    return all(isinstance(tag, str) and tag.strip() for tag in tags)
```

**Normalization**: Tags are deduplicated and whitespace-trimmed during parsing (see research.md)

**Error handling**: Invalid tags rejected at parse time:
```
"Invalid tags format. Use comma-separated values (e.g., 'work, home, urgent')."
```

### Due Date Validation

**Constraint**: Must be `datetime.date` object or `None`

```python
from datetime import date

def validate_due_date(due_date):
    """Validate due date."""
    if due_date is None:
        return True
    return isinstance(due_date, date)
```

**Format**: User input must be YYYY-MM-DD (validated during parsing)

**Error handling**: Invalid dates rejected with clear message:
```
"Invalid date. Use format: YYYY-MM-DD (example: 2026-01-10)"
```

### Recurrence Validation

**Constraint**: Must be one of: `'daily'`, `'weekly'`, `'monthly'`, or `None`

```python
def validate_recurrence(recurrence):
    """Validate recurrence pattern."""
    if recurrence is None:
        return True
    return recurrence in ['daily', 'weekly', 'monthly']
```

**Dependency**: Recurrence requires due_date to be set (enforced in CLI handlers)

**Error handling**:
```
"Invalid recurrence. Must be 'daily', 'weekly', 'monthly', or leave empty."
"Recurring tasks require a due date. Please set a due date first."
```

---

## Entity Methods

### Display Helper Methods

```python
def get_priority_display(self) -> str:
    """Return priority label for display."""
    if self.priority == 'high':
        return "[HIGH]"
    elif self.priority == 'medium':
        return "[MEDIUM]"
    elif self.priority == 'low':
        return "[LOW]"
    return ""
```

```python
def get_tags_display(self) -> str:
    """Return formatted tags for display."""
    if not self.tags:
        return ""
    return "[" + ", ".join(self.tags) + "]"
```

```python
def get_due_date_display(self) -> str:
    """Return formatted due date for display."""
    if not self.due_date:
        return ""
    return self.due_date.strftime("%b %d, %Y")  # "Jan 10, 2026"
```

```python
def get_recurrence_display(self) -> str:
    """Return recurrence pattern for display."""
    if not self.recurrence:
        return ""
    return f"[RECURS: {self.recurrence.capitalize()}]"
```

### State Detection Methods

```python
def is_overdue(self) -> bool:
    """Check if task is overdue (past due date and not completed)."""
    if self.completed or self.due_date is None:
        return False
    from datetime import date
    return self.due_date < date.today()
```

```python
def is_due_today(self) -> bool:
    """Check if task is due today."""
    if self.due_date is None:
        return False
    from datetime import date
    return self.due_date == date.today()
```

```python
def days_overdue(self) -> int:
    """Calculate days past due date (0 if not overdue)."""
    if not self.is_overdue():
        return 0
    from datetime import date
    delta = date.today() - self.due_date
    return delta.days
```

---

## Complete Task Class Definition

```python
from datetime import date, datetime

class Task:
    """
    Task entity for todo application.

    Extended in Feature 003 with priority, tags, due_date, and recurrence.
    All extended attributes are optional for backward compatibility.
    """

    def __init__(self, task_id, title, description=None, completed=False,
                 priority=None, tags=None, due_date=None, recurrence=None):
        """
        Initialize a task.

        Args:
            task_id (int): Unique task identifier
            title (str): Task title (required, non-empty)
            description (str, optional): Task description
            completed (bool): Completion status (default: False)
            priority (str, optional): 'high', 'medium', 'low', or None
            tags (list[str], optional): List of tag strings
            due_date (datetime.date, optional): Task deadline
            recurrence (str, optional): 'daily', 'weekly', 'monthly', or None

        Raises:
            ValueError: If title is empty or validation fails
        """
        # Core attributes validation (Phase I)
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        self._id = task_id  # Immutable
        self.title = title.strip()
        self.description = description.strip() if description else None
        self.completed = completed

        # Extended attributes validation (Feature 003)
        if priority is not None and priority not in ['high', 'medium', 'low']:
            raise ValueError(f"Invalid priority: {priority}")

        if recurrence is not None and recurrence not in ['daily', 'weekly', 'monthly']:
            raise ValueError(f"Invalid recurrence: {recurrence}")

        if tags is None:
            tags = []

        self.priority = priority
        self.tags = tags
        self.due_date = due_date
        self.recurrence = recurrence

    @property
    def id(self):
        """Get task ID (immutable)."""
        return self._id

    # Display helper methods (see above)
    # State detection methods (see above)
```

---

## Backward Compatibility

### Existing Tasks

Tasks created before Feature 003 will have:
- `priority = None`
- `tags = []`
- `due_date = None`
- `recurrence = None`

**Display behavior**: Extended attributes are not displayed when None/empty.

**Operations**: All existing operations (view, update, delete, toggle) work unchanged.

### Migration

No migration required. Existing tasks automatically gain extended attributes with safe defaults.

**Gradual enhancement**: Users can add extended attributes to old tasks via Update operation.

---

## Storage Representation

### In-Memory Structure

Tasks stored in dual structure (unchanged from Phase I):

```python
class TodoService:
    def __init__(self):
        self._tasks = []  # Ordered list for display
        self._task_dict = {}  # Dict for O(1) lookup
        self._next_id = 1
```

### Task Example

**Simple task (Phase I compatible)**:
```python
Task(
    task_id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False
)
# Extended attributes: priority=None, tags=[], due_date=None, recurrence=None
```

**Full-featured task (Feature 003)**:
```python
Task(
    task_id=2,
    title="Team meeting",
    description="Weekly sync with development team",
    completed=False,
    priority='high',
    tags=['work', 'meetings'],
    due_date=date(2026, 1, 10),
    recurrence='weekly'
)
```

---

## Relationships

### Priority Hierarchy

```
High Priority > Medium Priority > Low Priority > No Priority (None)
```

**Sort order**: When sorting by priority, tasks ordered: high → medium → low → None

### Tag Relationships

- **Many-to-many**: One task can have multiple tags, one tag can apply to multiple tasks
- **Filtering**: Filter returns tasks containing the specified tag (any match)
- **No hierarchy**: Tags are flat, no parent-child relationships

### Due Date Relationships

- **Time-based states**:
  - Overdue: due_date < today AND completed = False
  - Due today: due_date == today
  - Upcoming: due_date > today

### Recurrence Relationships

- **Dependency**: Recurrence requires due_date (validated in CLI layer)
- **Trigger**: Completing a recurring task creates new instance
- **Independence**: New instance is separate task with new ID

---

## Constraints Summary

| Constraint | Type | Enforcement |
|------------|------|-------------|
| Title non-empty | Business | Task.__init__ validation |
| ID immutability | Technical | Property with no setter |
| Priority values | Business | Task.__init__ validation |
| Recurrence values | Business | Task.__init__ validation |
| Recurrence requires due_date | Business | CLI validation (before Task creation) |
| Tags must be strings | Business | Parser ensures str type |
| Due date must be valid | Business | datetime.strptime validation |

---

**Document Version**: 1.0
**Last Updated**: 2026-01-04
**Status**: Complete - Ready for implementation
