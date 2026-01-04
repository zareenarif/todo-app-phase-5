# Implementation Plan: Advanced Task Management

**Branch**: `003-advanced-task-mgmt` | **Date**: 2026-01-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-advanced-task-mgmt/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Feature 003 adds advanced task management capabilities to the existing CLI todo application: task priorities (high/medium/low), tags/categories, due dates with overdue tracking, and recurring tasks. All features use Python standard library only (datetime module), maintain in-memory storage, and extend the existing Task model with optional attributes for backward compatibility. The implementation extends the three-layer architecture (models, services, CLI) with enhanced input handling, filtering/sorting capabilities, and automated recurring task creation.

## Technical Context

**Language/Version**: Python 3.13 or higher (existing constraint from constitution)
**Primary Dependencies**: Python standard library only - datetime module for date handling (no external packages)
**Storage**: In-memory using Python lists and dictionaries (existing dual-storage pattern)
**Testing**: Manual testing against acceptance scenarios from spec.md (no automated tests per constitution)
**Target Platform**: Command Line Interface (CLI) - Windows, Linux, macOS via Python interpreter
**Project Type**: Single project (established structure: src/models/, src/services/, src/cli/)
**Performance Goals**: All operations complete in <3 seconds for 1000 tasks (existing standard maintained)
**Constraints**:
- No external dependencies (constitutional constraint)
- No file system persistence (constitutional constraint)
- CLI only, no GUI/web interface (constitutional constraint)
- No color output required (must work on all terminal types)
- Backward compatible with existing tasks (extended attributes optional)
**Scale/Scope**: Single-user, in-memory task management with up to 1000 tasks expected

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Version**: 1.2.0 (ratified 2026-01-04)

### Core Principles Compliance

✅ **Principle I - Specification Before Implementation**: PASS
- Complete specification created with 8 user stories, 29 functional requirements, 10 success criteria
- All requirements are concrete and testable
- Feature approved for implementation

✅ **Principle II - Planning Before Coding**: PASS
- This implementation plan being created before any code
- Architectural decisions documented below
- Component interactions defined

✅ **Principle III - Tasks Before Execution**: PENDING
- Task breakdown will be created via `/sp.tasks` command after this plan
- Tasks will reference specific files and components
- Each task will be independently verifiable

✅ **Principle IV - Simplicity Over Complexity**: PASS
- Uses Python standard library only (datetime module)
- No external dependencies introduced
- Extends existing architecture without adding new layers
- Clear, straightforward data structures (strings, lists, datetime objects)

✅ **Principle V - Scope Discipline and Controlled Enhancement**: PASS
- Feature follows full SDD workflow (specification → plan → tasks → implementation)
- Constitution v1.2.0 amendment explicitly approves extended Task attributes
- Core constraints maintained (no database, no persistence, no GUI)

### Technical Constraints Compliance

✅ **Programming Language**: Python 3.13+ (existing requirement maintained)
✅ **Interface**: CLI only with menu-driven interaction (maintained)
✅ **Storage**: In-memory using lists and dictionaries (maintained)
✅ **Libraries**: Python standard library only - datetime module (constitutional compliance)
✅ **Architecture**: Maintains three-layer separation (models, services, CLI)

### Task Entity Rules Compliance

✅ **Core Attributes**: Unchanged (id, title, description, completed)
✅ **Extended Attributes**: Explicitly ratified in constitution v1.2.0:
- priority: String ('high', 'medium', 'low', or None)
- tags: List of strings
- due_date: datetime object or None
- recurrence: String ('daily', 'weekly', 'monthly', or None)

### CLI Behavior Rules Compliance

✅ **Menu-driven interaction**: Menu will be extended with new options
✅ **Clear prompts**: All new inputs have examples and format guidance
✅ **Input validation**: Date format validation, tag parsing, priority validation
✅ **Continuous loop**: Maintained (no changes to main loop structure)
✅ **User feedback**: Clear confirmation for all new operations

### Quality Standards Compliance

✅ **Clean and readable**: Following existing code style
✅ **Maintainable**: Small, focused functions with single responsibilities
✅ **Predictable**: Deterministic behavior, no external dependencies
✅ **No dead code**: Only adding necessary functionality

**GATE STATUS**: ✅ PASS - All constitutional requirements met, no violations requiring justification

**Re-check after Phase 1**: Will verify data model and contracts maintain compliance

## Project Structure

### Documentation (this feature)

