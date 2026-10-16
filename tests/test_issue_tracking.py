from tests.common import FacilityTestCase


class TrackingTests(FacilityTestCase):
    def test_own_history_details_and_no_other_description(self):
        own = self.seed(description='Unique own issue')
        other = self.seed(2, description='Private other issue')
        self.login()
        response = self.client.get('/issues')
        self.assertIn(f'/issues/{own}'.encode(), response.data)
        self.assertNotIn(f'/issues/{other}'.encode(), response.data)
        self.assertIn(b'Unique own issue', self.client.get(f'/issues/{own}').data)
        self.assertEqual(self.client.get(f'/issues/{other}').status_code, 404)

    def test_missing_issue_and_missing_photo(self):
        issue = self.seed()
        self.login()
        self.assertEqual(self.client.get('/issues/999').status_code, 404)
        self.assertEqual(self.client.get(f'/issues/{issue}/photo').status_code, 404)

    def test_user_text_is_escaped(self):
        issue = self.seed(description='<script>alert(1)</script>')
        self.login()
        response = self.client.get(f'/issues/{issue}')
        self.assertIn(b'&lt;script&gt;', response.data)
        self.assertNotIn(b'<script>alert(1)</script>', response.data)

    def test_resolution_visible_after_reopening(self):
        issue = self.seed()
        self.login(4)
        self.resolve(issue)
        self.post('/logout')
        self.login()
        self.assertIn(b'Test Resolver', self.client.get(f'/issues/{issue}').data)
        self.assertEqual(self.post(f'/issues/{issue}/reopen').status_code, 302)
        response = self.client.get(f'/issues/{issue}')
        self.assertIn(b'Previous resolution', response.data)
        self.assertIn(b'Replaced the test fitting.', response.data)
