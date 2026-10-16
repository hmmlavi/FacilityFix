from database.connection import get_db
from database.issue_repository import counts, list_issues
from tests.common import FacilityTestCase


class CoordinatorTests(FacilityTestCase):
    def setUp(self):
        super().setUp()
        self.first = self.seed()
        self.second = self.seed(2, category='Plumbing', building='Test Block B')
        self.login(4)

    def test_dashboard_and_all_details(self):
        self.assertEqual(self.client.get('/coordinator/').status_code, 200)
        self.assertEqual(self.client.get(f'/issues/{self.second}').status_code, 200)
        with self.app.app_context():
            self.assertEqual(counts(), {'Submitted':2})

    def test_counts_follow_workflow(self):
        self.resolve(self.first)
        with self.app.app_context():
            self.assertEqual(counts(), {'Resolved':1, 'Submitted':1})
        response = self.client.get('/coordinator/')
        self.assertIn(b'<strong>2</strong>', response.data)

    def test_priority_validation_and_update(self):
        url = f'/coordinator/issues/{self.first}/priority'
        self.assertEqual(self.post(url, {'final_priority':'Urgent'}).status_code, 400)
        self.assertIsNone(self.issue(self.first)['final_priority'])
        self.assertEqual(self.post(url, {'final_priority':'High'}).status_code, 302)
        self.assertEqual(self.issue(self.first)['final_priority'], 'High')

    def test_each_filter_and_combined(self):
        self.post(f'/coordinator/issues/{self.first}/priority', {'final_priority':'High'})
        self.move(self.first, 'Submitted', 'In Progress')
        with self.app.app_context():
            with get_db() as db:
                db.execute("UPDATE issues SET created_at='2026-10-01T12:00:00.000Z' WHERE id=?", (self.first,))
                db.execute("UPDATE issues SET created_at='2026-10-02T12:00:00.000Z' WHERE id=?", (self.second,))
            filters = {'status':'In Progress', 'category':'Electrical', 'building':'Test Block A',
                       'date':'2026-10-01', 'priority':'High'}
            for field, value in filters.items():
                self.assertEqual([r['id'] for r in list_issues({field:value})], [self.first])
            self.assertEqual([r['id'] for r in list_issues(filters)], [self.first])
        response = self.client.get('/coordinator/', query_string=filters)
        self.assertIn(f'/issues/{self.first}'.encode(), response.data)
        self.assertNotIn(f'/issues/{self.second}'.encode(), response.data)

    def test_invalid_filters_and_empty_state(self):
        for query in ({'status':'Deleted'}, {'category':'Unknown'}, {'date':'2026-02-30'}, {'priority':'Urgent'}):
            self.assertEqual(self.client.get('/coordinator/', query_string=query).status_code, 400)
        response = self.client.get('/coordinator/', query_string={'building':"' OR 1=1 --"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No issues to display', response.data)
