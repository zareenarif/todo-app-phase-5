# Phase I Todo Application Constitution

<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0
- Amendment: Extended Task Entity Rules to support advanced task management features
- Sections affected: Task Entity Rules (added Extended Attributes subsection)
- New attributes added: priority, tags, due_date, recurrence
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md (reviewed - no changes needed)
  ✅ .specify/templates/spec-template.md (reviewed - no changes needed)
  ✅ .specify/templates/tasks-template.md (reviewed - no changes needed)
- Follow-up TODOs: None
- Impact: Feature 003 (priorities, tags, due dates, recurring tasks) can now proceed with constitutional compliance
-->

## Purpose

This project follows Spec-Driven Development (SDD). The objective of Phase I is to build a simple, reliable, in-memory Todo application that runs in the command-line interface (CLI).

All development decisions MUST be guided by this constitution and the approved specification. No implementation may begin until the specification, plan, and tasks are agreed upon.

## Core Principles

### I. Specification Before Implementation

All features MUST be specified before any code is written. The specification defines what will be built, why it is needed, and what success looks like.

**Non-negotiable rules:**
- No coding without an approved specification
- Specifications must be concrete and testable
- Requirements must be clear and unambiguous

**Rationale:** Specifications prevent scope creep, ensure alignment, and provide a shared understanding of what will be delivered. They serve as the contract between intent and implementation.

### II. Planning Before Coding

All implementations MUST have an architectural plan approved before code is generated. The plan defines how the specification will be achieved technically.

**Non-negotiable rules:**
- No coding without an approved implementation plan
- Plans must identify all components and their interactions
- Plans must consider separation of concerns

**Rationale:** Planning ensures that technical decisions are deliberate and documented. It prevents reactive coding and ensures architectural consistency.

### III. Tasks Before Execution

All work MUST be broken down into discrete, testable tasks before execution begins. Tasks define the specific steps to implement the plan.

**Non-negotiable rules:**
- No execution without a defined task list
- Each task must be independently verifiable
- Tasks must reference specific files and components

**Rationale:** Task decomposition ensures work is trackable, testable, and completable in small increments. It makes progress visible and prevents partial implementations.

### IV. Simplicity Over Complexity

The implementation MUST be as simple as possible while meeting all requirements. Complexity requires explicit justification.

**Non-negotiable rules:**
- Use Python standard library only
- No external dependencies unless absolutely necessary
- No over-engineering or premature optimization
- Clear, readable code over clever solutions

**Rationale:** Simplicity reduces maintenance burden, improves reliability, and makes the codebase accessible. Complexity is a liability unless it solves a real problem.

### V. Scope Discipline and Controlled Enhancement

This project maintains strict scope discipline. New features may be added ONLY through proper Spec-Driven Development workflow with explicit user approval.

**Non-negotiable rules:**
- All new features MUST follow SDD workflow: specification → plan → tasks → implementation
- No features may be added without user-approved specification
- Core constraints remain enforced unless explicitly amended:
  - No database integration (unless constitutionally amended)
  - No file system persistence (unless constitutionally amended)
  - No web interface or GUI (unless constitutionally amended)
- Features must maintain simplicity and architectural consistency

**Rationale:** Scope discipline ensures the project remains focused and deliverable. Controlled enhancement through SDD workflow allows deliberate expansion while preventing unplanned feature creep. Each enhancement undergoes the same rigorous specification and planning as the original implementation.

## Technical Constraints

**Programming Language:** Python 3.13 or higher MUST be used.

**Interface:** Command Line Interface (CLI) only. Menu-driven interaction using numbered options.

**Storage:** In-memory only using Python data structures (lists, dictionaries). No database, no file system, no persistent storage of any kind.

**Libraries:** Python standard library only. No external dependencies or third-party packages.

**Architecture:** Clear separation of concerns. Models, services, and CLI interface MUST be separated into distinct modules.

## Task Entity Rules

