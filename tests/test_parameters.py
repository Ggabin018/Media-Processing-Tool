import os
import unittest

from Parameters import Params

class TestParams(unittest.TestCase):
    def test_file_exists(self):
        filename = "save.json"
        self.assertTrue(os.path.exists(filename))
        
    def test_params_create_from_file(self):
        params = Params()
        filename = "save.json"
        params.load_params_from_json(filename)
        expected = {"max_workers":'5'}
        self.assertEqual(expected, params.params_dict)
        
    def test_params_get_max_workers_default(self):
        params = Params()
        params.load_params_from_json("")
        expected = "5"
        self.assertEqual(expected, params.get_max_workers())
        expected = {}
        self.assertEqual(expected, params.params_dict)


if __name__ == '__main__':
    unittest.main()
