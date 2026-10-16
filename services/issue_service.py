"""Central authorization and workflow. Conditional updates reject stale submissions."""
from flask import abort

from database.connection import get_db
from database.issue_repository import find_issue
from services.validation import PRIORITIES, REPORTER_ROLES, ValidationError, required_text

TRANSITIONS = {
    ('Submitted', 'In Progress'): 'Facility Coordinator',
    ('In Progress', 'Resolved'): 'Facility Coordinator',
    ('Resolved', 'Reopened'): 'owner',
    ('Reopened', 'In Progress'): 'Facility Coordinator',
}


def accessible_issue(issue_id, user):
    issue = find_issue(issue_id)
    if issue is None:
        abort(404)
    if user['role'] != 'Facility Coordinator' and issue['reporter_id'] != user['id']:
        abort(404)  # Do not disclose another reporter's issue existence.
    return issue


def transition(issue_id, user, next_status, expected_status, data):
    issue = accessible_issue(issue_id, user)
    authority = TRANSITIONS.get((issue['status'], next_status))
    if authority is None or issue['status'] != expected_status:
        raise ValidationError('This status change is not allowed, or the issue has changed. Reload and try again.')
    if authority == 'owner':
        if user['role'] not in REPORTER_ROLES or issue['reporter_id'] != user['id']:
            abort(403)
    elif user['role'] != authority:
        abort(403)
    note, name = issue['resolution_note'], issue['resolved_by']
    resolved_at = issue['resolved_at']
    if next_status == 'Resolved':
        note = required_text(data, 'resolution_note', 'Resolution note', 2000)
        name = required_text(data, 'resolved_by', 'Resolved-by name', 100)
    with get_db() as db:
        cursor = db.execute('''UPDATE issues SET status = ?, resolution_note = ?, resolved_by = ?,
            resolved_at = CASE WHEN ? = 'Resolved' THEN strftime('%Y-%m-%dT%H:%M:%fZ', 'now') ELSE ? END,
            updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ? AND status = ? AND updated_at = ?''',
            (next_status, note, name, next_status, resolved_at, issue_id, expected_status, issue['updated_at']))
        if cursor.rowcount != 1:
            raise ValidationError('The issue changed while saving. Reload and try again.')


def set_priority(issue_id, user, value):
    if user['role'] != 'Facility Coordinator':
        abort(403)
    accessible_issue(issue_id, user)
    if value not in PRIORITIES:
        raise ValidationError('Final priority must be Low, Medium or High.')
    with get_db() as db:
        db.execute('''UPDATE issues SET final_priority = ?,
            updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') WHERE id = ?''', (value, issue_id))