Each Todo task MUST contain the following attributes:

### Core Attributes (Required for all tasks):
- **id:** Integer, auto-incremented, unique, immutable
- **title:** String, required, non-empty
- **description:** String, optional (may be empty or None)
- **completed:** Boolean, default is False

### Extended Attributes (Added via Feature 003):
- **priority:** String, optional - one of 'high', 'medium', 'low', or None (default)
- **tags:** List of strings, optional - categories like 'work', 'home', 'personal'
- **due_date:** datetime object, optional - deadline for task completion
- **recurrence:** String, optional - recurrence pattern ('daily', 'weekly', 'monthly', or None)

Additional attributes may be added through proper SDD workflow with constitutional compliance verification.

## CLI Behavior Rules

The CLI MUST exhibit the following behavior:

- **Menu-driven interaction:** Display numbered options for all available actions
- **Clear prompts:** All user prompts must be readable and unambiguous
- **Input validation:** Gracefully handle invalid input without crashing
- **Continuous loop:** The application must continue running until the user explicitly chooses to exit
- **User feedback:** Provide clear confirmation of all actions (creation, update, deletion, completion)

## Quality Standards

All code MUST meet the following quality standards:

- **Clean and readable:** Code should be self-documenting with clear variable and function names
- **Maintainable:** Small, focused functions with single responsibilities
- **Predictable:** Behavior should be deterministic and consistent
- **No dead code:** No unused functions, variables, or imports

## Governance

This constitution supersedes all other development practices. Any amendments to this constitution MUST be documented with rationale and approved before taking effect.

**Compliance:**
- All specifications, plans, and tasks MUST be verified against this constitution
- Any complexity introduced MUST be justified explicitly
- All code generation MUST be performed by Claude Code (no manual coding by humans)

**Amendment Process:**
- Amendments require explicit documentation of the change and rationale
- Version must be incremented according to semantic versioning
- All dependent templates and documentation must be updated to reflect amendments

**Version:** 1.2.0 | **Ratified:** 2026-01-03 | **Last Amended:** 2026-01-04

## Amendment History

### Version 1.2.0 (2026-01-04)

**Amendment:** Extended Task Entity Rules to support advanced task management features

**Rationale:** Enable organizational and productivity features (priorities, tags, due dates, recurring tasks) while maintaining CLI-only and in-memory constraints. These extensions provide practical task management capabilities without introducing external dependencies or persistence requirements.

**Changes:**
- Added Extended Attributes subsection to Task Entity Rules
- Added four new optional task attributes:
  - **priority**: String ('high', 'medium', 'low', or None) for task prioritization
  - **tags**: List of strings for categorization (e.g., 'work', 'home', 'personal')
  - **due_date**: datetime object for deadline tracking
  - **recurrence**: String pattern ('daily', 'weekly', 'monthly', or None) for repeating tasks
- All new attributes are optional to maintain backward compatibility
- All new attributes use Python standard library types (str, list, datetime)

**Impact:** Enables Feature 003 (advanced task management) to proceed with constitutional compliance. Application can now support task organization, time management, and recurring workflows while maintaining Phase I architectural principles.

### Version 1.1.0 (2026-01-03)

**Amendment:** Updated Principle V from "No Features Beyond Phase I Scope" to "Scope Discipline and Controlled Enhancement"

**Rationale:** Allow controlled feature expansion through proper SDD workflow (specification → plan → tasks → implementation) while maintaining scope discipline. This enables deliberate enhancement of the application (e.g., search/filter/sort capabilities) without permitting unplanned feature creep.

**Changes:**
- Renamed Principle V title to reflect controlled enhancement approach
- Added requirement for SDD workflow for all new features
- Maintained core constraints (no database, no persistence, no GUI) unless explicitly amended
- Preserved rationale for scope discipline while enabling planned expansion

**Impact:** Enables Feature 002 (search/filter/sort) to proceed through proper SDD workflow while maintaining constitutional governance.
