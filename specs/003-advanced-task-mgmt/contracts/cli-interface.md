# CLI Interface Contract: Advanced Task Management

**Feature**: 003-advanced-task-mgmt
**Created**: 2026-01-04
**Purpose**: Define CLI interface specifications for Feature 003

## Main Menu

```
==============================
===  Todo Application  ===
==============================

! You have 3 overdue tasks     [Only if overdue tasks exist]

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

---

## Option 1: Add Task (Extended)

**Flow**: Extended to collect priority, tags, due date, and recurrence

```
=== Add Task ===

Enter task title: Buy groceries
Enter task description (optional, press Enter to skip): Weekly shopping

Set priority (high/medium/low, or press Enter to skip): high
Add tags (comma-separated, or press Enter to skip): shopping, urgent
Set due date (YYYY-MM-DD, or press Enter to skip): 2026-01-10
Set recurrence (daily/weekly/monthly, or press Enter to skip): weekly

Task added successfully!
  ID: 1
  Title: Buy groceries
  Description: Weekly shopping
  Priority: [HIGH]
  Tags: shopping, urgent
  Due: Jan 10, 2026
  Recurs: Weekly
  Status: Pending
```

**Validation**:
- Priority: Accept only 'high', 'medium', 'low', or empty
- Tags: Parse comma-separated, deduplicate, trim whitespace
- Due date: Validate YYYY-MM-DD format, reject invalid dates
- Recurrence: Only allow if due_date is set

**Error Messages**:
```
"Invalid priority. Must be 'high', 'medium', 'low', or leave empty."
"Invalid date. Use format: YYYY-MM-DD (example: 2026-01-10)"
"Invalid recurrence. Must be 'daily', 'weekly', 'monthly', or leave empty."
"Recurring tasks require a due date. Please set a due date first."
```

---

## Option 2: View Tasks (Extended)

**Display Format**: Extended to show priority, tags, due date, recurrence, and overdue indicators

```
=== All Tasks ===

ID    | Title                          | Priority  | Tags            | Due Date      | Recurs   | Status
------------------------------------------------------------------------------------------------------
1     | Buy groceries                  | [HIGH]    | shopping, urgent| Jan 10, 2026  | Weekly   | Pending
2     | Team meeting [OVERDUE 3 days]  | [MEDIUM]  | work, meetings  | Jan 01, 2026  |          | Pending
3     | Read book                      |           |                 |               |          | Completed

Total: 3 tasks
```

**Indicators**:
- `[OVERDUE X days]`: Task past due date and not completed
- `[DUE TODAY]`: Task due today
- Priority shown as `[HIGH]`, `[MEDIUM]`, `[LOW]`, or empty
- Tags shown comma-separated or empty
- Recurrence shown or empty

---

## Option 3: Update Task (Extended)

**Flow**: Extended to allow updating priority, tags, due date, recurrence

```
=== Update Task ===

Enter task ID to update: 1

Current title: Buy groceries
Enter new title (press Enter to keep current):

Current description: Weekly shopping
Enter new description (press Enter to keep current):

Current priority: high
Set new priority (high/medium/low, or press Enter to keep current): medium

Current tags: shopping, urgent
Enter new tags (comma-separated, or press Enter to keep current): shopping, home

Current due date: 2026-01-10
Set new due date (YYYY-MM-DD, or press Enter to keep current):

Current recurrence: weekly
Set new recurrence (daily/weekly/monthly, or press Enter to keep current):

Task updated successfully!
  ID: 1
  Title: Buy groceries
  Description: Weekly shopping
  Priority: [MEDIUM]
  Tags: shopping, home
  Due: Jan 10, 2026
  Recurs: Weekly
  Status: Pending
```

---

## Option 8: Filter by Priority (New)

**Flow**: Display only tasks matching selected priority

```
=== Filter by Priority ===

Select priority:
  1. High
  2. Medium
  3. Low
  4. No priority (None)

Enter choice (1-4): 1

Showing 2 high-priority tasks:

