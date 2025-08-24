import unittest
from highlight_utils import build_contextual_highlight_prompt, parse_llm_highlight_groups

class TestHighlightUtils(unittest.TestCase):
    
    def test_build_contextual_highlight_prompt(self):
        """Test prompt building for LLM"""
        chunk = [
            {"sentence": "DNA is the genetic material.", "word_indices": [0, 1, 2, 3, 4, 5]},
            {"sentence": "It contains four bases.", "word_indices": [6, 7, 8, 9]}
        ]
        
        prompt = build_contextual_highlight_prompt(chunk)
        
        # Check prompt contains key elements
        self.assertIn("DNA is the genetic material.", prompt)
        self.assertIn("It contains four bases.", prompt)
        self.assertIn("1: DNA is the genetic material.", prompt)
        self.assertIn("2: It contains four bases.", prompt)
        self.assertIn("indices: explanation", prompt)
    
    def test_parse_llm_highlight_groups_valid(self):
        """Test parsing valid LLM output"""
        llm_output = """1,2: defines DNA structure
3: explains base pairs
5,6: details replication process"""
        
        chunk = [
            {"sentence": "DNA is genetic material.", "word_indices": [0, 1], "page_num": 1},
            {"sentence": "It has four bases.", "word_indices": [2, 3], "page_num": 1}, 
            {"sentence": "Base pairs are important.", "word_indices": [4, 5], "page_num": 1},
            {"sentence": "Extra sentence.", "word_indices": [6, 7], "page_num": 1},
            {"sentence": "Replication occurs.", "word_indices": [8, 9], "page_num": 1},
            {"sentence": "In the nucleus.", "word_indices": [10, 11], "page_num": 1}
        ]
        
        groups = parse_llm_highlight_groups(llm_output, chunk)
        
        self.assertEqual(len(groups), 3)
        
        # Check first group
        self.assertEqual(groups[0]["group_indices"], [0, 1])
        self.assertEqual(groups[0]["explanation"], "defines DNA structure")
        self.assertEqual(groups[0]["word_indices_grouped"], [0, 1, 2, 3])
        
        # Check second group  
        self.assertEqual(groups[1]["group_indices"], [2])
        self.assertEqual(groups[1]["explanation"], "explains base pairs")
        
        # Check third group
        self.assertEqual(groups[2]["group_indices"], [4, 5])
        self.assertEqual(groups[2]["explanation"], "details replication process")
    
    def test_parse_llm_highlight_groups_invalid(self):
        """Test parsing invalid LLM output"""
        llm_output = """This is not a valid format
        Some random text
        Not matching the pattern"""
        
        chunk = [{"sentence": "Test sentence.", "word_indices": [0], "page_num": 1}]
        
        groups = parse_llm_highlight_groups(llm_output, chunk)
        self.assertEqual(len(groups), 0)
    
    def test_parse_llm_highlight_groups_mixed(self):
        """Test parsing mixed valid/invalid LLM output"""
        llm_output = """1: valid highlight
        This line is invalid
        2,3: another valid highlight
        Also invalid line"""
        
        chunk = [
            {"sentence": "First.", "word_indices": [0], "page_num": 1},
            {"sentence": "Second.", "word_indices": [1], "page_num": 1},
            {"sentence": "Third.", "word_indices": [2], "page_num": 1}
        ]
        
        groups = parse_llm_highlight_groups(llm_output, chunk)
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0]["explanation"], "valid highlight")
        self.assertEqual(groups[1]["explanation"], "another valid highlight")

if __name__ == '__main__':
    unittest.main()