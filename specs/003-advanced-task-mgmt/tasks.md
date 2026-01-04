---

description: "Task list for Feature 003: Advanced Task Management (priorities, tags, due dates, recurring tasks)"
---

# Tasks: Advanced Task Management

**Input**: Design documents from `/specs/003-advanced-task-mgmt/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/cli-interface.md (complete), quickstart.md (complete)

**Tests**: Tests are OPTIONAL and not included per constitutional constraints (manual testing only per quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, at repository root (established structure)
- Paths shown below follow single project structure from plan.md

---

## Phase 1: Verification (Prerequisites)

**Purpose**: Verify existing application is functional and ready for extension

- [X] T001 Verify Phase I + Feature 002 application runs successfully with `python main.py`
- [X] T002 Verify all existing features work (Add, View, Update, Delete, Toggle, Search/Filter, Sort, Exit)
- [X] T003 Verify constitution v1.2.0 amendment is in place (allows extended Task attributes)

---

## Phase 2: User Story 1 - Set Task Priority (Priority: P1) 🎯 MVP

**Goal**: Allow users to assign priority levels (high/medium/low) to tasks for basic task organization

**Independent Test**: Create 5 tasks with different priorities (2 high, 2 medium, 1 low), view all tasks, and verify priorities are displayed correctly next to each task

### Implementation for User Story 1

- [ ] T004 [US1] Extend Task.__init__() in src/models/task.py to accept optional priority parameter (default: None)
- [ ] T005 [US1] Add priority validation in Task.__init__() in src/models/task.py (must be 'high', 'medium', 'low', or None)
- [ ] T006 [US1] Add get_priority_display() method to Task class in src/models/task.py (returns "[HIGH]", "[MEDIUM]", "[LOW]", or "")
- [ ] T007 [US1] Modify handle_add_task() in src/cli/menu.py to prompt for priority (optional, with examples)
- [ ] T008 [US1] Add validate_priority_input() helper function in src/cli/menu.py (validates and normalizes priority input)
- [ ] T009 [US1] Modify handle_update_task() in src/cli/menu.py to allow updating priority
- [ ] T010 [US1] Modify handle_view_tasks() in src/cli/menu.py to display priority labels using get_priority_display()
- [ ] T011 [US1] Update task display in handle_search_filter_tasks() in src/cli/menu.py to show priority
- [ ] T012 [US1] Update task display in handle_sort_tasks() in src/cli/menu.py to show priority

**Checkpoint**: At this point, User Story 1 should be fully functional - users can set, update, and view task priorities

---

## Phase 3: User Story 2 - Add Tags/Categories (Priority: P1) 🎯 MVP

**Goal**: Allow users to categorize tasks with multiple tags for contextual organization

**Independent Test**: Create 10 tasks with various tag combinations ('work', 'home', 'urgent', 'project-a'), view all tasks, and verify tags are displayed for each task

### Implementation for User Story 2

- [ ] T013 [US2] Extend Task.__init__() in src/models/task.py to accept optional tags parameter (default: empty list)
- [ ] T014 [US2] Add get_tags_display() method to Task class in src/models/task.py (returns comma-joined tags or "")
- [ ] T015 [US2] Add parse_tags_input() helper function in src/cli/menu.py (parses comma-separated tags, deduplicates, trims)
- [ ] T016 [US2] Modify handle_add_task() in src/cli/menu.py to prompt for tags (optional, comma-separated)
- [ ] T017 [US2] Modify handle_update_task() in src/cli/menu.py to allow updating tags
- [ ] T018 [US2] Modify handle_view_tasks() in src/cli/menu.py to display tags using get_tags_display()
- [ ] T019 [US2] Update task display in handle_search_filter_tasks() in src/cli/menu.py to show tags
- [ ] T020 [US2] Update task display in handle_sort_tasks() in src/cli/menu.py to show tags

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can set priorities and tags independently

---

## Phase 4: User Story 3 - Set Due Dates (Priority: P1) 🎯 MVP

**Goal**: Allow users to assign due dates to tasks for deadline tracking and time management

**Independent Test**: Create 5 tasks with different due dates (2 past dates, 1 today, 2 future dates), view all tasks, and verify due dates are displayed with appropriate indicators (overdue, today, upcoming)

### Implementation for User Story 3

- [ ] T021 [US3] Extend Task.__init__() in src/models/task.py to accept optional due_date parameter (datetime.date or None)
- [ ] T022 [US3] Add is_overdue() method to Task class in src/models/task.py (check if due_date < today and not completed)
- [ ] T023 [US3] Add is_due_today() method to Task class in src/models/task.py (check if due_date == today)
- [ ] T024 [US3] Add days_overdue() method to Task class in src/models/task.py (calculate days past due date)
- [ ] T025 [US3] Add get_due_date_display() method to Task class in src/models/task.py (format as "Jan 10, 2026" or "")
- [ ] T026 [US3] Add validate_date_input() helper function in src/cli/menu.py (parse YYYY-MM-DD format, validate date)
- [ ] T027 [US3] Modify handle_add_task() in src/cli/menu.py to prompt for due date (optional, YYYY-MM-DD format with validation)
- [ ] T028 [US3] Modify handle_update_task() in src/cli/menu.py to allow updating due date
- [ ] T029 [US3] Modify handle_view_tasks() in src/cli/menu.py to display due dates and overdue indicators ([OVERDUE], [DUE TODAY])
- [ ] T030 [US3] Update task display in handle_search_filter_tasks() in src/cli/menu.py to show due dates and indicators
- [ ] T031 [US3] Update task display in handle_sort_tasks() in src/cli/menu.py to show due dates and indicators

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - MVP complete with priorities, tags, and due dates

---

## Phase 5: User Story 4 - Filter by Priority and Tags (Priority: P2)

**Goal**: Allow users to filter tasks by priority level or tags to focus on relevant work

**Independent Test**: Create 15 tasks with various priorities and tags, use filter menu to show only "high priority tasks" or only "work-tagged tasks", and verify correct subset is displayed

### Implementation for User Story 4

- [ ] T032 [US4] Implement filter_by_priority(priority) method in src/services/todo_service.py (return tasks matching priority)
- [ ] T033 [US4] Implement filter_by_tag(tag) method in src/services/todo_service.py (return tasks containing tag)
- [ ] T034 [US4] Implement handle_filter_by_priority() function in src/cli/menu.py (prompt for priority, display filtered tasks)
- [ ] T035 [US4] Implement handle_filter_by_tags() function in src/cli/menu.py (prompt for tag, display filtered tasks)
- [ ] T036 [US4] Modify display_menu() in src/cli/menu.py to add option 8 "Filter by Priority"
- [ ] T037 [US4] Modify display_menu() in src/cli/menu.py to add option 9 "Filter by Tags"
- [ ] T038 [US4] Modify get_menu_choice() in src/cli/menu.py to validate 1-9 (instead of 1-8)
- [ ] T039 [US4] Update run_menu() in src/cli/menu.py to route option 8 to handle_filter_by_priority()
- [ ] T040 [US4] Update run_menu() in src/cli/menu.py to route option 9 to handle_filter_by_tags()
- [ ] T041 [US4] Move Exit option from 8 to 10 in display_menu() in src/cli/menu.py

**Checkpoint**: At this point, User Stories 1-4 work - users can filter by priority and tags

---

## Phase 6: User Story 5 - View Overdue Tasks (Priority: P2)

**Goal**: Provide dedicated view of overdue tasks with visual warnings for deadline management

**Independent Test**: Create 5 overdue tasks and 10 current tasks, select "View Overdue Tasks" from menu, and verify only the 5 overdue tasks are shown with warning indicators

### Implementation for User Story 5

- [ ] T042 [US5] Implement get_overdue_tasks() method in src/services/todo_service.py (return tasks where is_overdue() is True)
- [ ] T043 [US5] Implement handle_view_overdue() function in src/cli/menu.py (display overdue tasks with days count)
- [ ] T044 [US5] Modify display_menu() in src/cli/menu.py to add option 10 "View Overdue Tasks"
- [ ] T045 [US5] Modify get_menu_choice() in src/cli/menu.py to validate 1-10 (instead of 1-9)
- [ ] T046 [US5] Update run_menu() in src/cli/menu.py to route option 10 to handle_view_overdue()
- [ ] T047 [US5] Move Exit option from 10 to 11 in display_menu() in src/cli/menu.py

**Checkpoint**: At this point, User Stories 1-5 work - dedicated overdue view available

---

## Phase 7: User Story 6 - Sort by Priority and Due Date (Priority: P2)

**Goal**: Allow users to sort task list by priority or due date for different organizational views

**Independent Test**: Create 10 tasks with mixed priorities, tags, and due dates, select different sort options, and verify the list reorders correctly each time

### Implementation for User Story 6

- [ ] T048 [US6] Extend sort_tasks(sort_by, reverse) method in src/services/todo_service.py to support 'priority' as sort_by option
- [ ] T049 [US6] Extend sort_tasks(sort_by, reverse) method in src/services/todo_service.py to support 'due_date' as sort_by option
- [ ] T050 [US6] Modify get_sort_choice() in src/cli/menu.py to add "Priority (high to low)" option
- [ ] T051 [US6] Modify get_sort_choice() in src/cli/menu.py to add "Priority (low to high)" option
- [ ] T052 [US6] Modify get_sort_choice() in src/cli/menu.py to add "Due Date (soonest first)" option
- [ ] T053 [US6] Modify get_sort_choice() in src/cli/menu.py to add "Due Date (latest first)" option
- [ ] T054 [US6] Update handle_sort_tasks() in src/cli/menu.py to handle new sort options (priority and due date)

**Checkpoint**: At this point, User Stories 1-6 work - full sorting capabilities available

---

## Phase 8: User Story 7 - Configure Recurring Tasks (Priority: P3)

**Goal**: Allow users to set tasks to recur on a schedule, automating repetitive task creation

**Independent Test**: Create a weekly recurring task "Team meeting", mark it complete, and verify a new instance is automatically created with due date 7 days from now

### Implementation for User Story 7

- [ ] T055 [US7] Extend Task.__init__() in src/models/task.py to accept optional recurrence parameter (default: None)
- [ ] T056 [US7] Add recurrence validation in Task.__init__() in src/models/task.py (must be 'daily', 'weekly', 'monthly', or None)
- [ ] T057 [US7] Add get_recurrence_display() method to Task class in src/models/task.py (returns "[RECURS: Daily/Weekly/Monthly]" or "")
- [ ] T058 [US7] Implement create_recurring_instance(original_task) helper method in src/services/todo_service.py (copy task with new due date)
- [ ] T059 [US7] Modify toggle_task_completion() in src/services/todo_service.py to detect recurring tasks and create new instance
- [ ] T060 [US7] Modify handle_add_task() in src/cli/menu.py to prompt for recurrence (only if due date is set)
- [ ] T061 [US7] Modify handle_update_task() in src/cli/menu.py to allow updating recurrence
- [ ] T062 [US7] Modify handle_view_tasks() in src/cli/menu.py to display recurrence pattern
- [ ] T063 [US7] Update task display in handle_search_filter_tasks() in src/cli/menu.py to show recurrence
- [ ] T064 [US7] Update task display in handle_sort_tasks() in src/cli/menu.py to show recurrence
- [ ] T065 [US7] Update handle_toggle_completion() in src/cli/menu.py to display "Creating next occurrence..." message when recurring task is completed

**Checkpoint**: At this point, User Stories 1-7 work - recurring tasks functional

---

## Phase 9: User Story 8 - Display Overdue Count in Menu (Priority: P3)

**Goal**: Display count of overdue tasks in main menu for passive awareness

**Independent Test**: Create 3 overdue tasks, return to main menu, and verify the menu shows "! You have 3 overdue tasks" warning message

### Implementation for User Story 8

- [ ] T066 [US8] Implement get_overdue_count() method in src/services/todo_service.py (count tasks where is_overdue() is True)
- [ ] T067 [US8] Modify display_menu() in src/cli/menu.py to call get_overdue_count() and display warning if count > 0
- [ ] T068 [US8] Ensure overdue count is recalculated on every display_menu() call for dynamic updates

**Checkpoint**: All user stories complete - application has full advanced task management capabilities

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [ ] T069 [P] Add comprehensive docstrings to all new Task methods in src/models/task.py
- [ ] T070 [P] Add comprehensive docstrings to all new service methods in src/services/todo_service.py
- [ ] T071 [P] Add comprehensive docstrings to all new CLI helpers in src/cli/menu.py
- [ ] T072 [P] Add comprehensive docstrings to all new CLI handlers in src/cli/menu.py
- [ ] T073 Review code for simplicity and readability per constitutional quality standards
- [ ] T074 Update README.md with new features section documenting priorities, tags, due dates, and recurring tasks
- [ ] T075 Run full manual test suite from quickstart.md (all 8 user story scenarios)
- [ ] T076 Verify all edge cases from spec.md (invalid dates, empty tags, duplicate tags, recurring without due date, etc.)
- [ ] T077 Verify backward compatibility (existing tasks without extended attributes display correctly)
- [ ] T078 Performance test with 100+ tasks to ensure <3 second operations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Verification (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Verification - can start immediately after
- **User Story 2 (Phase 3)**: Depends on Verification - can run in parallel with US1 (different attributes)
- **User Story 3 (Phase 4)**: Depends on Verification - can run in parallel with US1/US2 (different attributes)
- **User Story 4 (Phase 5)**: Depends on US1 and US2 completion (filters require priority and tags to exist)
- **User Story 5 (Phase 6)**: Depends on US3 completion (overdue detection requires due dates)
- **User Story 6 (Phase 7)**: Depends on US1 and US3 completion (sorting by priority and due date)
- **User Story 7 (Phase 8)**: Depends on US3 completion (recurring requires due dates)
- **User Story 8 (Phase 9)**: Depends on US5 completion (menu count uses overdue detection logic)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

**P1 Stories (MVP) - Can run in parallel**:
- User Story 1 (Priority): Independent - extends Task with priority attribute
- User Story 2 (Tags): Independent - extends Task with tags attribute
- User Story 3 (Due Dates): Independent - extends Task with due_date attribute

**P2 Stories - Depend on P1 completion**:
- User Story 4 (Filter): Depends on US1 (priority) and US2 (tags)
- User Story 5 (Overdue View): Depends on US3 (due dates)
- User Story 6 (Sort): Depends on US1 (priority) and US3 (due date)

**P3 Stories - Depend on earlier stories**:
- User Story 7 (Recurring): Depends on US3 (due dates required for recurrence)
- User Story 8 (Menu Count): Depends on US5 (uses overdue detection)

### Within Each User Story

Tasks within a user story are sequential unless marked [P] for parallel execution. Follow the order shown for each phase.

### Parallel Opportunities

**MVP Development (P1 Stories)**:
If team has 3 developers:
- Developer A: User Story 1 (Priority) - Tasks T004-T012
- Developer B: User Story 2 (Tags) - Tasks T013-T020
- Developer C: User Story 3 (Due Dates) - Tasks T021-T031
- All can work in parallel after Verification phase complete

**Polish Phase**:
- T069-T072 can all run in parallel (different documentation tasks)

**Note**: Tasks within same file (e.g., multiple modifications to menu.py) must run sequentially to avoid conflicts.

---

## Parallel Example: MVP Development

```bash
# After Verification (T001-T003) complete, launch 3 parallel tracks:

