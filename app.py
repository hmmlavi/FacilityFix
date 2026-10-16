"""FacilityFix application factory and Flask entry point."""
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, render_template, request, session
from werkzeug.exceptions import HTTPException

from config import Config
from database.connection import close_db, get_db, init_db_command


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Set FACILITYFIX_SECRET_KEY before starting FacilityFix.')
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    @app.before_request
    def load_identity_and_check_csrf():
        g.user = None
        user_id = session.get('user_id')
        if user_id is not None:
            g.user = get_db().execute(
                'SELECT id, username, name, role FROM users WHERE id = ?', (user_id,)
            ).fetchone()
            if g.user is None:
                session.clear()
        session.setdefault('csrf_token', secrets.token_hex(32))
        if request.method == 'POST':
            token = request.form.get('csrf_token', '')
            if not secrets.compare_digest(token.encode(), session['csrf_token'].encode()):
                abort(400, description='Your form expired or is invalid. Reload the page and try again.')

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        if not app.config.get('ALLOW_PREVIEW_EMBED'):
            response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; "
            "base-uri 'self'; form-action 'self'"
        )
        if not app.config.get('ALLOW_PREVIEW_EMBED'):
            response.headers['Content-Security-Policy'] += "; frame-ancestors 'none'"
        if request.endpoint != 'static':
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {
            403: 'You do not have permission to perform this action.',
            404: 'This page or issue was not found.',
            413: 'The request is too large. Attach one JPEG or PNG photo no larger than 2 MiB.',
        }
        return render_template('errors/error.html', code=error.code,
                               message=messages.get(error.code, error.description)), error.code

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.exception('Database operation failed')
        if 'db' in g:
            g.db.rollback()
        return render_template('errors/error.html', code=503,
                               message='Data is temporarily unavailable. Please try again later.'), 503

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/error.html', code=500,
                               message='Something went wrong. Please try again later.'), 500

    from routes.auth_routes import bp as auth_bp, create_user_command
    from routes.reporter_routes import bp as reporter_bp
    from routes.coordinator_routes import bp as coordinator_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(reporter_bp)
    app.register_blueprint(coordinator_bp)
    app.cli.add_command(create_user_command)
    return app
