"""Local account provisioning and session-based password authentication."""
import functools
import re
import secrets
import sqlite3

import click
from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from flask.cli import with_appcontext
from werkzeug.security import check_password_hash, generate_password_hash

from database.connection import get_db
from services.validation import ROLES

bp = Blueprint('auth', __name__)
DUMMY_HASH = generate_password_hash('unused-timing-comparison-value')


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


def roles_required(*roles):
    def decorate(view):
        @login_required
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if g.user['role'] not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorate


@bp.route('/')
def home():
    if g.user is None:
        return redirect(url_for('auth.login'))
    endpoint = 'coordinator.dashboard' if g.user['role'] == 'Facility Coordinator' else 'reporter.history'
    return redirect(url_for(endpoint))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None:
        return redirect(url_for('auth.home'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = None
        if 3 <= len(username) <= 50 and 12 <= len(password) <= 128:
            user = get_db().execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        valid = check_password_hash(user['password_hash'] if user else DUMMY_HASH, password[:128])
        if user is not None and valid:
            session.clear()
            session['user_id'] = user['id']
            session['csrf_token'] = secrets.token_hex(32)
            session.permanent = True
            return redirect(url_for('auth.home'))
        error = 'Username or password is incorrect.'
    return render_template('auth/login.html', error=error), 400 if error else 200


@bp.post('/logout')
@login_required
def logout():
    session.clear()
    flash('You have signed out.', 'success')
    return redirect(url_for('auth.login'))


@click.command('create-user')
@click.option('--username', prompt=True)
@click.option('--name', prompt='Display name')
@click.option('--role', type=click.Choice(ROLES), prompt=True)
@click.password_option(confirmation_prompt=True)
@with_appcontext
def create_user_command(username, name, role, password):
    """Create a local application account; the password is prompted, not echoed."""
    username, name = username.strip(), name.strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,50}', username):
        raise click.ClickException('Username must contain 3–50 letters, digits, dots, underscores or hyphens.')
    if not 1 <= len(name) <= 100:
        raise click.ClickException('Display name must contain 1–100 characters.')
    if not 12 <= len(password) <= 128:
        raise click.ClickException('Password must contain 12–128 characters.')
    try:
        with get_db() as db:
            db.execute('INSERT INTO users (username, name, role, password_hash) VALUES (?, ?, ?, ?)',
                       (username, name, role, generate_password_hash(password)))
    except sqlite3.IntegrityError:
        raise click.ClickException('That username already exists or the account data is invalid.') from None
    except sqlite3.Error:
        raise click.ClickException('Could not save the account. Check database initialization and permissions.') from None
    click.echo(f'Created {role} account: {username}')