Track A - Priority (US1):
  T004-T012: Extend Task with priority, add CLI prompts and display

Track B - Tags (US2):
  T013-T020: Extend Task with tags, add CLI prompts and display

Track C - Due Dates (US3):
  T021-T031: Extend Task with due_date, add CLI prompts and display

# Once all 3 complete, MVP ready for testing and deployment
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only) 🎯

1. Complete Phase 1: Verification (T001-T003)
2. Complete Phase 2: User Story 1 - Priority (T004-T012)
3. Complete Phase 3: User Story 2 - Tags (T013-T020)
4. Complete Phase 4: User Story 3 - Due Dates (T021-T031)
5. **STOP and VALIDATE**: Test all 3 MVP stories independently
6. Run basic manual tests from quickstart.md
7. **Deploy/demo if ready** - MVP delivers core organizational features

**MVP Delivers**: Users can set priorities, add tags, and set due dates - foundation for all advanced task management

---

### Incremental Delivery (Priority Order)

1. Complete Verification → Foundation ready
2. Add User Story 1 (Priority) → Test independently → Deploy/Demo
3. Add User Story 2 (Tags) → Test independently → Deploy/Demo
4. Add User Story 3 (Due Dates) → Test independently → Deploy/Demo (MVP! 🎯)
5. Add User Story 4 (Filter) → Test independently → Deploy/Demo
6. Add User Story 5 (Overdue View) → Test independently → Deploy/Demo
7. Add User Story 6 (Sort Enhancements) → Test independently → Deploy/Demo
8. Add User Story 7 (Recurring) → Test independently → Deploy/Demo
9. Add User Story 8 (Menu Count) → Test independently → Deploy/Demo
10. Add Polish tasks → Final release

