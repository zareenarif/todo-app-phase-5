# Feature Specification: Advanced Task Management

**Feature Branch**: `003-advanced-task-mgmt`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "Feature 003: Advanced Task Management - Add priorities, tags, due dates, recurring tasks, and time-based reminders to enable better organization and time management"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Task Priority (Priority: P1) 🎯 MVP

Users can assign priority levels (high, medium, low) to tasks to indicate urgency and importance, helping them focus on what matters most.

**Why this priority**: Priority is the foundation of task organization. Without it, users cannot distinguish between urgent and non-urgent work, making it the most critical organizational feature. This alone delivers immediate value by enabling basic task triage.

**Independent Test**: Create 5 tasks with different priorities (2 high, 2 medium, 1 low), view all tasks, and verify priorities are displayed correctly next to each task.

**Acceptance Scenarios**:

1. **Given** I am adding a new task, **When** I enter the task details, **Then** I am prompted to optionally set a priority (high/medium/low) or skip
2. **Given** I set priority to "high", **When** the task is created, **Then** the task is saved with priority "high" and displays "[HIGH]" label
3. **Given** I create a task without setting priority, **When** the task is saved, **Then** the priority defaults to None and no priority label is shown
4. **Given** I have an existing task, **When** I update the task, **Then** I can change or remove the priority level

---

### User Story 2 - Add Tags/Categories (Priority: P1) 🎯 MVP

Users can categorize tasks with multiple tags (e.g., 'work', 'home', 'personal') to organize tasks by context or area of responsibility.

**Why this priority**: Tags enable basic categorization and are essential for organizing tasks by context. Combined with priorities, this forms the minimal organizational system users need. Independently delivers value by letting users group related tasks.

**Independent Test**: Create 10 tasks with various tag combinations ('work', 'home', 'urgent', 'project-a'), view all tasks, and verify tags are displayed for each task.

**Acceptance Scenarios**:

1. **Given** I am adding a new task, **When** I enter task details, **Then** I am prompted to optionally add tags (comma-separated) or skip
2. **Given** I enter "work, urgent, project-a", **When** the task is created, **Then** the task is saved with all three tags and displays them as labels
3. **Given** I create a task without tags, **When** the task is saved, **Then** the tags list is empty and no tag labels are shown
4. **Given** I have an existing task, **When** I update the task, **Then** I can add, remove, or modify tags

---

### User Story 3 - Set Due Dates (Priority: P1) 🎯 MVP

Users can assign due dates to tasks to track deadlines and manage time-sensitive work.

**Why this priority**: Due dates are fundamental for time management. Without them, users cannot track deadlines or identify overdue work. This is the foundation for all time-based features and independently delivers value for deadline tracking.

**Independent Test**: Create 5 tasks with different due dates (2 past dates, 1 today, 2 future dates), view all tasks, and verify due dates are displayed with appropriate indicators (overdue, today, upcoming).

**Acceptance Scenarios**:

1. **Given** I am adding a new task, **When** I enter task details, **Then** I am prompted to optionally set a due date (YYYY-MM-DD format) or skip
2. **Given** I enter a valid date "2026-01-10", **When** the task is created, **Then** the due date is saved and displayed in readable format
3. **Given** I enter an invalid date, **When** I try to create the task, **Then** I receive an error message and am prompted to re-enter
4. **Given** I create a task without a due date, **When** the task is saved, **Then** the due date is None and no date is shown
5. **Given** I have an existing task, **When** I update the task, **Then** I can change or remove the due date
6. **Given** a task has a due date in the past, **When** I view tasks, **Then** the task is marked as "[OVERDUE]" in red text
7. **Given** a task is due today, **When** I view tasks, **Then** the task is marked as "[DUE TODAY]" in yellow text

---

### User Story 4 - Filter by Priority and Tags (Priority: P2)

Users can filter tasks to show only those matching specific priority levels or tags, helping them focus on relevant work.

**Why this priority**: Filtering enhances the organizational features from P1 stories by letting users narrow down their task list. This is valuable but requires P1 stories (priorities and tags) to exist first.

**Independent Test**: Create 15 tasks with various priorities and tags, use filter menu to show only "high priority tasks" or only "work-tagged tasks", and verify correct subset is displayed.

**Acceptance Scenarios**:

1. **Given** I select "Filter by Priority" from the menu, **When** I choose "High", **Then** only tasks with priority "high" are displayed
2. **Given** I select "Filter by Tags" from the menu, **When** I enter "work", **Then** only tasks containing the tag "work" are displayed
3. **Given** I apply a filter that matches no tasks, **When** the results are shown, **Then** I see a message "No tasks match this filter"
4. **Given** I have applied a filter, **When** I return to main menu and select "View Tasks", **Then** the filter is cleared and all tasks are shown

