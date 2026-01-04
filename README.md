# Phase I Todo Application

A simple, in-memory command-line todo application built with Python 3.13+ following Spec-Driven Development (SDD) principles.

## Overview

This is a menu-driven CLI application for managing todo tasks during a single session. All data is stored in memory and is cleared when the application exits (no persistence).

**Core Features:**
- ✅ Add tasks with title and optional description
- ✅ View all tasks with ID, title, and completion status
- ✅ Search tasks by keyword (title or description)
- ✅ Filter tasks by completion status (All/Pending/Completed)
- ✅ Sort tasks by ID, title, or status
- ✅ Update existing task details
- ✅ Delete tasks
- ✅ Toggle task completion status (Pending ↔ Completed)
- ✅ Graceful error handling
- ✅ Clean, menu-driven interface

**Advanced Task Management Features (Feature 003):**
- ✅ **Priority Levels**: Assign high/medium/low priority to tasks
- ✅ **Tags/Categories**: Organize tasks with multiple tags
- ✅ **Due Dates**: Set deadlines with automatic overdue detection
- ✅ **Recurring Tasks**: Daily/weekly/monthly task recurrence
- ✅ **Filter by Priority**: View tasks by priority level
- ✅ **Filter by Tags**: Find tasks with specific tags
- ✅ **View Overdue Tasks**: Dedicated view for overdue items
- ✅ **Sort by Priority**: Organize by importance
- ✅ **Sort by Due Date**: Arrange by deadline
- ✅ **Overdue Warnings**: Menu displays overdue task count
- ✅ **Overdue Indicators**: Visual markers for overdue tasks

## Requirements

- **Python**: 3.13 or higher
- **Dependencies**: None (Python standard library only)
- **Operating System**: Windows, Linux, or macOS

## Quick Start

### 1. Verify Python Version

```bash
python --version
# or
python3 --version
# Expected: Python 3.13.x or higher
```

### 2. Run the Application

```bash
python main.py
# or
python3 main.py
```

### 3. Use the Application

You'll see a numbered menu:

```
==============================
===  Todo Application  ===
==============================

1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Search/Filter Tasks
7. Sort Tasks
8. Filter by Priority
9. Filter by Tags
10. View Overdue Tasks
11. Exit

Enter your choice (1-11): _
```

**Example Workflow:**

1. Select `1` to add a task
   - Enter title: "Buy groceries"
   - Enter description (or press Enter to skip)
   - Set priority: high/medium/low (or skip)
   - Add tags: "errands,home" (comma-separated, or skip)
   - Set due date: YYYY-MM-DD format (or skip)
   - Set recurrence: daily/weekly/monthly (only if due date set, or skip)

2. Select `2` to view all tasks
   - See your task list with IDs, statuses, priorities, tags, and due dates
   - Overdue tasks show [OVERDUE X days] indicator
   - Tasks due today show [DUE TODAY] indicator

3. Select `8` to filter by priority
   - Choose high/medium/low
   - See only tasks with that priority level

4. Select `9` to filter by tags
   - Enter tag name
   - See all tasks with that tag

5. Select `10` to view overdue tasks
   - See all tasks past their due date
   - Shows days overdue for each task

6. Select `7` to sort tasks
   - Choose sort: by ID, Title, Status, Priority, or Due Date
   - See tasks in sorted order

7. Select `5` to mark a recurring task complete
   - Enter task ID
   - Status toggles to Completed
   - If recurring, new instance created automatically with next due date

8. Select `11` to exit
   - All data is cleared (no persistence)

## Project Structure

```
todo-app-phase1/
├── src/
│   ├── models/
│   │   └── task.py              # Task entity (id, title, description, completed)
│   ├── services/
│   │   └── todo_service.py      # Business logic (CRUD operations)
│   └── cli/
│       └── menu.py               # CLI interface and menu loop
├── main.py                       # Application entry point
├── specs/                        # SDD documentation
│   └── 001-todo-app/
│       ├── spec.md               # Feature specification
│       ├── plan.md               # Implementation plan
│       ├── data-model.md         # Data model documentation
│       ├── quickstart.md         # Developer quickstart guide
│       ├── tasks.md              # Implementation tasks
│       └── contracts/
│           └── cli-interface.md  # CLI interface specification
├── .specify/
│   └── memory/
│       └── constitution.md       # Project constitution (SDD principles)
└── README.md                     # This file
```

