import os
import unittest

from toolbox.Parameters import Params

class TestParams(unittest.TestCase):
    def test_file_exists(self):
        filename = "save.json"
        self.assertTrue(os.path.exists(filename))
        
    def test_params_create_from_file(self):
        filename = "save.json"

        f = open(filename, "w")
        f.write("{\n\t\"max_workers\": \"10\"\n}")
        f.close()

        params = Params()
        params.load_params_from_json(filename)
        expected = {"max_workers": '10'}
        self.assertEqual(expected, params.params_dict)

        os.remove(filename)
        
    def test_params_get_max_workers_default(self):
        params = Params()
        params.load_params_from_json("")
        expected = 5
        self.assertEqual(expected, params.get_max_workers())
        expected = {}
        self.assertEqual(expected, params.params_dict)


if __name__ == '__main__':
    unittest.main()
