import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from werkzeug.security import generate_password_hash

from app import create_app
from database.connection import get_db, init_db
from database.issue_repository import find_issue, insert_issue
from services.validation import report_values

PASSWORD = 'test-password-123'


class FacilityTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.password_hash = generate_password_hash(PASSWORD)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = {'TESTING': True, 'SECRET_KEY': 'isolated-tests-only',
                       'DATABASE': str(Path(self.temp.name) / 'test.sqlite3'),
                       'UPLOAD_FOLDER': str(Path(self.temp.name) / 'uploads')}
        self.app = create_app(self.config)
        with self.app.app_context():
            init_db()
            with get_db() as db:
                for index, role in enumerate(('Student', 'Faculty', 'Staff', 'Facility Coordinator'), 1):
                    db.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)',
                               (index, f'user{index}', f'Test Person {index}', self.password_hash, role))
        self.client = self.app.test_client()

    def login(self, user_id=1):
        self.client.get('/login')
        response = self.post('/login', {'username': f'user{user_id}', 'password': PASSWORD})
        self.assertEqual(response.status_code, 302)

    def post(self, url, data=None, **kwargs):
        with self.client.session_transaction() as session:
            token = session.get('csrf_token', '')
        return self.client.post(url, data={'csrf_token': token, **(data or {})}, **kwargs)

    def values(self, **changes):
        return dict(category='Electrical', description='A test light is broken.', building='Test Block A',
                    floor='Ground', room='Test Room 1', suggested_priority='Medium', **changes)

    def seed(self, reporter_id=1, **changes):
        values = self.values()
        values.update(changes)
        with self.app.app_context():
            return insert_issue(reporter_id, report_values(values), None)

    def issue(self, issue_id):
        with self.app.app_context():
            return dict(find_issue(issue_id))

    def submit(self, changes=None, photo=None):
        self.client.get('/issues/new')
        with self.client.session_transaction() as session:
            token = session['report_token']
        values = self.values()
        values.update(changes or {})
        values['report_token'] = token
        if photo:
            values['photo'] = photo
        return self.post('/issues/new', values)

    def move(self, issue_id, before, after, **values):
        return self.post(f'/coordinator/issues/{issue_id}/status',
                         dict(expected_status=before, status=after, **values))

    def resolve(self, issue_id):
        self.assertEqual(self.move(issue_id, 'Submitted', 'In Progress').status_code, 302)
        self.assertEqual(self.move(issue_id, 'In Progress', 'Resolved',
                                  resolution_note='Replaced the test fitting.', resolved_by='Test Resolver').status_code, 302)

    @staticmethod
    def image(fmt='PNG'):
        buffer = io.BytesIO()
        Image.new('RGB', (8, 8), 'white').save(buffer, format=fmt)
        buffer.seek(0)
        return buffer
