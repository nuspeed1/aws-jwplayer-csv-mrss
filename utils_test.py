import unittest
from pprint import pprint
from utils import build_load_order

class Test_Build_Load_Order(unittest.TestCase):

    def test_build_load_order_invalid(self):
        """
        If invalid is found, return sorted result
        """ 
        struct = {
            "media": {"dependencies": ["thumbnail_portrait", "thumbnail_landscape"]},
            "thumbnail":{"dependencies": ["media"]},
            "thumbnail_portrait":{},
            "thumbnail_landscape":{"dependencies": ["thumbnail_portrait", "INVALID_KEY"]},
            "series_portrait":{},
            "series_landscape":{},
            "series":{"dependencies": ["series_portrait", "series_landscape"]},
            "subtitle":{"dependencies": ["media", "series_landscape"]}
        }
        sorted = build_load_order(struct)

        self.assertEqual(sorted[0], {'thumbnail_portrait': {'perm': True, 'temp': False}})
        self.assertEqual(sorted[1], {'thumbnail_landscape': {'dependencies': ['thumbnail_portrait','INVALID_KEY'],'perm': True,'temp': False}})
        self.assertEqual(sorted[2], {'media': {'dependencies': ['thumbnail_portrait', 'thumbnail_landscape'],'perm': True,'temp': False}})
        self.assertEqual(sorted[3], {'thumbnail': {'dependencies': ['media'], 'perm': True, 'temp': False}})
        self.assertEqual(sorted[4], {'series_portrait': {'perm': True, 'temp': False}})
        self.assertEqual(sorted[5], {'series_landscape': {'perm': True, 'temp': False}})
        self.assertEqual(sorted[6], {'series': {'dependencies': ['series_portrait', 'series_landscape'],'perm': True,'temp': False}})
        self.assertEqual(sorted[7], {'subtitle': {'dependencies': ['media', 'series_landscape'],'perm': True,'temp': False}})

    def test_build_load_order(self):
        """
        If valid result
        """ 
        struct = {
            "media": {"dependencies": ["thumbnail_portrait", "thumbnail_landscape"]},
            "thumbnail":{"dependencies": ["media"]},
            "thumbnail_portrait":{},
            "thumbnail_landscape":{"dependencies": ["thumbnail_portrait", "series_portrait"]},
            "series_portrait":{},
            "series_landscape":{},
            "series":{"dependencies": ["series_portrait", "series_landscape"]},
            "subtitle":{"dependencies": ["media", "series_landscape"]}
        }
        sorted = build_load_order(struct)

        self.assertEqual(sorted[0], {'thumbnail_portrait': {'perm': True, 'temp': False}})
        self.assertEqual(sorted[1], {'series_portrait': {'perm': True, 'temp': False}})
        self.assertEqual(sorted[2], {'thumbnail_landscape': {'dependencies': ['thumbnail_portrait','series_portrait'],'perm': True,'temp': False}})
        self.assertEqual(sorted[3], {'media': {'dependencies': ['thumbnail_portrait', 'thumbnail_landscape'],'perm': True,'temp': False}})
        self.assertEqual(sorted[4], {'thumbnail': {'dependencies': ['media'], 'perm': True, 'temp': False}})
        self.assertEqual(sorted[5], {'series_landscape': {'perm': True, 'temp': False}})
        self.assertEqual(sorted[6], {'series': {'dependencies': ['series_portrait', 'series_landscape'],'perm': True,'temp': False}})
        self.assertEqual(sorted[7], {'subtitle': {'dependencies': ['media', 'series_landscape'],'perm': True,'temp': False}})
        

if __name__ == '__main__':
    unittest.main()