## Design Principles

This project follows **Spec-Driven Development (SDD)** as defined in `.specify/memory/constitution.md`:

1. **Specification Before Implementation**: Complete spec created before coding
2. **Planning Before Coding**: Architectural plan approved before implementation
3. **Tasks Before Execution**: Work broken into discrete, testable tasks
4. **Simplicity Over Complexity**: Python standard library only, minimal architecture
5. **No Features Beyond Phase I Scope**: Strictly scoped to approved requirements

## Technical Details

**Architecture**: Three-layer separation of concerns
- **Models** (`src/models/`): Task entity with validation
- **Services** (`src/services/`): Business logic and in-memory storage
- **CLI** (`src/cli/`): User interface and menu loop

**Storage**: Dual structure for efficiency
- **List**: Maintains task order for display
- **Dictionary**: Provides O(1) lookup by task ID

**Data Model**:
- **Task ID**: Auto-incremented integer (no reuse after deletion)
- **Title**: Required, non-empty string
- **Description**: Optional string
- **Completed**: Boolean (default: False)
- **Priority**: Optional ('high', 'medium', 'low', or None)
- **Tags**: Optional list of strings for categorization
- **Due Date**: Optional datetime.date for deadlines
- **Recurrence**: Optional ('daily', 'weekly', 'monthly', or None)

## Validation

All operations include input validation:
- ✅ Empty titles rejected
- ✅ Invalid menu options handled gracefully
- ✅ Non-existent task IDs return clear error messages
- ✅ Application never crashes on invalid input

## Limitations (By Design)

Phase I with advanced task management features - intentionally simple and focused:

- ❌ **No Persistence**: Data lost on exit (in-memory only)
- ❌ **No Database**: Uses Python lists and dictionaries
- ❌ **No GUI**: Command-line interface only
- ❌ **No External Dependencies**: Standard library only (datetime module)
- ❌ **Single User**: No multi-user support
- ❌ **No Automated Tests**: Manual testing only per constitutional constraints

## Development

### Code Quality

All code adheres to constitutional quality standards:
- ✅ Clean, readable code with clear variable names
- ✅ Small, focused functions with single responsibilities
- ✅ Comprehensive docstrings for all classes and methods
- ✅ No dead code or unused imports

### Testing

Manual testing against acceptance scenarios from `specs/001-todo-app/spec.md`:
- 6 user stories with 18 acceptance scenarios
- All scenarios validated manually
- Independent test criteria for each user story

### Current Implementation Status

**Completed Features:**
- ✅ Feature 001: Core todo app functionality
- ✅ Feature 002: Search, filter, and sort capabilities
- ✅ Feature 003: Advanced task management (priorities, tags, due dates, recurring tasks)

**Future Phases**

Future enhancements may include:
- Persistent storage (database or file system)
- Email/SMS reminders for due dates
- Calendar integration
- Web or GUI interface
- Multi-user support and collaboration
- Task dependencies and subtasks

## Documentation

Comprehensive SDD documentation available in `specs/`:

**Feature 001 - Core Todo App** (`specs/001-todo-app/`):
- spec.md, plan.md, data-model.md, tasks.md, quickstart.md, contracts/

**Feature 002 - Search/Filter/Sort** (`specs/002-search-filter-sort/`):
- spec.md, plan.md, data-model.md, tasks.md, quickstart.md, contracts/

**Feature 003 - Advanced Task Management** (`specs/003-advanced-task-mgmt/`):
- spec.md, plan.md, data-model.md, tasks.md, quickstart.md, contracts/
- 8 user stories: priorities, tags, due dates, filtering, overdue view, sorting, recurring tasks, menu warnings

## License

This is a demonstration project for Spec-Driven Development.

## Acknowledgments

Built with Claude Code following constitutional SDD principles.

---

**Phase I Todo Application** - Simple. Reliable. In-Memory.
