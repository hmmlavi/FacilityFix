"""Parameterized SQLite issue queries. Business permissions live in the service."""
from database.connection import get_db


def find_issue(issue_id):
    return get_db().execute('''SELECT issues.*, users.name AS reporter_name,
        users.role AS reporter_role FROM issues JOIN users ON users.id = issues.reporter_id
        WHERE issues.id = ?''', (issue_id,)).fetchone()


def insert_issue(reporter_id, values, photo):
    with get_db() as db:
        cursor = db.execute('''INSERT INTO issues
            (reporter_id, category, description, building, floor, room, suggested_priority, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (reporter_id, values['category'], values['description'], values['building'],
             values['floor'], values['room'], values['suggested_priority'], photo))
    return cursor.lastrowid


def own_issues(reporter_id):
    return get_db().execute('SELECT * FROM issues WHERE reporter_id = ? ORDER BY id DESC',
                            (reporter_id,)).fetchall()


def list_issues(filters):
    clauses, params = [], []
    columns = {'status': 'status', 'category': 'category', 'building': 'building',
               'date': 'substr(created_at, 1, 10)', 'priority': 'final_priority'}
    for key, column in columns.items():
        if filters.get(key):
            clauses.append(f'{column} = ?')  # Columns come only from the fixed mapping.
            params.append(filters[key])
    query = 'SELECT * FROM issues'
    if clauses:
        query += ' WHERE ' + ' AND '.join(clauses)
    return get_db().execute(query + ' ORDER BY id DESC', params).fetchall()


def counts():
    return {row['status']: row['total'] for row in get_db().execute(
        'SELECT status, COUNT(*) AS total FROM issues GROUP BY status')}


def buildings():
    return [row[0] for row in get_db().execute('SELECT DISTINCT building FROM issues ORDER BY building')]
