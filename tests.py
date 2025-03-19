import unittest
from rag import CartageneRelatedFieldAnnotator


class CartageneRelatedFieldsTestCase(unittest.TestCase):

    def testGetPrefix(self):
        annotator = CartageneRelatedFieldAnnotator([])
        assert annotator.get_prefix("a_bcd_def_geh") == "a_bcd_def"
        assert annotator.get_prefix("abcdefg") == "abcdefg"

    def testGetRelatedFields(self):
        df = [
            {"varname": "a_bcd_def_geh"},
            {"varname": "a_bcd_def_xyz"},
            {"varname": "a_bcd_def"},
            {"varname": "a_bcd"},
            {"varname": "a"},
            {"varname": "abc"},
            {"varname": "abc_def"},
            {"varname": "xyz_abc"},
            {"varname": "test_varname"},
        ]
        annotator = CartageneRelatedFieldAnnotator(df)

        assert annotator.get_related("a_bcd_def_abc") == {"a_bcd_def_geh", "a_bcd_def_xyz", "a_bcd_def"}
        assert annotator.get_related("a_bcd_def") == {"a_bcd_def_geh", "a_bcd_def_xyz", "a_bcd"}

        assert annotator.get_related("test_varname") == set() 
        assert annotator.get_related("abc") == {"abc_def"}
    

if __name__ == '__main__':
    unittest.main()
