import secrets

from flask import (Blueprint, abort, current_app, flash, g, redirect, render_template,
                   request, send_from_directory, session, url_for)

from database.issue_repository import insert_issue, own_issues
from routes.auth_routes import login_required, roles_required
from services.issue_service import accessible_issue, transition
from services.uploads import remove_photo, save_photo
from services.validation import CATEGORIES, PRIORITIES, REPORTER_ROLES, ValidationError, report_values

bp = Blueprint('reporter', __name__)


@bp.get('/issues')
@roles_required(*REPORTER_ROLES)
def history():
    return render_template('reporter/history.html', issues=own_issues(g.user['id']))


@bp.route('/issues/new', methods=['GET', 'POST'])
@roles_required(*REPORTER_ROLES)
def new_issue():
    error = None
    session.setdefault('report_token', secrets.token_hex(24))
    if request.method == 'POST':
        photo = None
        try:
            if not secrets.compare_digest(request.form.get('report_token', '').encode(), session['report_token'].encode()):
                raise ValidationError('This report form has already been used or has expired. Please review and submit again.')
            values = report_values(request.form)
            photo = save_photo(request.files.get('photo'))
            try:
                issue_id = insert_issue(g.user['id'], values, photo)
            except Exception:
                remove_photo(photo)
                raise
            session['report_token'] = secrets.token_hex(24)
            flash('Your issue was submitted successfully.', 'success')
            return redirect(url_for('reporter.detail', issue_id=issue_id))
        except ValidationError as exc:
            error = str(exc)
        except OSError:
            current_app.logger.exception('Photo storage failed')
            error = 'The photo could not be saved. Please try again or submit without a photo.'
    return render_template('reporter/new.html', categories=CATEGORIES, priorities=PRIORITIES,
                           values=request.form, error=error), 400 if error else 200


@bp.get('/issues/<int:issue_id>')
@login_required
def detail(issue_id):
    issue = accessible_issue(issue_id, g.user)
    return render_template('issues/detail.html', issue=issue, priorities=PRIORITIES, values={})


@bp.get('/issues/<int:issue_id>/photo')
@login_required
def photo(issue_id):
    issue = accessible_issue(issue_id, g.user)
    if not issue['photo']:
        abort(404)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], issue['photo'])


@bp.post('/issues/<int:issue_id>/reopen')
@roles_required(*REPORTER_ROLES)
def reopen(issue_id):
    try:
        transition(issue_id, g.user, 'Reopened', 'Resolved', {})
    except ValidationError as exc:
        return render_template('issues/detail.html', issue=accessible_issue(issue_id, g.user),
                               priorities=PRIORITIES, values={}, error=str(exc)), 400
    flash('Your issue has been reopened for the Facility Coordinator to review.', 'success')
    return redirect(url_for('reporter.detail', issue_id=issue_id))
