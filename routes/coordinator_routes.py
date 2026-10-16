from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from database import issue_repository as repository
from routes.auth_routes import roles_required
from services.issue_service import accessible_issue, set_priority, transition
from services.validation import CATEGORIES, PRIORITIES, STATUSES, ValidationError, filter_values

bp = Blueprint('coordinator', __name__, url_prefix='/coordinator')


@bp.get('/')
@roles_required('Facility Coordinator')
def dashboard():
    error = None
    try:
        filters = filter_values(request.args)
        issues = repository.list_issues(filters)
    except ValidationError as exc:
        error = str(exc)
        filters, issues = request.args, []
    counts = repository.counts()
    return render_template('coordinator/dashboard.html', issues=issues, counts=counts,
                           total=sum(counts.values()), filters=filters, error=error,
                           statuses=STATUSES, categories=CATEGORIES, priorities=PRIORITIES,
                           buildings=repository.buildings()), 400 if error else 200


@bp.post('/issues/<int:issue_id>/priority')
@roles_required('Facility Coordinator')
def priority(issue_id):
    try:
        set_priority(issue_id, g.user, request.form.get('final_priority', ''))
    except ValidationError as exc:
        return management_error(issue_id, str(exc))
    flash('Final priority updated.', 'success')
    return redirect(url_for('reporter.detail', issue_id=issue_id))


@bp.post('/issues/<int:issue_id>/status')
@roles_required('Facility Coordinator')
def status(issue_id):
    try:
        transition(issue_id, g.user, request.form.get('status', ''),
                   request.form.get('expected_status', ''), request.form)
    except ValidationError as exc:
        return management_error(issue_id, str(exc))
    flash('Issue status updated.', 'success')
    return redirect(url_for('reporter.detail', issue_id=issue_id))


def management_error(issue_id, error):
    return render_template('issues/detail.html', issue=accessible_issue(issue_id, g.user),
                           priorities=PRIORITIES, values=request.form, error=error), 400
