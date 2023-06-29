import unittest

from job_api.DB import DB


class MyTestCase(unittest.TestCase):
    def test_insert(self):
        db = DB()
        result = db.insert(
            'users',
            ['login', 'password', 'email'],
            ('test', 'test', 'test@test.text')
        )
        self.assertEqual(True, result > 0)

    def test_insert_or_update(self):
        db = DB()
        result = db.update_or_insert_one('users', ['login', 'password', 'email'], ('test', 'test2', 'pass2'), '"login"=\'test\'')
        self.assertEqual(True, result > 0)


if __name__ == '__main__':
    unittest.main()
