# Developer Quickstart: Feature 003 - Advanced Task Management

**Feature**: 003-advanced-task-mgmt
**Branch**: `003-advanced-task-mgmt`
**Created**: 2026-01-04

## Overview

This guide helps developers implement and test Feature 003: priorities, tags, due dates, and recurring tasks.

---

## Development Environment

**Prerequisites**:
- Python 3.13+ installed
- Git repository cloned
- Branch `003-advanced-task-mgmt` checked out

**Setup**:
```bash
# Verify Python version
python --version  # Should be 3.13+

# Verify branch
git branch --show-current  # Should be 003-advanced-task-mgmt

# Test existing application
python main.py
```

---

## Implementation Checklist

Follow this sequence for systematic implementation:

### Phase 1: Extend Task Model
- [ ] Add 4 new optional parameters to `Task.__init__()`: priority, tags, due_date, recurrence
- [ ] Add validation for priority ('high', 'medium', 'low', None)
- [ ] Add validation for recurrence ('daily', 'weekly', 'monthly', None)
- [ ] Add helper methods: is_overdue(), is_due_today(), days_overdue()
- [ ] Add display methods: get_priority_display(), get_tags_display(), get_due_date_display(), get_recurrence_display()
- [ ] Test: Create tasks with and without extended attributes

### Phase 2: Extend TodoService
- [ ] Add filter_by_priority(priority) method
- [ ] Add filter_by_tag(tag) method
- [ ] Add get_overdue_tasks() method
- [ ] Add get_overdue_count() method
- [ ] Extend sort_tasks() to support 'priority' and 'due_date'
- [ ] Modify toggle_task_completion() to create recurring instances
- [ ] Add create_recurring_instance() helper method
- [ ] Test: All filtering and sorting operations

### Phase 3: Extend CLI Menu
- [ ] Modify display_menu() to show overdue count and 11 options
- [ ] Modify get_menu_choice() to validate 1-11
- [ ] Extend handle_add_task() with prompts for priority, tags, due date, recurrence
- [ ] Extend handle_update_task() to allow updating extended attributes
- [ ] Extend handle_view_tasks() to display extended attributes and overdue indicators
- [ ] Add handle_filter_by_priority()
- [ ] Add handle_filter_by_tags()
- [ ] Add handle_view_overdue()
- [ ] Extend handle_sort_tasks() with new sort options
- [ ] Add input helpers: validate_date_input(), parse_tags_input(), validate_priority_input()
- [ ] Update run_menu() routing for options 8-11

### Phase 4: Integration Testing
- [ ] Run application with `python main.py`
- [ ] Test all 8 user stories (see scenarios below)
- [ ] Test all edge cases (see edge case testing below)
- [ ] Verify backward compatibility (existing tasks work)
- [ ] Performance test with 1000 tasks

---

## Manual Testing Scenarios

### User Story 1: Set Task Priority

**Test Steps**:
1. Run `python main.py`
2. Select "1. Add Task"
3. Create task with priority "high"
4. Create task with priority "medium"
5. Create task with priority "low"
6. Create task with no priority (press Enter to skip)
7. Select "2. View Tasks"
8. Verify: Tasks show `[HIGH]`, `[MEDIUM]`, `[LOW]`, and no label

**Pass Criteria**: All priority levels display correctly

---

### User Story 2: Add Tags

**Test Steps**:
1. Add task with tags: "work, urgent, project-a"
2. Add task with tags: "home"
3. Add task with no tags
4. View tasks
5. Verify: Tags display correctly, comma-separated

**Pass Criteria**: Tags shown correctly, deduplicated, trimmed

---

### User Story 3: Set Due Dates

**Test Steps**:
1. Add task with due date: "2025-12-31" (past date)
2. Add task with due date: "2026-01-04" (today, use current date)
3. Add task with due date: "2026-02-01" (future date)
4. Add task with no due date
5. View tasks
6. Verify: Overdue shows "[OVERDUE]", due today shows "[DUE TODAY]"

**Pass Criteria**: Date indicators display correctly

---

### User Story 4: Filter by Priority and Tags

**Test Steps**:
1. Create 15 tasks with mixed priorities and tags
2. Select "8. Filter by Priority" → choose "High"
3. Verify: Only high-priority tasks shown
4. Return to main menu
5. Select "9. Filter by Tags" → enter "work"
6. Verify: Only tasks with 'work' tag shown

**Pass Criteria**: Filters return correct subsets

---

### User Story 5: View Overdue Tasks

**Test Steps**:
1. Create 3 tasks with past due dates (not completed)
2. Create 5 tasks with future due dates
3. Select "10. View Overdue Tasks"
4. Verify: Only 3 overdue tasks shown with days count

**Pass Criteria**: Overdue view shows only past-due incomplete tasks

