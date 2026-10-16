# FacilityFix — requirements and gap analysis

## Inspection baseline

Inspected 2026-10-12 on branch `arena/db370694-oppilot`, starting commit `5f5fdf2`.
The repository contained only README.md (`# oppilot`). No Week 3 document,
application, schema, dependencies, tests, or established authentication policy exists.
Python 3.11.2 and SQLite 3.40.1 are available. Flask is not installed.
The following inspection paragraph records the initial baseline. See the updated
checklist and verification record below for implementation evidence.

Statuses: **V** = implemented and verified at the stated automated/HTTP level;
**P** = partially verified, with browser checks outstanding. No formal audit implied.
Evidence: `docs/verification.md` and the 45-test suite under `tests/`.

## Requirements checklist

| Requirement | Status | Requirement coverage (evidence in verification record) |
| --- | --- | --- |
| FacilityFix identity, hypothetical internship context, no real institutional-user claims | V | Accurate UI and documentation |
| HTML/CSS/JavaScript, Python/Flask, persistent SQLite, Git/GitHub | V | Minimal application; no substituted frameworks |
| Modular app/config, routes, services, database, templates, static files, tests, docs | V | Implemented structure; README updated in documentation phase |
| Minimal compatible dependency manifest and repeatable startup | V | Flask 3.1.3 and Pillow 12.3.0 installed; pip check passed |
| Authentication and account provisioning | V | Confirmed local username/password provisioning for all roles; CLI/login tests pass |
| Exactly Student, Faculty, Staff, Facility Coordinator | V | Database constraints and server permission checks |
| Password hashing, safe sessions, secret configuration, logout | V | Hashing, session rotation, required secret and logout tested |
| Protected routes and server-side role checks | V | Test unauthenticated and wrong-role access |
| Reporters see only their own issues and attachments | V | Test ownership and URL manipulation |
| No reporter editing/deletion or coordinator-field mutation | V | Server enforcement and negative tests |
| Required category with six exact approved names | V | Electrical; IT & Computer; Furniture; Plumbing; Cleanliness & Sanitation; Other |
| Required non-whitespace description, maximum length, useful errors and retained fields | V | Approved 2,000 characters; boundary tests pass |
| Required building/block, floor, room/area text inputs | V | No invented campus directory; bounded validated inputs |
| Suggested Low/Medium/High priority distinct from coordinator final priority | V | Validate values; final priority remains separate |
| Optional single photo attachment | V | Approved JPEG/PNG, 2 MiB, Pillow; valid/invalid upload tests pass |
| Secure uploads and private serving | V | Validate content and size, generated names, controlled directory, no executable/path access |
| SQLite identity and issue data, constraints, foreign keys, parameterized queries | V | Two-table schema implemented and tested |
| Repeatable non-destructive database initialization | V | Document and test |
| Atomic updates and safe database errors | V | Failure tests and transaction review |
| Own history and issue details | V | Identifier, category, description, location, priorities, status and timestamps |
| Resolution note and resolved-by name visible when available | V | Persist and display escaped text |
| Exactly Submitted, In Progress, Resolved, Reopened | V | Central business rules and schema constraints |
| Submitted → In Progress by coordinator | V | Positive and negative workflow tests |
| In Progress → Resolved by coordinator with resolution note and resolved-by name | V | Required-field validation and persistence tests |
| Resolved → Reopened only by owning reporter | V | Ownership and current-status checks |
| Reopened → In Progress by coordinator, then repeat resolution | V | Test full cycle |
| Reject all unsupported transitions without data changes | V | Central service and negative tests |
| Relevant update/status tracking information | V | Smallest schema supporting timestamps and resolution visibility; no established history design |
| Coordinator all-issue listing and details | V | Actual database queries and role-specific controls |
| Five database-derived counts | V | All Issues, Submitted, In Progress, Resolved, Reopened |
| Combined status/category/building/date/priority filters | V | Query validation, correct results and empty states |
| Coordinator final-priority changes | V | Validate and persist independently of reporter suggestion |
| Coordinator resolution management | V | Save note, resolved-by name and update information |
| Role-specific navigation and all required screen responsibilities | V | Authentication, history, report, tracking, coordinator overview/details |
| Clear responsive visual design without unapproved frameworks | P | Semantic HTML, CSS and small JavaScript enhancements |
| Accessible forms and controls | P | Visible labels, required markers, focus, contrast, keyboard operation |
| Textual status/priority indicators | V | Consistent wording; no reliance on color alone |
| Accurate success/error/loading/empty states | V | No simulated results or decorative controls |
| Practical duplicate-submission protection | P | Server/browser safeguards and redirect after success |
| Desktop/mobile layout verification | P | Representative viewports; navigation, forms, tables, errors and actions |
| Safe errors for missing/invalid/unauthorized requests, uploads and database failures | V | No sensitive details or stack traces to users |
| Security review | V | Authorization, validation, CSRF, SQL parameters, escaping, sessions, secrets, upload privacy |
| Authentication tests | V | Login/protected screens and unauthorized actions |
| Reporting tests | V | Valid submission, missing fields, category/priority rejection, whitespace, safe photos |
| Tracking and permission tests | V | Own history/details; deny cross-user reads and mutations |
| Workflow tests | V | Every permitted transition, resolution requirements and rejected transitions |
| Coordinator tests | V | Listing, priority, resolution, combined filters, real counts |
| Persistence and failure tests | V | Restart app against same database; rejected operations do not corrupt data |
| Startup/database/screen/end-to-end verification | V | Execute and record actual outcomes |
| README delivery | V | Overview, actual stack/structure, prerequisites, install/config/init/run/test, features, limitations |
| No unapproved scope additions | V | Review against exclusions before delivery |
| No secrets, real personal data or generated data committed | V | Ignore configuration/data/uploads and review diff |

## Decisions and remaining gaps

All four clarification questions were answered before implementation: local username
provisioning, approved text limits, 2 MiB JPEG/PNG with Pillow, and exact UTC date/final
priority filtering. No consequential decision is currently blocked.

The **P** rows are deliberately not marked complete: responsive CSS, semantic forms,
focus styles and duplicate-submit JS exist, but viewport rendering and actual keyboard/
back-forward-cache behavior have not been checked in a browser. Sequential server-side
resubmission rejection is covered by tests; simultaneous exactly-once submission is
not guaranteed.

For rows marked **V**, verification means the implemented behavior is covered by the
executed automated suite, live HTTP checks or source/dependency review as appropriate;
it does not assert visual, production or formal security certification.

## Phase evidence

See `docs/verification.md` for per-phase outcomes and commands. Phases 1–8 and 10–11
are implemented with the recorded checks; phase 9 browser checks and the corresponding
phase 12 release gate remain open. Phase 13 documentation describes the actual state.
No real personal data, example issues or default accounts were inserted into the
normal database. No secrets, database files or uploaded photos are tracked.