```text
specs/003-advanced-task-mgmt/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output - technical decisions
├── data-model.md        # Phase 1 output - extended Task entity
├── quickstart.md        # Phase 1 output - developer guide
├── contracts/
│   └── cli-interface.md # Phase 1 output - CLI specifications
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete, all pass)
└── tasks.md             # Phase 2 output (via /sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── task.py              # MODIFIED: Add priority, tags, due_date, recurrence attributes
├── services/
│   └── todo_service.py      # MODIFIED: Add filter/sort by priority/tags/date, recurring logic
└── cli/
    └── menu.py              # MODIFIED: Add handlers for new features, menu options

tests/                       # NOT USED (manual testing per constitution)
main.py                      # UNCHANGED: Entry point
```

**Structure Decision**: Single project structure maintained. All changes are extensions to existing files in the established three-layer architecture. No new modules or files required - all functionality fits naturally into the existing Task model, TodoService business logic layer, and CLI menu interface.

## Complexity Tracking

**No constitutional violations** - complexity tracking not required.

All features comply with constitutional constraints:
- Uses Python standard library only (datetime module)
- Maintains in-memory storage
- Extends existing architecture without adding layers
- No external dependencies

## Phase 0: Research & Technical Decisions

### Research Areas

1. **Python datetime Module Usage**
   - Date parsing and validation (YYYY-MM-DD format)
   - Date comparison for overdue detection (due_date < today)
   - Date arithmetic for recurring tasks (timedelta operations)
   - Human-readable date formatting (strftime)

2. **Date Validation Strategy**
   - Format validation: YYYY-MM-DD only
   - Value validation: Valid calendar dates
   - Edge case handling: Invalid dates, leap years, month boundaries

3. **Tag Parsing and Storage**
   - Comma-separated input parsing
   - Deduplication strategy
   - Case sensitivity decision
   - Special character handling

4. **Recurring Task Logic**
   - Trigger point: When task is marked complete
   - Date calculation: Simple day-offset (daily: +1, weekly: +7, monthly: +30)
   - Attribute copying: title, description, priority, tags, recurrence (not completion status)
   - Error handling: What if new task creation fails

5. **Priority/Tag Filtering**
   - Filter implementation: List comprehension vs filter()
   - Multiple tag support: Match any tag vs match all tags
   - Performance considerations for 1000 tasks

6. **Menu Extension Strategy**
   - How many new menu options needed
   - Menu numbering scheme (extend existing 1-8)
   - Grouping related features (filter by priority vs filter by tags)

### Decisions Summary

**See research.md** for complete technical decisions and rationale.

## Phase 1: Design Artifacts

### Data Model

**See data-model.md** for complete entity specifications.

**Summary**:
- Extend existing Task class with 4 new optional attributes
- priority: str | None ('high', 'medium', 'low')
- tags: list[str] (empty list if no tags)
- due_date: datetime.date | None (using datetime.date for date-only values)
- recurrence: str | None ('daily', 'weekly', 'monthly')
- All validation rules documented
- Backward compatibility maintained (existing tasks work without changes)

### Contracts

**See contracts/cli-interface.md** for complete CLI specifications.

**Summary**:
- Extended "Add Task" flow: Add prompts for priority, tags, due date, recurrence
- Extended "Update Task" flow: Allow updating new attributes
- Extended "View Tasks" display: Show priority, tags, due date, recurrence, overdue indicators
- New menu options (exact count TBD during contract design):
  - Filter by Priority
  - Filter by Tags
  - View Overdue Tasks
  - Enhanced Sort (add priority and due date options)
- Input validation specifications for all new fields
- Error message templates for validation failures

### Developer Quickstart

**See quickstart.md** for complete development guide.

**Summary**:
- Development environment setup (unchanged)
- New feature testing scenarios for each user story
- Manual test checklist for all 8 user stories
- Edge case validation procedures
- Performance testing guide (ensure <3 second operations)
- Backward compatibility testing (existing tasks still work)

## Implementation Approach

### Modified Components

**1. src/models/task.py** (Task Entity)
- Add 4 new optional parameters to `__init__`: priority, tags, due_date, recurrence
- Add validation for priority (must be 'high', 'medium', 'low', or None)
- Add validation for recurrence (must be 'daily', 'weekly', 'monthly', or None)
- Add validation for tags (must be list of strings)
- Add helper methods:
  - `is_overdue()` → bool (check if due_date < today and not completed)
  - `is_due_today()` → bool (check if due_date == today)
  - `days_overdue()` → int (calculate days since due date)
  - `get_priority_display()` → str (return "[HIGH]", "[MEDIUM]", "[LOW]", or "")
  - `get_tags_display()` → str (return comma-joined tags or "")
  - `get_due_date_display()` → str (return formatted date or "")
  - `get_recurrence_display()` → str (return "[RECURS: Daily/Weekly/Monthly]" or "")

