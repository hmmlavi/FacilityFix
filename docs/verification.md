# Verification and development record

Date: 2026-10-12. Branch: `arena/db370694-oppilot`.

## Confirmed choices

User approved locally provisioned username/password accounts, 12–128-character
passwords, 2,000-character descriptions and resolution notes, 100-character location
and name fields, optional JPEG/PNG photos up to 2 MiB, Pillow, and an exact UTC
submission-date filter with priority filtering on coordinator final priority.

Minor implementation choices: case-insensitive ASCII usernames; an eight-hour signed
session; optional suggested priority; initially unassigned final priority; exact
building filtering; latest resolution/timestamps rather than a separate history
module. Image decoding rejects animation and enforces a 16-million-pixel resource
ceiling. No product role, category, status or integration was added.

## Phase record

1. **Inspection:** Only the nine-byte `README.md` existed. Git was clean. Python
   3.11.2, SQLite 3.40.1, unittest and venv available; Flask absent. No Week 3 document.
2. **Gap analysis:** Created the requirements checklist; all behavior initially absent.
3. **Clarification:** Obtained the decisions above before schema/authentication design.
4. **Structure:** Added modular Flask factory/configuration, packages, dependency
   manifest and ignore rules. Factory import and dependency checks passed.
5. **Database/business logic:** Implemented two-table schema, query layer, constraints,
   input vocabulary/validation and centralized workflow. Initialization ran twice;
   unsupported-category validation and transition-map checks passed.
6. **Authentication:** Added provisioning, hashed passwords, session login/logout and
   role guards. Initial CLI test exposed missing application context; corrected it.
   Retest passed for provisioning, login rendering and valid login.
7. **Reporters:** Implemented reports, images, private history/details and reopening.
   Isolated smoke checks passed for form/submission/history/details and rejection
   of ineligible reopening.
8. **Coordinator:** Implemented dashboard/counts, filters and issue management.
   Isolated checks passed for rendering, priority, resolution, counts and query filters.
9. **UI:** Implemented responsive CSS and progressive JS. Browser executable absent;
   viewport/keyboard checks remain open rather than reported as passed.
10. **Review:** Reviewed SQL/escaping/auth/ownership/uploads/errors; corrected Unicode
    CSRF/form-token comparison failure and CLI context handling. Added explicit preview
    embedding setting; normal framing protection remains enabled.
11. **Automated tests:** Initial suite ran 42 tests, all passed. Expanded during final
    verification to 45 tests, all passed; no skipped tests.
12. **Final verification:** Started Flask on 0.0.0.0:5000 with debug disabled. HTTP
    sign-in and static assets returned 200; protected pages redirected to sign-in.
    Preview-style Host accepted and HTTPS cookie/embedding configuration checked.
    Browser visual checks are still unverified.
13. **Documentation:** Replaced initial README heading with truthful setup/use/testing
    documentation; updated checklist and this verification record. No complete-release
    claim is made while browser verification is outstanding.

## Automated results

Executed using the installed requirements in `.venv`:

```
python -m unittest discover -v
Ran 45 tests
OK
```

The final-verification run took 7.971 seconds. No failures or skips.
The temporary detailed test output is in ignored `instance/test-results.txt`.

Also executed successfully:

- `python -m pip check`: no broken requirements found.
- `python -m compileall -q app.py config.py database routes services tests`.
- `git diff --check`: no whitespace errors.
- `flask --app app init-db`: repeat initialization preserved existing schema.
- Interactive CLI provisioning with synthetic accounts in temporary databases.
- Live HTTP GET checks through Python urllib for `/login`, CSS, JS and redirects
  from `/issues` and `/coordinator/`. These are HTTP checks, not browser screenshots.

Persistent-data verification closes the original application context, recreates an
application against the same on-disk SQLite file, repeats initialization and reads
back the saved issue. Runtime database is not populated with fixture data.

## Outstanding manual browser checks

Use two separately provisioned synthetic reporter accounts and one coordinator.
Perform these at approximately **1440×900**, **768×1024**, **390×844** and **320×640**:

- Sign in/out and inspect role-specific navigation; check wrapping and visible focus.
- Submit an issue, including each location component and optional photo.
- Check useful validation and preserved fields; reselect a photo after a failed form.
- Confirm no page-level horizontal overflow. The issue table may scroll horizontally
  inside its labeled, keyboard-focusable region.
- Tab through navigation, labels, selects, fields, submit actions and table links.
- Confirm tap targets and resolution/reopening actions remain visible on mobile.
- Verify dashboard/list filters using actual newly submitted records.
- Assign final priority, start work, resolve with both fields, inspect as reporter,
  reopen, resume and resolve again.
- Confirm resolution text and user-controlled text wrap without layout overlap.
- Check failed login, missing issue, empty history and empty filtered results.
- Check duplicate-submit button disabling and browser back/forward navigation.
- Confirm readability, contrast, zoom and screen-reader labels in an actual browser.

These checks are **not recorded as passed**. No screenshot, browser automation,
formal accessibility audit, vulnerability scan or production deployment was performed.