---

### User Story 5 - View Overdue Tasks (Priority: P2)

Users can see a dedicated view of overdue tasks with visual warnings, helping them identify and address missed deadlines.

**Why this priority**: This builds on the due date feature (P1) by providing focused visibility into overdue work. Valuable for deadline management but requires due dates to exist first.

**Independent Test**: Create 5 overdue tasks and 10 current tasks, select "View Overdue Tasks" from menu, and verify only the 5 overdue tasks are shown with warning indicators.

**Acceptance Scenarios**:

1. **Given** I select "View Overdue Tasks" from the menu, **When** the list loads, **Then** only tasks with due dates in the past are displayed
2. **Given** there are no overdue tasks, **When** I select "View Overdue Tasks", **Then** I see message "No overdue tasks. Great job staying on track!"
3. **Given** overdue tasks exist, **When** they are displayed, **Then** each shows "[OVERDUE]" label and days overdue count (e.g., "3 days overdue")
4. **Given** I view overdue tasks, **When** I mark one as complete, **Then** it is removed from the overdue list

---

### User Story 6 - Sort by Priority, Tags, or Due Date (Priority: P2)

Users can sort their task list by priority (high to low), due date (soonest first), or alphabetically, helping them view tasks in the most useful order.

**Why this priority**: Sorting enhances existing features by providing different views of the task list. Useful but not critical - users can still accomplish their goals without it.

**Independent Test**: Create 10 tasks with mixed priorities, tags, and due dates, select different sort options, and verify the list reorders correctly each time.

**Acceptance Scenarios**:

1. **Given** I select "Sort Tasks" from the menu and choose "Priority", **When** the list loads, **Then** tasks are ordered: high priority first, then medium, then low, then no priority
2. **Given** I select "Sort by Due Date", **When** the list loads, **Then** tasks are ordered with soonest due date first, overdue at top, no due date at bottom
3. **Given** multiple tasks have the same priority, **When** sorted by priority, **Then** tasks with same priority are sub-sorted by ID (creation order)
4. **Given** I return to "View Tasks" after sorting, **When** the main list loads, **Then** tasks return to original creation order

---

### User Story 7 - Configure Recurring Tasks (Priority: P3)

Users can set tasks to recur on a schedule (daily, weekly, monthly), automating the creation of repetitive tasks.

**Why this priority**: Recurring tasks are a convenience feature for repeated workflows. Nice to have but not essential for core task management. Most users can manually recreate tasks if needed.

**Independent Test**: Create a weekly recurring task "Team meeting", mark it complete, and verify a new instance is automatically created with due date 7 days from now.

**Acceptance Scenarios**:

1. **Given** I am adding a task, **When** I set recurrence to "weekly", **Then** the task is saved with recurrence pattern "weekly"
2. **Given** I have a recurring task, **When** I mark it as complete, **Then** a new instance is created with the same title, description, priority, and tags
3. **Given** the recurring pattern is "daily", **When** the new instance is created, **Then** the due date is set to 1 day after the completed task's due date
4. **Given** the recurring pattern is "weekly", **When** the new instance is created, **Then** the due date is set to 7 days after the completed task's due date
5. **Given** the recurring pattern is "monthly", **When** the new instance is created, **Then** the due date is set to 30 days after the completed task's due date
6. **Given** I update a recurring task, **When** I change the recurrence pattern, **Then** future instances use the new pattern (current instance unchanged)

---

### User Story 8 - Display Overdue Count in Menu (Priority: P3)

Users see the count of overdue tasks displayed in the main menu, providing passive awareness of missed deadlines without requiring navigation.

**Why this priority**: This is a quality-of-life enhancement that provides ambient awareness. Useful but not critical - users can still navigate to view overdue tasks manually.

**Independent Test**: Create 3 overdue tasks, return to main menu, and verify the menu shows "! You have 3 overdue tasks" warning message.

**Acceptance Scenarios**:

1. **Given** I have overdue tasks, **When** the main menu is displayed, **Then** I see "! You have [N] overdue task(s)" at the top of the menu
2. **Given** I have no overdue tasks, **When** the main menu is displayed, **Then** no overdue warning is shown
3. **Given** the overdue count changes, **When** I return to the main menu, **Then** the count is updated to reflect the current state

---

### Edge Cases

