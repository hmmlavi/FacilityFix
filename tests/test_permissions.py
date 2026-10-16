from tests.common import FacilityTestCase


class PermissionTests(FacilityTestCase):
    def test_reporters_cannot_manage(self):
        issue = self.seed()
        original = self.issue(issue)
        for reporter in (1, 2, 3):
            self.login(reporter)
            self.assertEqual(self.client.get('/coordinator/').status_code, 403)
            self.assertEqual(self.post(f'/coordinator/issues/{issue}/priority', {'final_priority':'High'}).status_code, 403)
            self.assertEqual(self.move(issue, 'Submitted', 'In Progress').status_code, 403)
            self.post('/logout')
        self.assertEqual(self.issue(issue), original)

    def test_cross_user_photo_and_reopen_denied(self):
        self.login()
        self.assertEqual(self.submit(photo=(self.image(), 'test.png')).status_code, 302)
        self.post('/logout'); self.login(4); self.resolve(1)
        self.post('/logout'); self.login(2)
        original = self.issue(1)
        self.assertEqual(self.client.get('/issues/1/photo').status_code, 404)
        self.assertEqual(self.post('/issues/1/reopen').status_code, 404)
        self.assertEqual(self.issue(1), original)

    def test_coordinator_cannot_report_or_reopen(self):
        issue = self.seed()
        self.login(4)
        self.assertEqual(self.client.get('/issues/new').status_code, 403)
        self.assertEqual(self.post('/issues/new', self.values()).status_code, 403)
        self.resolve(issue)
        self.assertEqual(self.post(f'/issues/{issue}/reopen').status_code, 403)
        self.assertEqual(self.move(issue, 'Resolved', 'Reopened').status_code, 403)
        self.assertEqual(self.issue(issue)['status'], 'Resolved')

    def test_no_edit_or_delete_endpoint(self):
        issue = self.seed()
        self.login()
        self.assertEqual(self.post(f'/issues/{issue}', {'description':'Changed'}).status_code, 405)
        self.assertEqual(self.client.delete(f'/issues/{issue}').status_code, 405)
        self.assertEqual(self.issue(issue)['description'], 'A test light is broken.')

    def test_photo_path_traversal_not_routed(self):
        self.login()
        self.assertEqual(self.client.get('/uploads/../../config.py').status_code, 404)
