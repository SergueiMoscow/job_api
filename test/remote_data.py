import unittest

from job_api.RemoteData import RemoteData


class MyTestCase(unittest.TestCase):
    def test_get_hh_list(self):
        num_saved = RemoteData.get_hh_list('python', area='', period=1)
        self.assertEqual(True, num_saved >= 0)

    def test_get_trud_vsem_list(self):
        num_saved = RemoteData.get_trud_vsem_list('python', area='', period=5)
        self.assertEqual(True, num_saved >= 0)


if __name__ == '__main__':
    unittest.main()