**2. src/services/todo_service.py** (Business Logic)
- Add filtering methods:
  - `filter_by_priority(priority: str)` → list[Task]
  - `filter_by_tag(tag: str)` → list[Task]
  - `get_overdue_tasks()` → list[Task]
- Add sorting enhancements:
  - Extend existing `sort_tasks()` to support 'priority' and 'due_date' as sort_by options
  - Priority sort order: high → medium → low → None
  - Due date sort order: overdue first, then soonest, then None
- Add recurring task logic:
  - Modify existing `toggle_task_completion()` to check for recurrence pattern
  - `create_recurring_instance(original_task: Task)` → Task (helper method)
  - Calculate new due date using timedelta (daily: +1, weekly: +7, monthly: +30)
  - Copy all attributes except completion status
- Add overdue detection:
  - `get_overdue_count()` → int (count tasks where is_overdue() is True)

**3. src/cli/menu.py** (User Interface)
- Modify `display_menu()`:
  - Add overdue warning if count > 0: "! You have [N] overdue task(s)"
  - Add new menu options (exact numbers TBD, likely expanding to 11-12 options)
- Modify `get_menu_choice()`:
  - Update validation range to accept new option count
- Modify `handle_add_task()`:
  - Add prompts for priority (optional, default None)
  - Add prompts for tags (optional, comma-separated)
  - Add prompts for due date (optional, YYYY-MM-DD format with validation)
  - Add prompts for recurrence (optional, only if due date is set)
- Modify `handle_update_task()`:
  - Add prompts for updating priority, tags, due date, recurrence
- Modify `handle_view_tasks()`:
  - Update display to show priority, tags, due date, recurrence
  - Add overdue indicators ("[OVERDUE]", "[DUE TODAY]")
- Add new handlers:
  - `handle_filter_by_priority()` → display filtered list
  - `handle_filter_by_tags()` → display filtered list
  - `handle_view_overdue()` → display overdue tasks with days count
- Modify `handle_search_filter_tasks()` (existing Feature 002 handler):
  - Optionally extend to include priority/tag filters (design decision during contracts)
- Modify `handle_sort_tasks()` (existing Feature 002 handler):
  - Add priority and due date to sort options menu
- Add input helpers:
  - `validate_date_input(date_str: str)` → datetime.date | None
  - `parse_tags_input(tags_str: str)` → list[str]
  - `validate_priority_input(priority_str: str)` → str | None

### Key Algorithms

**Date Validation**:
```python
def validate_date_input(date_str):
    if not date_str.strip():
        return None  # No date entered
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "INVALID"  # Signal error
```

**Tag Parsing**:
```python
def parse_tags_input(tags_str):
    if not tags_str.strip():
        return []
    tags = [tag.strip() for tag in tags_str.split(',')]
    tags = [tag for tag in tags if tag]  # Remove empty strings
    return list(set(tags))  # Deduplicate
```

**Recurring Task Creation**:
```python
def create_recurring_instance(original_task):
    from datetime import timedelta

    offset_days = {
        'daily': 1,
        'weekly': 7,
        'monthly': 30
    }

    new_due_date = original_task.due_date + timedelta(days=offset_days[original_task.recurrence])

    return Task(
        task_id=next_id,
        title=original_task.title,
        description=original_task.description,
        completed=False,  # New instance starts incomplete
        priority=original_task.priority,
        tags=original_task.tags.copy(),
        due_date=new_due_date,
        recurrence=original_task.recurrence
    )
```

**Overdue Detection**:
```python
def is_overdue(self):
    if self.completed or self.due_date is None:
        return False
    from datetime import date
    return self.due_date < date.today()
```

### Testing Strategy

**Manual Testing Per User Story** (from spec.md):

1. **Priority (US1)**: Create 5 tasks with different priorities, verify display
2. **Tags (US2)**: Create 10 tasks with various tags, verify display
3. **Due Dates (US3)**: Create tasks with past/today/future dates, verify indicators
4. **Filter (US4)**: Create 15 tasks, filter by priority and tags
5. **Overdue View (US5)**: Create overdue tasks, verify dedicated view
6. **Sort (US6)**: Create mixed tasks, test all sort options
7. **Recurring (US7)**: Create recurring task, complete it, verify new instance
8. **Menu Count (US8)**: Create overdue tasks, verify menu warning