- **Invalid date format**: What happens when user enters "2026-13-45" or "January 10"? → System validates format and shows error with example
- **Past due date on creation**: Can users create a task that is already overdue? → Yes, system allows it and marks as overdue immediately
- **Empty tags**: What happens when user enters only commas ",,,"? → System ignores empty entries and saves no tags
- **Duplicate tags**: What happens when user enters "work, work, work"? → System deduplicates and stores only one instance
- **Special characters in tags**: How are tags like "work@home" or "project#1" handled? → System accepts alphanumeric and common symbols, validates input
- **Recurring task without due date**: What happens when recurrence is set but no due date? → System shows error: "Recurring tasks require a due date"
- **Completed recurring task creation fails**: What if the new instance cannot be created due to error? → Original task remains complete, error is logged, user is notified
- **Priority/tag filter on empty list**: What happens when filtering an empty task list? → Display "No tasks available to filter"
- **Sorting with all None values**: What happens when sorting by priority and all tasks have no priority? → Tasks remain in original creation order
- **Overdue task marked complete**: Does it still show in overdue list? → No, completed tasks are excluded from overdue view

## Requirements *(mandatory)*

### Functional Requirements

**Priority & Organization:**
- **FR-001**: System MUST allow users to optionally assign priority level (high, medium, low, or None) when creating a task
- **FR-002**: System MUST allow users to update the priority level of existing tasks
- **FR-003**: System MUST display priority labels ([HIGH], [MEDIUM], [LOW]) next to tasks in all views
- **FR-004**: System MUST allow users to add multiple tags (comma-separated) when creating a task
- **FR-005**: System MUST allow users to update tags on existing tasks
- **FR-006**: System MUST display all tags as labels next to each task in all views
- **FR-007**: System MUST deduplicate tags entered by the user (e.g., "work, work" → "work")
- **FR-008**: System MUST allow users to filter tasks by priority level
- **FR-009**: System MUST allow users to filter tasks by tag (showing tasks that contain the specified tag)
- **FR-010**: System MUST allow users to sort tasks by priority (high → medium → low → none)
- **FR-011**: System MUST allow users to sort tasks by due date (soonest first, overdue at top)

**Due Dates & Time Management:**
- **FR-012**: System MUST allow users to optionally set a due date (YYYY-MM-DD format) when creating a task
- **FR-013**: System MUST validate due date format and reject invalid inputs with clear error messages
- **FR-014**: System MUST allow users to update or remove due dates on existing tasks
- **FR-015**: System MUST display due dates in human-readable format (e.g., "Jan 10, 2026") in all task views
- **FR-016**: System MUST mark tasks as [OVERDUE] when the due date is in the past and task is not completed
- **FR-017**: System MUST mark tasks as [DUE TODAY] when the due date is the current date
- **FR-018**: System MUST provide a dedicated "View Overdue Tasks" option in the main menu
- **FR-019**: System MUST display overdue task count in the main menu when overdue tasks exist
- **FR-020**: System MUST show "days overdue" count for each overdue task (e.g., "3 days overdue")

**Recurring Tasks:**
- **FR-021**: System MUST allow users to optionally set recurrence pattern (daily, weekly, monthly, or None) when creating a task
- **FR-022**: System MUST require a due date when recurrence pattern is set (validation rule)
- **FR-023**: System MUST automatically create a new task instance when a recurring task is marked complete
- **FR-024**: New recurring instance MUST have the same title, description, priority, tags, and recurrence pattern as the original
- **FR-025**: New recurring instance MUST have due date calculated based on pattern (daily: +1 day, weekly: +7 days, monthly: +30 days)
- **FR-026**: System MUST display recurrence pattern next to task in all views (e.g., "[RECURS: Weekly]")
- **FR-027**: System MUST allow users to update or remove recurrence pattern on existing tasks

**Backward Compatibility:**
- **FR-028**: System MUST support existing tasks without extended attributes (priority, tags, due_date, recurrence all default to None)
- **FR-029**: System MUST continue to support all existing features (add, view, update, delete, toggle completion, search, filter, sort) without modification

### Key Entities

**Task** (extended from existing entity):
- **Core attributes** (unchanged): id, title, description, completed
- **Extended attributes** (new, all optional):
  - **priority**: String value ('high', 'medium', 'low', or None) indicating task urgency
  - **tags**: List of strings for categorization (e.g., ['work', 'urgent', 'project-a'])
  - **due_date**: datetime object representing deadline (None if no deadline)
  - **recurrence**: String value ('daily', 'weekly', 'monthly', or None) for repeating tasks