ID    | Title                 | Tags            | Due Date      | Status
----------------------------------------------------------------
1     | Buy groceries         | shopping, home  | Jan 10, 2026  | Pending
5     | Finish report         | work            | Jan 12, 2026  | Pending

Total: 2 tasks
```

---

## Option 9: Filter by Tags (New)

**Flow**: Display tasks containing specified tag

```
=== Filter by Tags ===

Enter tag to filter by: work

Found 3 tasks with tag 'work':

ID    | Title                 | Priority  | Due Date      | Status
-----------------------------------------------------------
2     | Team meeting          | [MEDIUM]  | Jan 01, 2026  | Pending
5     | Finish report         | [HIGH]    | Jan 12, 2026  | Pending
7     | Code review           | [LOW]     |               | Completed

Total: 3 tasks

[If no matches]:
No tasks found with tag 'work'.
```

---

## Option 10: View Overdue Tasks (New)

**Flow**: Display incomplete tasks past their due date

```
=== Overdue Tasks ===

You have 2 overdue tasks:

ID    | Title                 | Priority  | Due Date      | Days Overdue
--------------------------------------------------------------------
2     | Team meeting          | [MEDIUM]  | Jan 01, 2026  | 3 days
8     | Pay bills             | [HIGH]    | Dec 30, 2025  | 5 days

Total: 2 overdue tasks

[If no overdue]:
No overdue tasks. Great job staying on track!
```

---

## Option 7: Sort Tasks (Extended)

**Extended sort options**: Add priority and due date sorting

```
=== Sort Tasks ===

Sort by:
  1. ID (ascending)
  2. ID (descending)
  3. Title (A-Z)
  4. Title (Z-A)
  5. Status (completed first)
  6. Status (pending first)
  7. Priority (high to low)        [NEW]
  8. Priority (low to high)        [NEW]
  9. Due Date (soonest first)      [NEW]
  10. Due Date (latest first)      [NEW]

Enter choice (1-10): 7

Tasks sorted by Priority (high to low):

[Display tasks with high priority first, then medium, then low, then None]
```

---

## Recurring Task Behavior

**Trigger**: When user marks a recurring task as complete (Option 5)

```
=== Mark Task Complete/Incomplete ===

Enter task ID: 1

Task marked as completed!
  ID: 1
  Title: Buy groceries
  Status: Completed

Creating next occurrence...

New recurring task created!
  ID: 12
  Title: Buy groceries
  Description: Weekly shopping
  Priority: [MEDIUM]
  Tags: shopping, home
  Due: Jan 17, 2026  [7 days after original]
  Recurs: Weekly
  Status: Pending
```

---

## Input Validation

### Date Validation
```python
Input: "2026-01-10" → Valid date
Input: "Jan 10" → Error: "Invalid date. Use format: YYYY-MM-DD"
Input: "2026-02-30" → Error: "Invalid date. February 30 does not exist."
Input: "" → Accepted (None)
```

### Tag Parsing
```python
Input: "work, home, urgent" → ['work', 'home', 'urgent']
Input: "work,work,work" → ['work'] (deduplicated)
Input: "  work  , home  " → ['work', 'home'] (trimmed)
Input: ",,," → [] (empty tags)
Input: "" → [] (empty tags)
```

### Priority Validation
```python
Input: "high" → 'high'
Input: "HIGH" → 'high' (case-insensitive)
Input: "urgent" → Error: "Invalid priority"
Input: "" → None (accepted)
```

---

## Error Handling

All operations handle errors gracefully:

- **Invalid menu choice**: "Invalid choice. Please enter a number between 1 and 11."
- **Task not found**: "Task with ID X not found."
- **Empty title**: "Task title cannot be empty."
- **Invalid date**: "Invalid date. Use format: YYYY-MM-DD (example: 2026-01-10)"
- **Recurrence without due date**: "Recurring tasks require a due date."

Application never crashes on invalid input.

---

**Contract Version**: 1.0
**Last Updated**: 2026-01-04
**Status**: Complete
