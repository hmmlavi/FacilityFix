import io
from pathlib import Path
from database.connection import get_db
from tests.common import FacilityTestCase


class ReportingTests(FacilityTestCase):
    def setUp(self):
        super().setUp()
        self.login()

    def test_valid_report_and_no_automatic_final_priority(self):
        response = self.submit({'reporter_id': '2', 'final_priority': 'High', 'status': 'Resolved'})
        self.assertEqual(response.status_code, 302)
        issue = self.issue(1)
        self.assertEqual(issue['reporter_id'], 1)
        self.assertEqual(issue['status'], 'Submitted')
        self.assertEqual(issue['suggested_priority'], 'Medium')
        self.assertIsNone(issue['final_priority'])

    def test_required_fields_and_boundaries(self):
        for field in ('description', 'building', 'floor', 'room', 'category'):
            for value in ('', '   '):
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.submit({field: value}).status_code, 400)
        for field, limit in [('description', 2000), ('building', 100), ('floor', 100), ('room', 100)]:
            self.assertEqual(self.submit({field: 'x' * (limit + 1)}).status_code, 400)
        self.assertEqual(self.submit({'description': 'x' * 2000}).status_code, 302)

    def test_invalid_category_and_priority(self):
        self.assertEqual(self.submit({'category': 'Security'}).status_code, 400)
        self.assertEqual(self.submit({'suggested_priority': 'Urgent'}).status_code, 400)
        self.assertEqual(self.submit({'suggested_priority': ''}).status_code, 302)

    def test_fields_preserved_after_validation_error(self):
        response = self.submit({'room': ''})
        self.assertIn(b'A test light is broken.', response.data)
        self.assertIn(b'Test Block A', response.data)

    def test_jpeg_png_and_generated_filenames(self):
        for fmt in ('JPEG', 'PNG'):
            response = self.submit(photo=(self.image(fmt), '../../dangerous.py'))
            self.assertEqual(response.status_code, 302)
            issue_id = int(response.location.rsplit('/', 1)[1])
            photo = self.issue(issue_id)['photo']
            self.assertNotIn('dangerous', photo)
            self.assertNotIn('/', photo)
            self.assertTrue((Path(self.config['UPLOAD_FOLDER']) / photo).is_file())
            self.assertEqual(self.client.get(f'/issues/{issue_id}/photo').status_code, 200)

    def test_invalid_and_oversized_uploads(self):
        for content, filename in [(b'<script>alert(1)</script>', 'photo.png'),
                                  (b'x' * (2 * 1024 * 1024 + 1), 'photo.jpg')]:
            self.assertEqual(self.submit(photo=(io.BytesIO(content), filename)).status_code, 400)
        self.assertEqual(list(Path(self.config['UPLOAD_FOLDER']).iterdir()), [])

    def test_gif_rejected(self):
        self.assertEqual(self.submit(photo=(self.image('GIF'), 'test.gif')).status_code, 400)

    def test_duplicate_form_token_rejected(self):
        self.client.get('/issues/new')
        with self.client.session_transaction() as session:
            token = session['report_token']
        data = {**self.values(), 'report_token': token}
        self.assertEqual(self.post('/issues/new', data).status_code, 302)
        self.assertEqual(self.post('/issues/new', data).status_code, 400)
        with self.app.app_context():
            self.assertEqual(get_db().execute('SELECT count(*) FROM issues').fetchone()[0], 1)

    def test_unicode_form_token_rejected_safely(self):
        self.client.get('/issues/new')
        self.assertEqual(self.post('/issues/new', {**self.values(), 'report_token': 'é'}).status_code, 400)

    def test_total_request_limit(self):
        self.assertEqual(self.submit(photo=(io.BytesIO(b'x' * (4 * 1024 * 1024)), 'large.jpg')).status_code, 413)

    def test_corrupt_image_with_valid_header_rejected(self):
        data = self.image().getvalue()[:25]
        self.assertEqual(self.submit(photo=(io.BytesIO(data), 'partial.png')).status_code, 400)

    def test_animated_png_rejected(self):
        from PIL import Image
        photo = io.BytesIO()
        Image.new('RGB', (8, 8), 'red').save(photo, format='PNG', save_all=True,
            append_images=[Image.new('RGB', (8, 8), 'blue')], duration=100, loop=0)
        photo.seek(0)
        self.assertEqual(self.submit(photo=(photo, 'animated.png')).status_code, 400)