Each user story adds value without breaking previous stories.

---

### Parallel Team Strategy (Optional)

With 2-3 developers:

**Week 1: MVP (P1 Stories)**
- Developer A: US1 (Priority)
- Developer B: US2 (Tags)
- Developer C: US3 (Due Dates)
- Converge for testing and integration

**Week 2: Enhanced Features (P2 Stories)**
- Developer A: US4 (Filter) + US6 (Sort)
- Developer B: US5 (Overdue View)
- Converge for testing

**Week 3: Advanced Features (P3 Stories)**
- Developer A: US7 (Recurring)
- Developer B: US8 (Menu Count)
- Both: Polish tasks

**Recommended for Feature 003**: Single developer, sequential implementation in priority order (simplest approach for extending existing files).

---

## Task Statistics

**Total Tasks**: 78

- Verification: 3 tasks (T001-T003)
- User Story 1 (P1): 9 tasks (T004-T012) 🎯 MVP Component 1
- User Story 2 (P1): 8 tasks (T013-T020) 🎯 MVP Component 2
- User Story 3 (P1): 11 tasks (T021-T031) 🎯 MVP Component 3
- User Story 4 (P2): 10 tasks (T032-T041)
- User Story 5 (P2): 6 tasks (T042-T047)
- User Story 6 (P2): 7 tasks (T048-T054)
- User Story 7 (P3): 11 tasks (T055-T065)
- User Story 8 (P3): 3 tasks (T066-T068)
- Polish: 10 tasks (T069-T078)

