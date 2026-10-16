import sqlite3
from pathlib import Path
from unittest.mock import patch
from app import create_app
from database.connection import get_db, init_db
from database.issue_repository import find_issue
from tests.common import FacilityTestCase


class PersistenceTests(FacilityTestCase):
    def test_restart_and_reinitialize_preserve_records(self):
        issue = self.seed()
        restarted = create_app(self.config)
        with restarted.app_context():
            init_db()
            self.assertEqual(find_issue(issue)['description'], 'A test light is broken.')
        result = restarted.test_cli_runner().invoke(args=['init-db'])
        self.assertEqual(result.exit_code, 0, result.output)

    def test_database_failure_safe_and_uploaded_file_cleaned(self):
        self.login()
        with patch('routes.reporter_routes.insert_issue', side_effect=sqlite3.OperationalError('sensitive internals')):
            with self.assertLogs('app', level='ERROR'):
                response = self.submit(photo=(self.image(), 'test.png'))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b'sensitive internals', response.data)
        self.assertEqual(list(Path(self.config['UPLOAD_FOLDER']).iterdir()), [])
        with self.app.app_context():
            self.assertEqual(get_db().execute('SELECT count(*) FROM issues').fetchone()[0], 0)

    def test_photo_storage_failure_is_honest(self):
        self.login()
        with patch('routes.reporter_routes.save_photo', side_effect=OSError('private path')):
            with self.assertLogs('app', level='ERROR'):
                response = self.submit(photo=(self.image(), 'test.png'))
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'could not be saved', response.data)
        self.assertNotIn(b'private path', response.data)

    def test_database_constraints(self):
        with self.app.app_context():
            with self.assertRaises(sqlite3.IntegrityError):
                with get_db() as db:
                    db.execute("INSERT INTO users VALUES(99,'invalid','Test','hash','Administrator')")

    def test_secret_is_required(self):
        with self.assertRaises(RuntimeError):
            create_app({**self.config, 'SECRET_KEY': None})
