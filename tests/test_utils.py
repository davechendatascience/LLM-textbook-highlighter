import unittest
from unittest.mock import patch, MagicMock
import fitz
from utils import normalize_word, get_sentence_bboxes

class TestUtils(unittest.TestCase):
    
    def test_normalize_word(self):
        """Test word normalization function"""
        self.assertEqual(normalize_word("Hello!"), "hello")
        self.assertEqual(normalize_word("  test.  "), "test")
        self.assertEqual(normalize_word("Café"), "cafe")
        self.assertEqual(normalize_word("123abc"), "123abc")
        self.assertEqual(normalize_word(""), "")
    
    def test_get_sentence_bboxes(self):
        """Test sentence bounding box calculation"""
        # Mock word data
        word_list = [
            {"x0": 10, "y0": 20, "x1": 30, "y1": 40},
            {"x0": 35, "y0": 21, "x1": 55, "y1": 39},
            {"x0": 10, "y0": 50, "x1": 30, "y1": 70}  # different line
        ]
        word_indices = [0, 1]  # first two words on same line
        
        bboxes = get_sentence_bboxes(word_list, word_indices)
        
        # Should group words on same line
        self.assertEqual(len(bboxes), 1)
        bbox = bboxes[0]
        self.assertEqual(bbox[0], 9)   # min x0 - margin
        self.assertEqual(bbox[1], 19)  # min y0 - margin  
        self.assertEqual(bbox[2], 56)  # max x1 + margin
        self.assertEqual(bbox[3], 41)  # max y1 + margin
    
    def test_get_sentence_bboxes_empty(self):
        """Test sentence bboxes with empty indices"""
        word_list = [{"x0": 10, "y0": 20, "x1": 30, "y1": 40}]
        bboxes = get_sentence_bboxes(word_list, [])
        self.assertEqual(len(bboxes), 0)
    
    def test_get_sentence_bboxes_invalid_indices(self):
        """Test sentence bboxes with invalid indices"""
        word_list = [{"x0": 10, "y0": 20, "x1": 30, "y1": 40}]
        bboxes = get_sentence_bboxes(word_list, [5, 10])  # out of range
        self.assertEqual(len(bboxes), 0)

if __name__ == '__main__':
    unittest.main()