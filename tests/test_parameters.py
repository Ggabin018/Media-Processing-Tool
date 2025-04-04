import os
import unittest

from Parameters import Params

class TestParams(unittest.TestCase):
    def test_file_exists(self):
        filename = "save.json"
        self.assertTrue(os.path.exists(filename))
        
    def test_params_create_from_file(self):
        filename = "save.json"
        params = Params(filename)
        expected = {"max_workers":'5'}
        self.assertEqual(expected, params.params_dict)


if __name__ == '__main__':
    unittest.main()
