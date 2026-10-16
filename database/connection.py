"""One SQLite connection per application context."""
import sqlite3
from pathlib import Path

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'], timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    schema = Path(__file__).with_name('schema.sql').read_text()
    get_db().executescript(schema)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create missing tables; never discard existing records."""
    init_db()
    click.echo('Database initialized (existing records preserved).')
