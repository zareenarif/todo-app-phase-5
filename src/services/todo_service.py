"""
TodoService - Business logic for todo task management

Provides CRUD operations for tasks with in-memory storage.
Uses dual storage: list for ordered display, dict for O(1) lookup.
"""

from src.models.task import Task


class TodoService:
    """
    Service layer for todo task management.

    Maintains tasks in memory using:
    - List for ordered display
    - Dictionary for fast lookup by ID

    Attributes:
        _tasks (list): Ordered list of tasks
        _task_dict (dict): ID to task mapping for O(1) lookup
        _next_id (int): Counter for auto-incrementing task IDs
    """

    def __init__(self):
        """Initialize TodoService with empty task storage."""
        self._tasks = []
        self._task_dict = {}
        self._next_id = 1

    def add_task(self, title, description=None, priority=None, tags=None,
                 due_date=None, recurrence=None):
        """
        Add a new task.

        Args:
            title (str): Task title (required, non-empty)
            description (str, optional): Task description
            priority (str, optional): Priority level ('high', 'medium', 'low', or None)
            tags (list, optional): List of tag strings
            due_date (datetime.date, optional): Task deadline
            recurrence (str, optional): Recurrence pattern ('daily', 'weekly', 'monthly', or None)

        Returns:
            Task: The created task

        Raises:
            ValueError: If title is empty or validation fails
        """
        task = Task(self._next_id, title, description, False,
                   priority=priority, tags=tags, due_date=due_date, recurrence=recurrence)
        self._tasks.append(task)
        self._task_dict[task.id] = task
        self._next_id += 1
        return task

    def get_all_tasks(self):
        """
        Get all tasks.

        Returns:
            list: List of all tasks in creation order
        """
        return self._tasks.copy()

    def get_task_by_id(self, task_id):
        """
        Get task by ID.

        Args:
            task_id (int): Task ID

        Returns:
            Task or None: Task if found, None otherwise
        """
        return self._task_dict.get(task_id)

    def update_task(self, task_id, title=None, description=None, priority=None,
                    tags=None, due_date=None, recurrence=None):
        """
        Update task attributes.

        Args:
            task_id (int): Task ID
            title (str, optional): New title (must be non-empty if provided)
            description (str, optional): New description
            priority (str, optional): New priority ('high', 'medium', 'low', or None)
            tags (list, optional): New tags list
            due_date (datetime.date, optional): New due date
            recurrence (str, optional): New recurrence ('daily', 'weekly', 'monthly', or None)

        Returns:
            tuple: (success: bool, message: str)
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False, f"Task with ID {task_id} not found"

        if title is not None:
            if not title or not title.strip():
                return False, "Task title cannot be empty"
            task.title = title.strip()

        if description is not None:
            task.description = description.strip() if description else None

        if priority is not None:
            if priority != "KEEP_CURRENT" and priority not in ['high', 'medium', 'low', None]:
                return False, f"Invalid priority: {priority}"
            if priority != "KEEP_CURRENT":
                task.priority = priority

        if tags is not None and tags != "KEEP_CURRENT":
            task.tags = tags

        if due_date is not None and due_date != "KEEP_CURRENT":
            task.due_date = due_date

        if recurrence is not None:
            if recurrence != "KEEP_CURRENT" and recurrence not in ['daily', 'weekly', 'monthly', None]:
                return False, f"Invalid recurrence: {recurrence}"
            if recurrence != "KEEP_CURRENT":
                task.recurrence = recurrence

        return True, "Task updated successfully"

    def delete_task(self, task_id):
        """
        Delete task by ID.

        Args:
            task_id (int): Task ID

        Returns:
            tuple: (success: bool, message: str)
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False, f"Task with ID {task_id} not found"

        self._tasks.remove(task)
        del self._task_dict[task_id]
        return True, "Task deleted successfully"

    def create_recurring_instance(self, original_task):
        """
        Create a new instance of a recurring task with updated due date.

        Args:
            original_task (Task): The original recurring task

        Returns:
            Task or None: New task instance or None if creation failed
        """
        if not original_task.recurrence or not original_task.due_date:
            return None

        from datetime import timedelta

        # Calculate new due date based on recurrence type
        if original_task.recurrence == 'daily':
            new_due_date = original_task.due_date + timedelta(days=1)
        elif original_task.recurrence == 'weekly':
            new_due_date = original_task.due_date + timedelta(weeks=1)
        elif original_task.recurrence == 'monthly':
            # Add approximately 30 days for monthly recurrence
            new_due_date = original_task.due_date + timedelta(days=30)
        else:
            return None

        # Create new task with same attributes but new due date
        new_task = self.add_task(
            title=original_task.title,
            description=original_task.description,
            priority=original_task.priority,
            tags=original_task.tags.copy() if original_task.tags else [],
            due_date=new_due_date,
            recurrence=original_task.recurrence
        )
        return new_task

    def toggle_task_completion(self, task_id):
        """
        Toggle task completion status. Creates new instance for recurring tasks.

        Args:
            task_id (int): Task ID

        Returns:
            tuple: (success: bool, message: str, new_status: bool or None, new_task: Task or None)
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False, f"Task with ID {task_id} not found", None, None

        # Check if this is a recurring task being marked complete
        is_recurring = task.recurrence and task.due_date and not task.completed

        task.completed = not task.completed
        status_text = "completed" if task.completed else "pending"

        # Create new recurring instance if applicable
        new_task = None
        if is_recurring:
            new_task = self.create_recurring_instance(task)

        return True, f"Task marked as {status_text}", task.completed, new_task

    def search_tasks(self, keyword):
        """
        Search tasks by keyword in title or description.

        Args:
            keyword (str): Search term (case-insensitive)

        Returns:
            list: Tasks matching keyword in title or description
        """
        if not keyword or not keyword.strip():
            return self._tasks.copy()

        keyword_lower = keyword.lower().strip()
        results = [
            task for task in self._tasks
            if keyword_lower in task.title.lower() or
               (task.description and keyword_lower in task.description.lower())
        ]
        return results

    def filter_tasks(self, status_filter):
        """
        Filter tasks by completion status.

        Args:
            status_filter (str): 'all', 'pending', or 'completed'

        Returns:
            list: Filtered task list
        """
        if status_filter == 'all':
            return self._tasks.copy()
        elif status_filter == 'pending':
            return [task for task in self._tasks if not task.completed]
        elif status_filter == 'completed':
            return [task for task in self._tasks if task.completed]
        else:
            return self._tasks.copy()  # Invalid filter returns all

    def search_and_filter(self, keyword=None, status_filter='all'):
        """
        Combine search and filter operations.

        Args:
            keyword (str, optional): Search keyword
            status_filter (str): 'all', 'pending', or 'completed'

        Returns:
            list: Tasks matching both criteria
        """
        # Filter first (typically smaller result set)
        filtered = self.filter_tasks(status_filter)

        # Then search within filtered results
        if not keyword or not keyword.strip():
            return filtered

        keyword_lower = keyword.lower().strip()
        results = [
            task for task in filtered
            if keyword_lower in task.title.lower() or
               (task.description and keyword_lower in task.description.lower())
        ]
        return results

    def sort_tasks(self, sort_by, reverse=False):
        """
        Sort tasks by specified criterion.

        Args:
            sort_by (str): 'id', 'title', 'status', 'priority', or 'due_date'
            reverse (bool): True for descending, False for ascending

        Returns:
            list: Sorted task list
        """
        if sort_by == 'id':
            return sorted(self._tasks, key=lambda t: t.id, reverse=reverse)
        elif sort_by == 'title':
            return sorted(self._tasks, key=lambda t: t.title.lower(), reverse=reverse)
        elif sort_by == 'status':
            return sorted(self._tasks, key=lambda t: t.completed, reverse=reverse)
        elif sort_by == 'priority':
            # Priority order: high=3, medium=2, low=1, None=0
            priority_map = {'high': 3, 'medium': 2, 'low': 1, None: 0}
            return sorted(self._tasks, key=lambda t: priority_map.get(t.priority, 0), reverse=reverse)
        elif sort_by == 'due_date':
            # Sort by due date, putting None at the end
            from datetime import date
            return sorted(self._tasks, key=lambda t: t.due_date if t.due_date else date.max, reverse=reverse)
        else:
            return self._tasks.copy()  # Invalid sort returns original order

    def filter_by_priority(self, priority):
        """
        Filter tasks by priority level.

        Args:
            priority (str): Priority level ('high', 'medium', or 'low')

        Returns:
            list: Tasks matching the specified priority
        """
        return [task for task in self._tasks if task.priority == priority]

    def filter_by_tag(self, tag):
        """
        Filter tasks by tag.

        Args:
            tag (str): Tag to filter by

        Returns:
            list: Tasks containing the specified tag
        """
        return [task for task in self._tasks if tag in task.tags]

    def get_overdue_tasks(self):
        """
        Get all overdue tasks (past due date and not completed).

        Returns:
            list: Tasks that are overdue
        """
        return [task for task in self._tasks if task.is_overdue()]

    def get_overdue_count(self):
        """
        Get count of overdue tasks.

        Returns:
            int: Number of overdue tasks
        """
        return len(self.get_overdue_tasks())
