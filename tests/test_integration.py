import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
import sys
from io import BytesIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestIntegration(unittest.TestCase):
    """Integration tests using mocked PDFs and sample data"""
    
    @patch('utils.fitz.open')
    def test_extract_sentences_and_chunks_mock(self, mock_fitz_open):
        """Test sentence extraction with mocked PDF"""
        # Mock PyMuPDF document
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__len__ = MagicMock(return_value=1)  # 1 page
        mock_doc.__getitem__ = MagicMock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        # Mock word data from PDF
        mock_words = [
            (10, 20, 30, 40, "DNA", 0, 0, 0),    # x0, y0, x1, y1, word, block, line, word_no
            (35, 20, 50, 40, "is", 0, 0, 1),
            (55, 20, 80, 40, "important.", 0, 0, 2),
            (10, 50, 40, 70, "Proteins", 0, 1, 0),  # new line
            (45, 50, 70, 70, "are", 0, 1, 1),
            (75, 50, 110, 70, "essential.", 0, 1, 2)
        ]
        mock_page.get_text.return_value = mock_words
        
        from utils import extract_sentences_and_chunks
        
        sentences, chunks, page_word_map = extract_sentences_and_chunks("fake.pdf", chunk_size=2)
        
        # Verify results
        self.assertGreater(len(sentences), 0)
        self.assertGreater(len(chunks), 0)
        self.assertIn(0, page_word_map)  # page 0 should exist
        
        # Verify chunks are properly sized
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 2)  # chunk_size=2
    
    @patch('highlight_utils.parse_llm_highlight_groups')
    @patch('highlight_utils.build_contextual_highlight_prompt') 
    def test_workflow_components_integration(self, mock_build_prompt, mock_parse_groups):
        """Test that workflow components work together properly"""
        # Setup sample data
        sample_chunk = [
            {"sentence": "DNA is genetic material.", "word_indices": [0, 1, 2, 3], "page_num": 0}
        ]
        
        # Mock prompt building
        mock_build_prompt.return_value = "Test prompt for DNA content"
        
        # Mock LLM response parsing  
        mock_parse_groups.return_value = [
            {
                "group_indices": [0],
                "page_num": 0,
                "chunk": sample_chunk,
                "word_indices_grouped": [0, 1, 2, 3],
                "explanation": "defines DNA"
            }
        ]
        
        # Test the integration
        from highlight_utils import build_contextual_highlight_prompt, parse_llm_highlight_groups
        
        # Build prompt
        prompt = build_contextual_highlight_prompt(sample_chunk)
        
        # Simulate LLM response
        llm_response = "1: defines DNA"
        
        # Parse response
        groups = parse_llm_highlight_groups(llm_response, sample_chunk)
        
        # Verify integration
        mock_build_prompt.assert_called_once_with(sample_chunk)
        mock_parse_groups.assert_called_once_with(llm_response, sample_chunk)
        
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["explanation"], "defines DNA")

if __name__ == '__main__':
    unittest.main()