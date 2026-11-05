import unittest
from unittest.mock import patch, MagicMock
from app import create_app

class StudentAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Patch init_db to avoid connection attempts during test setup
        with patch('app.database.init_db'):
            cls.app = create_app()
            cls.client = cls.app.test_client()

    def setUp(self):
        self.client = self.__class__.client

    def test_pages_render(self):
        # Test dashboard page route
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Admin Dashboard', resp.data)

        # Test students directory route
        resp = self.client.get('/students')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Student Directory', resp.data)

        # Test add student form route
        resp = self.client.get('/students/add')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'New Student Information', resp.data)

    def test_student_validation(self):
        # Test validation failure for empty payload
        resp = self.client.post('/api/students', json={})
        self.assertEqual(resp.status_code, 422)
        data = resp.get_json()
        self.assertFalse(data['success'])
        self.assertIn('name', data['errors'])
        self.assertIn('email', data['errors'])

    @patch('app.routes.get_connection')
    def test_get_students_mock(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'name': 'John Doe',
                'email': 'john.doe@university.edu',
                'phone': '+1-555-0100',
                'department': 'Computer Science',
                'gender': 'Male',
                'date_of_birth': '2001-01-01',
                'created_at': '2026-01-01 12:00'
            }
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        resp = self.client.get('/api/students')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'John Doe')

    @patch('app.routes.get_connection')
    def test_create_student_mock(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Email uniqueness check returns None (no duplicate)
        mock_cursor.fetchone.return_value = None
        mock_cursor.lastrowid = 10
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        payload = {
            'name': 'Jane Doe',
            'email': 'jane.doe@university.edu',
            'phone': '+1-555-0199',
            'department': 'Electrical Engineering',
            'gender': 'Female',
            'date_of_birth': '2002-05-15'
        }
        resp = self.client.post('/api/students', json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], 10)

    @patch('app.routes.get_connection')
    def test_update_student_mock(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Student exists:
        mock_cursor.fetchone.side_effect = [{'id': 10}, None]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        payload = {
            'name': 'Jane Updated',
            'email': 'jane.doe@university.edu',
            'phone': '+1-555-0199',
            'department': 'Computer Science',
            'gender': 'Female',
            'date_of_birth': '2002-05-15'
        }
        resp = self.client.put('/api/students/10', json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Jane Updated')

    @patch('app.routes.get_connection')
    def test_delete_student_mock(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'id': 10}
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        resp = self.client.delete('/api/students/10')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()