**Parallel Opportunities**: 4 tasks can run in parallel in Polish phase (T069-T072)
**Sequential Tasks**: 74 tasks must run in sequence (modifying same files)

**MVP Scope**: 31 tasks (T001-T031) - Verification + User Stories 1, 2, 3

**Estimated Effort** (based on quickstart.md):
- Verification: ~15 minutes
- User Story 1 (Priority): ~1 hour
- User Story 2 (Tags): ~1 hour
- User Story 3 (Due Dates): ~1.5 hours
- User Story 4 (Filter): ~1 hour
- User Story 5 (Overdue View): ~45 minutes
- User Story 6 (Sort): ~45 minutes
- User Story 7 (Recurring): ~1.5 hours
- User Story 8 (Menu Count): ~30 minutes
- Polish: ~1.5 hours

**Total Estimated Time**: ~10-12 hours for complete implementation (matches quickstart estimate)

---

## Notes

- Tasks follow constitutional principle: specification → planning → tasks → execution
- Each task is specific with exact file paths for immediate executability
- User stories are independently testable after their phase completes
- No automated tests per constitutional constraints (manual testing via quickstart.md)
- Verify against acceptance scenarios from spec.md after completing each user story
- Stop at any checkpoint to validate story independently
- Follow constitutional quality standards: clean code, small functions, comprehensive docstrings
- All code must be generated by Claude Code (no manual coding)
- Backward compatibility maintained throughout (existing tasks work without modification)