**Relationships**:
- Tasks with priority can be filtered/sorted independently
- Tasks with tags can be filtered by any tag they contain
- Tasks with due dates are eligible for overdue checking
- Tasks with recurrence create new instances upon completion

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can assign priority to a task in under 5 seconds (single prompt during creation)
- **SC-002**: Users can categorize tasks with tags in under 10 seconds (comma-separated input)
- **SC-003**: Users can set a due date for a task in under 10 seconds (YYYY-MM-DD input with validation)
- **SC-004**: System displays overdue tasks with visual indicators within 1 second of viewing any task list
- **SC-005**: Users can filter tasks by priority or tags and see results in under 2 seconds
- **SC-006**: Recurring task instances are created automatically within 1 second of marking the original task complete
- **SC-007**: All new features maintain existing performance standards (operations complete in under 3 seconds for 1000 tasks)
- **SC-008**: System handles 1000 tasks with full extended attributes (priority, tags, due dates, recurrence) without performance degradation
- **SC-009**: Users can complete common organizational workflows (add task with priority and tags, view by priority, mark complete) in under 30 seconds
- **SC-010**: 100% backward compatibility - existing tasks without extended attributes display and function correctly

## Non-Functional Requirements *(optional)*

### Performance
- All filtering and sorting operations MUST complete in under 3 seconds for lists up to 1000 tasks
- Date validation MUST provide feedback within 500ms of user input
- Overdue calculation MUST complete within 1 second for lists up to 1000 tasks

### Usability
- Date format errors MUST provide clear examples (e.g., "Invalid date. Use format: YYYY-MM-DD (example: 2026-01-10)")
- Priority and tag inputs MUST have clear prompts with examples
- Overdue warnings MUST use visual indicators (text markers, not requiring color support in all terminals)

### Reliability
- Invalid date inputs MUST NOT crash the application
- Recurring task creation failures MUST be handled gracefully with error messages
- Tag parsing MUST handle edge cases (empty strings, duplicates, special characters)

## Assumptions *(optional)*

1. **Date handling**: Using Python's datetime module from standard library (no timezone support needed - dates only)
2. **Recurrence calculation**: Simple day-offset calculation (daily: +1, weekly: +7, monthly: +30) - no calendar-aware logic needed
3. **Tag storage**: Case-sensitive tags (e.g., 'Work' and 'work' are different tags)
4. **Priority levels**: Only three levels (high, medium, low) - no custom priority levels
5. **Overdue definition**: Any task with due_date < today's date and completed=False
6. **CLI limitations**: No color output required (must work on all terminal types), no browser notifications possible
7. **User input**: Users are expected to follow prompted format (validation will catch errors)
8. **Task completion**: Marking a recurring task complete is the trigger for creating the next instance
9. **Menu expansion**: Will require adding new menu options (exact count TBD during implementation)

## Dependencies *(optional)*

**External Dependencies**:
- None - all features use Python standard library (datetime module for date handling)

**Internal Dependencies**:
- Depends on existing Task model (src/models/task.py)
- Depends on existing TodoService (src/services/todo_service.py)
- Depends on existing CLI menu system (src/cli/menu.py)
- Depends on constitution v1.2.0 (extended Task attributes ratified)

**Feature Dependencies**:
- User Story 4 (Filter) depends on User Story 1 and 2 being complete (priority and tags must exist)
- User Story 5 (Overdue View) depends on User Story 3 (due dates must exist)
- User Story 6 (Sort) can be implemented independently but is more valuable after priorities/tags/dates exist
- User Story 7 (Recurring) depends on User Story 3 (requires due dates)
- User Story 8 (Menu Count) depends on User Story 5 (overdue detection logic)

## Out of Scope *(optional)*

The following are explicitly OUT OF SCOPE for this feature:

- **File system persistence**: Tasks remain in-memory only (constitutional constraint)
- **Database integration**: No persistent storage (constitutional constraint)
- **Web/GUI interface**: CLI only (constitutional constraint)
- **External libraries**: No third-party dependencies (constitutional constraint)
- **Browser notifications**: Not possible in CLI environment
- **Email/SMS reminders**: No external communication channels
- **Timezone support**: Date-only, no time-of-day handling
- **Calendar integration**: No external calendar sync
- **Advanced recurrence patterns**: No "every 2nd Tuesday" or custom patterns
- **Task dependencies**: No parent-child or blocking task relationships
- **Subtasks**: No hierarchical task structure
- **Collaboration**: No multi-user or task sharing features
- **Task history**: No audit trail or change tracking
- **Natural language date parsing**: YYYY-MM-DD format only
- **Bulk operations**: No bulk edit, bulk delete, or bulk tag assignment
- **Custom priority levels**: Limited to high/medium/low
- **Tag hierarchies**: Flat tag structure only, no tag categories or nesting

---

**Version**: 1.0
**Last Updated**: 2026-01-04
