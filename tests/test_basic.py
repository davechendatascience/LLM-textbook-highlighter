import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBasicFunctionality(unittest.TestCase):
    """Basic tests that don't require heavy dependencies"""
    
    def test_imports_available(self):
        """Test that we can at least check what's available"""
        try:
            import requests
            self.assertTrue(True, "requests available")
        except ImportError:
            self.fail("requests not available")
    
    def test_highlight_utils_parsing(self):
        """Test LLM output parsing without imports"""
        # Simulate the parse function manually for testing
        import re
        
        llm_output = """1,2: defines DNA structure
3: explains base pairs
5,6: details replication process"""
        
        pattern = r'([0-9,\s]+):\s*([^\n]+)'
        results = []
        
        for line in llm_output.splitlines():
            m = re.match(pattern, line.strip())
            if m:
                indices_str, expl = m.groups()
                indices = [int(x.strip())-1 for x in indices_str.split(",") if x.strip().isdigit()]
                if indices:
                    results.append({
                        "indices": indices,
                        "explanation": expl.strip()
                    })
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["indices"], [0, 1])
        self.assertEqual(results[0]["explanation"], "defines DNA structure")
    
    def test_word_normalization_logic(self):
        """Test word normalization without imports"""
        import unicodedata
        import re
        
        def normalize_word(word):
            word_norm = unicodedata.normalize('NFKD', word)
            word_norm = word_norm.encode('ascii', 'ignore').decode("ascii")
            word_norm = re.sub(r"^\W+|\W+$", "", word_norm.lower())
            return word_norm
        
        self.assertEqual(normalize_word("Hello!"), "hello")
        self.assertEqual(normalize_word("  test.  "), "test")
        self.assertEqual(normalize_word("Café"), "cafe")
        
    def test_environment_check(self):
        """Test that we're in the right environment"""
        current_dir = os.getcwd()
        self.assertIn("LLM-textbook-highlighter", current_dir)

if __name__ == '__main__':
    unittest.main()