---

## Validation Checklist

After completing all tasks, verify:

**Functional Requirements (from spec.md)**:
- [ ] FR-001 through FR-029 all satisfied

**Success Criteria (from spec.md)**:
- [ ] SC-001 through SC-010 all met

**Constitutional Compliance**:
- [ ] Python 3.13+ used
- [ ] Standard library only (datetime module)
- [ ] In-memory operations (no persistence)
- [ ] CLI interface only
- [ ] Separation of concerns (models, services, CLI)
- [ ] Clean, readable code
- [ ] Comprehensive docstrings
- [ ] No dead code

**User Story Acceptance Scenarios (from spec.md)**:
- [ ] User Story 1: All 4 acceptance scenarios pass
- [ ] User Story 2: All 4 acceptance scenarios pass
- [ ] User Story 3: All 7 acceptance scenarios pass
- [ ] User Story 4: All 4 acceptance scenarios pass
- [ ] User Story 5: All 4 acceptance scenarios pass
- [ ] User Story 6: All 4 acceptance scenarios pass
- [ ] User Story 7: All 6 acceptance scenarios pass
- [ ] User Story 8: All 3 acceptance scenarios pass

**Edge Cases (from spec.md)**:
- [ ] Invalid date format handled gracefully
- [ ] Past due date on creation accepted
- [ ] Empty tags handled (returns empty list)
- [ ] Duplicate tags deduplicated
- [ ] Special characters in tags accepted
- [ ] Recurring task without due date rejected
- [ ] Completed recurring task creation failures handled
- [ ] Priority/tag filter on empty list handled
- [ ] Sorting with all None values handled
- [ ] Overdue task marked complete removed from overdue view

**Backward Compatibility**:
- [ ] Existing Phase I + Feature 002 tasks display correctly
- [ ] All existing features still functional
- [ ] Extended attributes optional (None/empty defaults work)

**Performance (from spec.md)**:
- [ ] All operations complete in <3 seconds for 1000 tasks
- [ ] Filter operations complete in <2 seconds
- [ ] Overdue calculation completes in <1 second