---

### User Story 6: Sort Tasks

**Test Steps**:
1. Create 10 tasks with random priorities, titles, due dates
2. Select "7. Sort Tasks" → "Priority (high to low)"
3. Verify: High → medium → low → None order
4. Select "7. Sort Tasks" → "Due Date (soonest first)"
5. Verify: Overdue first, then upcoming, then None

**Pass Criteria**: All sort options work correctly

---

### User Story 7: Recurring Tasks

**Test Steps**:
1. Add task: title="Meeting", due_date="2026-01-10", recurrence="weekly"
2. Select "5. Mark Task Complete" → mark task complete
3. Verify: New task created with due_date="2026-01-17" (7 days later)
4. Verify: New task has same title, tags, priority, recurrence
5. Verify: New task is incomplete

**Pass Criteria**: Recurring instance created correctly

---

### User Story 8: Menu Overdue Count

**Test Steps**:
1. Create 3 overdue tasks
2. Return to main menu
3. Verify: Menu shows "! You have 3 overdue tasks"
4. Complete 1 overdue task
5. Return to main menu
6. Verify: Menu shows "! You have 2 overdue tasks"

**Pass Criteria**: Count updates dynamically

---

## Edge Case Testing

### Date Validation
```
Test: Enter "2026-13-01" → Error: Invalid date
Test: Enter "2026-02-30" → Error: Invalid date
Test: Enter "January 10" → Error: Use YYYY-MM-DD format
Test: Enter "" → Accepted (None)
```

### Tag Parsing
```
Test: Enter ",,," → Empty tags list
Test: Enter "work, work, work" → Single "work" tag (deduplicated)
Test: Enter "  work  , home  " → ["work", "home"] (trimmed)
Test: Enter "" → Empty tags list
```

### Recurring without Due Date
```
Test: Add task with recurrence but no due date → Error before task created
```

### Empty List Operations
```
Test: Filter on empty task list → "No tasks available to filter"
Test: View overdue with no tasks → "No overdue tasks"
```

### Backward Compatibility
```
Test: Run application with existing Phase I tasks → Tasks display without errors
Test: View old tasks → Extended attributes not shown (graceful)
Test: Update old task to add priority → Works correctly
```

---

## Performance Testing

### Load Test (1000 Tasks)

**Setup**:
```python
# Create test script to add 1000 tasks with full attributes
for i in range(1000):
    service.add_task(
        title=f"Task {i}",
        description=f"Description {i}",
        priority=random.choice(['high', 'medium', 'low', None]),
        tags=[random.choice(['work', 'home', 'urgent', 'project'])],
        due_date=date.today() + timedelta(days=random.randint(-10, 30)),
        recurrence=random.choice(['daily', 'weekly', 'monthly', None])
    )
```

**Performance Criteria**:
- [ ] View all tasks: <3 seconds
- [ ] Filter by priority: <2 seconds
- [ ] Filter by tag: <2 seconds
- [ ] Sort by priority: <3 seconds
- [ ] Sort by due date: <3 seconds
- [ ] Get overdue count: <1 second

---

## Common Issues and Fixes

### Issue: Date parsing fails
**Fix**: Ensure using `datetime.strptime(date_str, "%Y-%m-%d").date()`

### Issue: Tags not deduplicated
**Fix**: Use `list(dict.fromkeys(tags))` for order-preserving deduplication

### Issue: Recurring task creates infinite loop
**Fix**: Only trigger on explicit toggle_completion, not automatic

### Issue: Menu shows wrong option count
**Fix**: Update get_menu_choice() validation to `1 <= choice <= 11`

### Issue: Overdue count not updating
**Fix**: Recalculate count on every display_menu() call

---

## Validation Before Completion

Run full validation checklist:

**Functional Requirements** (from spec.md):
- [ ] All 29 functional requirements implemented
- [ ] All user stories independently testable

**Success Criteria** (from spec.md):
- [ ] SC-001 through SC-010 all met

**Constitutional Compliance**:
- [ ] Python 3.13+ used
- [ ] Standard library only (datetime module)
- [ ] In-memory storage maintained
- [ ] CLI interface only
- [ ] Clean, readable code
- [ ] Comprehensive docstrings
- [ ] No dead code

**Backward Compatibility**:
- [ ] Existing tasks work without modification
- [ ] All Phase I features still functional

---

## Next Steps

After successful testing:

1. Mark all tasks complete in `tasks.md`
2. Update README.md with new features
3. Create git commit: `git commit -m "Implement Feature 003: Advanced task management"`
4. Push to remote: `git push origin 003-advanced-task-mgmt`
5. Merge to main (if approved)

---

**Guide Version**: 1.0
**Last Updated**: 2026-01-04
**Status**: Ready for implementation