**Edge Case Testing** (from spec.md):
- Invalid date formats
- Empty tags
- Duplicate tags
- Recurring without due date
- All-None sorting
- Filter on empty list

**Performance Testing**:
- Create 1000 tasks with full attributes
- Test all operations complete in <3 seconds
- Verify no degradation with extended attributes

**Backward Compatibility Testing**:
- Existing tasks without extended attributes must display correctly
- All existing features (add, view, update, delete, toggle, search, filter, sort) must work unchanged
- Menu must be accessible and navigable

## Risk Assessment

### Technical Risks

1. **Date Parsing Edge Cases**
   - **Risk**: Invalid dates crash application
   - **Mitigation**: Comprehensive try/except around datetime.strptime with clear error messages

2. **Recurring Task Infinite Loops**
   - **Risk**: Bug in recurring logic creates tasks continuously
   - **Mitigation**: Recurring trigger only on explicit toggle_completion call, not automatic

3. **Menu Complexity**
   - **Risk**: Too many menu options confuse users
   - **Mitigation**: Group related features, clear option labels, maintain consistent numbering

4. **Backward Compatibility**
   - **Risk**: Existing tasks fail with new attributes
   - **Mitigation**: All new attributes optional with defaults, test with old tasks

### Performance Risks

1. **Large Task Lists**
   - **Risk**: 1000 tasks with tags/dates slow down operations
   - **Mitigation**: Simple O(n) operations maintained, no nested loops for filtering

2. **Date Calculations**
   - **Risk**: Overdue detection on every view slows render
   - **Mitigation**: datetime comparisons are O(1), acceptable for 1000 tasks

### User Experience Risks

1. **Too Many Prompts**
   - **Risk**: Adding task becomes tedious with 6+ prompts
   - **Mitigation**: All new attributes optional (can skip with Enter)

2. **Date Format Confusion**
   - **Risk**: Users don't know YYYY-MM-DD format
   - **Mitigation**: Clear examples in prompts, helpful error messages with format reminder

## Dependencies

### External Dependencies
- None (Python standard library only per constitution)

### Internal Dependencies
- Existing Task model (src/models/task.py) - will be extended
- Existing TodoService (src/services/todo_service.py) - will be extended
- Existing CLI menu (src/cli/menu.py) - will be extended
- Constitution v1.2.0 (extended attributes ratified)

### Feature Dependencies
- Feature 002 (search/filter/sort) is complete - will enhance existing sort functionality
- No blocking dependencies - Feature 003 can proceed immediately

## Success Metrics

From spec.md Success Criteria:

- **SC-001**: Priority assignment in <5 seconds ✓ (single prompt)
- **SC-002**: Tag categorization in <10 seconds ✓ (comma-separated input)
- **SC-003**: Due date setting in <10 seconds ✓ (YYYY-MM-DD input)
- **SC-004**: Overdue display in <1 second ✓ (simple date comparison)
- **SC-005**: Filter operations in <2 seconds ✓ (O(n) list comprehension)
- **SC-006**: Recurring instance creation in <1 second ✓ (simple object creation)
- **SC-007**: Maintain <3 second performance ✓ (no complex operations added)
- **SC-008**: Handle 1000 tasks with extended attributes ✓ (simple data types)
- **SC-009**: Common workflows in <30 seconds ✓ (streamlined prompts)
- **SC-010**: 100% backward compatibility ✓ (optional attributes with defaults)

## Next Steps

1. ✅ **Phase 0 Complete**: research.md generated with all technical decisions documented
2. ✅ **Phase 1 Complete**: All design artifacts generated:
   - data-model.md: Extended Task entity with priorities, tags, due dates, recurrence
   - contracts/cli-interface.md: Complete CLI interface specifications for 11 menu options
   - quickstart.md: Developer guide with testing scenarios and implementation checklist
   - Agent context updated (CLAUDE.md)
3. **Phase 2 (Next)**: Run `/sp.tasks` to generate task breakdown
4. **Phase 3 (After tasks)**: Run `/sp.implement` to execute implementation
5. **Phase 4 (Final)**: Manual testing per quickstart.md, then git commit and push

---

**Plan Version**: 1.0
**Last Updated**: 2026-01-04
**Status**: Phase 0 and Phase 1 complete - Ready for task generation (/sp.tasks)
