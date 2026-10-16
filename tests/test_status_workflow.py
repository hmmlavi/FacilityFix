from services.validation import STATUSES
from tests.common import FacilityTestCase


class WorkflowTests(FacilityTestCase):
    def test_full_workflow_and_reresolution(self):
        issue = self.seed()
        self.login(4)
        self.resolve(issue)
        self.post('/logout'); self.login()
        self.assertEqual(self.post(f'/issues/{issue}/reopen').status_code, 302)
        self.assertEqual(self.issue(issue)['status'], 'Reopened')
        self.assertEqual(self.post(f'/issues/{issue}/reopen').status_code, 400)
        self.post('/logout'); self.login(4)
        self.assertEqual(self.move(issue, 'Reopened', 'In Progress').status_code, 302)
        self.assertEqual(self.move(issue, 'In Progress', 'Resolved', resolution_note='Second repair',
                                   resolved_by='Another Test Person').status_code, 302)
        saved = self.issue(issue)
        self.assertEqual(saved['resolution_note'], 'Second repair')
        self.assertIsNotNone(saved['resolved_at'])

    def test_resolution_requires_both_fields(self):
        issue = self.seed()
        self.login(4)
        self.move(issue, 'Submitted', 'In Progress')
        for values in ({}, {'resolution_note':'Fixed'}, {'resolved_by':'Test'},
                       {'resolution_note':'   ', 'resolved_by':'Test'},
                       {'resolution_note':'x'*2001, 'resolved_by':'Test'}):
            self.assertEqual(self.move(issue, 'In Progress', 'Resolved', **values).status_code, 400)
            self.assertEqual(self.issue(issue)['status'], 'In Progress')

    def test_unsupported_transitions_do_not_mutate(self):
        issue = self.seed()
        self.login(4)
        original = self.issue(issue)
        for target in ('Submitted', 'Resolved', 'Reopened', 'Deleted', ''):
            self.assertEqual(self.move(issue, 'Submitted', target).status_code, 400)
            self.assertEqual(self.issue(issue), original)

    def test_stale_status_form_rejected(self):
        issue = self.seed()
        self.login(4)
        self.move(issue, 'Submitted', 'In Progress')
        self.assertEqual(self.move(issue, 'Submitted', 'Resolved', resolution_note='Test',
                                   resolved_by='Test').status_code, 400)

    def test_reopen_requires_current_resolution(self):
        issue = self.seed()
        self.login()
        self.assertEqual(self.post(f'/issues/{issue}/reopen').status_code, 400)

    def test_every_coordinator_status_pair(self):
        from database.connection import get_db
        allowed = {('Submitted', 'In Progress'), ('In Progress', 'Resolved'), ('Reopened', 'In Progress')}
        self.login(4)
        for before in STATUSES:
            for after in STATUSES:
                with self.subTest(before=before, after=after):
                    issue = self.seed()
                    with self.app.app_context():
                        with get_db() as db:
                            db.execute("""UPDATE issues SET status=?, resolution_note='Earlier repair',
                                resolved_by='Test Resolver', resolved_at='2026-10-01T00:00:00Z' WHERE id=?""",
                                (before, issue))
                    original = self.issue(issue)
                    response = self.move(issue, before, after, resolution_note='Current repair', resolved_by='Test Resolver')
                    if (before, after) in allowed:
                        self.assertEqual(response.status_code, 302)
                        self.assertEqual(self.issue(issue)['status'], after)
                    else:
                        self.assertIn(response.status_code, (400, 403))
                        self.assertEqual(self.issue(issue), original)
