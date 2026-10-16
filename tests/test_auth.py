from werkzeug.security import check_password_hash
from database.connection import get_db
from tests.common import FacilityTestCase, PASSWORD


class AuthTests(FacilityTestCase):
    def test_protected_pages_redirect_to_login(self):
        for path in ('/', '/issues', '/issues/new', '/issues/1', '/coordinator/', '/issues/1/photo'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 302)

    def test_login_logout_and_role_landing(self):
        for user_id, destination in ((1, '/issues'), (2, '/issues'), (3, '/issues'), (4, '/coordinator/')):
            self.login(user_id)
            self.assertEqual(self.client.get('/').location, destination)
            self.assertEqual(self.post('/logout').status_code, 302)
            self.assertEqual(self.client.get('/issues').status_code, 302)

    def test_invalid_login_is_generic(self):
        self.client.get('/login')
        for username, password in [('user1', 'wrong-password-123'), ('missing', PASSWORD)]:
            response = self.post('/login', dict(username=username, password=password))
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Username or password is incorrect', response.data)

    def test_csrf_missing_wrong_and_unicode(self):
        self.client.get('/login')
        for token in ('', 'wrong', 'é'):
            self.assertEqual(self.client.post('/login', data={'csrf_token': token}).status_code, 400)

    def test_login_rotates_session(self):
        self.client.get('/login')
        with self.client.session_transaction() as session:
            old_token = session['csrf_token']
            session['untrusted'] = 'value'
        self.login()
        with self.client.session_transaction() as session:
            self.assertNotEqual(old_token, session['csrf_token'])
            self.assertNotIn('untrusted', session)

    def test_create_user_cli_hashes_password_and_rejects_duplicates(self):
        runner = self.app.test_cli_runner()
        args = ['create-user', '--username', 'new.user', '--name', 'Test New', '--role', 'Staff']
        response = runner.invoke(args=args, input=f'{PASSWORD}\n{PASSWORD}\n')
        self.assertEqual(response.exit_code, 0, response.output)
        with self.app.app_context():
            row = get_db().execute("SELECT * FROM users WHERE username='new.user'").fetchone()
            self.assertNotEqual(row['password_hash'], PASSWORD)
            self.assertTrue(check_password_hash(row['password_hash'], PASSWORD))
        self.assertNotEqual(runner.invoke(args=args, input=f'{PASSWORD}\n{PASSWORD}\n').exit_code, 0)

    def test_cli_rejects_short_password(self):
        result = self.app.test_cli_runner().invoke(args=['create-user', '--username', 'new.user',
            '--name', 'Test', '--role', 'Student'], input='short\nshort\n')
        self.assertNotEqual(result.exit_code, 0)

    def test_cookie_and_response_headers(self):
        response = self.client.get('/login')
        self.assertIn('HttpOnly', response.headers['Set-Cookie'])
        self.assertIn('SameSite=Lax', response.headers['Set-Cookie'])
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
