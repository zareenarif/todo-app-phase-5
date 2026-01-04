"""
Task Model - Represents a todo item

Adheres to constitutional Task Entity Rules (v1.2.0):

Core Attributes:
- id: Integer, auto-incremented, unique, immutable
- title: String, required, non-empty
- description: String, optional
- completed: Boolean, default False

Extended Attributes (Feature 003):
- priority: String, optional ('high', 'medium', 'low', or None)
- tags: List of strings, optional
- due_date: datetime.date, optional
- recurrence: String, optional ('daily', 'weekly', 'monthly', or None)
"""


class Task:
    """
    Represents a todo task item.

    Core Attributes:
        id (int): Unique task identifier (immutable)
        title (str): Task title (required, non-empty)
        description (str): Optional task description
        completed (bool): Completion status (default: False)

    Extended Attributes (Feature 003):
        priority (str): Priority level ('high', 'medium', 'low', or None)
        tags (list): List of tag strings for categorization
        due_date (datetime.date): Task deadline (None if no deadline)
        recurrence (str): Recurrence pattern ('daily', 'weekly', 'monthly', or None)
    """

    def __init__(self, task_id, title, description=None, completed=False,
                 priority=None, tags=None, due_date=None, recurrence=None):
        """
        Initialize a new Task.

        Args:
            task_id (int): Unique integer identifier
            title (str): Task title (must be non-empty after strip)
            description (str, optional): Optional description
            completed (bool, optional): Completion status (default: False)
            priority (str, optional): Priority level ('high', 'medium', 'low', or None)
            tags (list, optional): List of tag strings
            due_date (datetime.date, optional): Task deadline
            recurrence (str, optional): Recurrence pattern ('daily', 'weekly', 'monthly', or None)

        Raises:
            ValueError: If title is empty or validation fails
        """
        # Core attributes validation
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        # Extended attributes validation (Feature 003)
        if priority is not None and priority not in ['high', 'medium', 'low']:
            raise ValueError(f"Invalid priority: {priority}. Must be 'high', 'medium', 'low', or None")

        if recurrence is not None and recurrence not in ['daily', 'weekly', 'monthly']:
            raise ValueError(f"Invalid recurrence: {recurrence}. Must be 'daily', 'weekly', 'monthly', or None")

        # Core attributes
        self._id = task_id  # Immutable (no setter, private attribute)
        self.title = title.strip()
        self.description = description.strip() if description else None
        self.completed = completed

        # Extended attributes (Feature 003)
        self.priority = priority
        self.tags = tags if tags is not None else []
        self.due_date = due_date
        self.recurrence = recurrence

    @property
    def id(self):
        """Get task ID (immutable)."""
        return self._id

    def get_priority_display(self):
        """
        Return priority label for display.

        Returns:
            str: Priority label ("[HIGH]", "[MEDIUM]", "[LOW]") or empty string
        """
        if self.priority == 'high':
            return "[HIGH]"
        elif self.priority == 'medium':
            return "[MEDIUM]"
        elif self.priority == 'low':
            return "[LOW]"
        return ""

    def get_tags_display(self):
        """
        Return formatted tags for display.

        Returns:
            str: Comma-joined tags ("[work, home]") or empty string
        """
        if not self.tags:
            return ""
        return "[" + ", ".join(self.tags) + "]"

    def get_due_date_display(self):
        """
        Return formatted due date for display.

        Returns:
            str: Formatted date ("Jan 10, 2026") or empty string
        """
        if not self.due_date:
            return ""
        return self.due_date.strftime("%b %d, %Y")

    def get_recurrence_display(self):
        """
        Return recurrence pattern for display.

        Returns:
            str: Recurrence label ("[RECURS: Daily/Weekly/Monthly]") or empty string
        """
        if not self.recurrence:
            return ""
        return f"[RECURS: {self.recurrence.capitalize()}]"

    def is_overdue(self):
        """
        Check if task is overdue (past due date and not completed).

        Returns:
            bool: True if task is overdue, False otherwise
        """
        if self.completed or self.due_date is None:
            return False
        from datetime import date
        return self.due_date < date.today()

    def is_due_today(self):
        """
        Check if task is due today.

        Returns:
            bool: True if due today, False otherwise
        """
        if self.due_date is None:
            return False
        from datetime import date
        return self.due_date == date.today()

    def days_overdue(self):
        """
        Calculate days past due date.

        Returns:
            int: Number of days overdue (0 if not overdue)
        """
        if not self.is_overdue():
            return 0
        from datetime import date
        delta = date.today() - self.due_date
        return delta.days

    def __repr__(self):
        """String representation for debugging."""
        return f"Task(id={self.id}, title='{self.title}', completed={self.completed})"

    def __str__(self):
        """Human-readable string representation."""
        status = "Completed" if self.completed else "Pending"
        return f"[{self.id}] {self.title} - {status}"
