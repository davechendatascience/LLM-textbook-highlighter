import unittest
from unittest.mock import patch, MagicMock
from llm import send_prompt_to_gemini, send_prompt_to_perplexity

class TestLLM(unittest.TestCase):
    
    @patch('llm.genai.Client')
    def test_send_prompt_to_gemini_success(self, mock_client_class):
        """Test successful Gemini API call"""
        # Mock the client and response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "This is a test response from Gemini."
        mock_client.models.generate_content.return_value = mock_response
        
        result = send_prompt_to_gemini("Test prompt", "fake-api-key", search_enabled=False)
        
        self.assertEqual(result, "This is a test response from Gemini.")
        mock_client.models.generate_content.assert_called_once()
    
    @patch('llm.genai.Client')
    def test_send_prompt_to_gemini_with_search(self, mock_client_class):
        """Test Gemini API call with web search enabled"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "Response with web search."
        mock_client.models.generate_content.return_value = mock_response
        
        result = send_prompt_to_gemini("Test prompt", "fake-api-key", search_enabled=True)
        
        self.assertEqual(result, "Response with web search.")
        
        # Check that generate_content was called with search tools
        call_args = mock_client.models.generate_content.call_args
        config = call_args[1]['config']
        self.assertIn('tools', config.__dict__)
    
    @patch('llm.genai.Client')
    def test_send_prompt_to_gemini_error(self, mock_client_class):
        """Test Gemini API error handling"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API Error")
        
        with self.assertRaises(Exception):
            send_prompt_to_gemini("Test prompt", "fake-api-key")
    
    @patch('llm.requests.post')
    def test_send_prompt_to_perplexity_success(self, mock_post):
        """Test successful Perplexity API call without search (default)"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Perplexity response'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = send_prompt_to_perplexity("Test prompt", "fake-api-key")
        
        self.assertEqual(result, "Perplexity response")
        mock_post.assert_called_once()
        
        # Verify search is disabled by default
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        self.assertFalse(request_data['search'])
        self.assertEqual(request_data['model'], 'llama-3.1-sonar-small-128k-online')
    
    @patch('llm.requests.post')
    def test_send_prompt_to_perplexity_with_search(self, mock_post):
        """Test Perplexity API call with search enabled"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Search-enabled response'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = send_prompt_to_perplexity("Test prompt", "fake-api-key", search_enabled=True)
        
        self.assertEqual(result, "Search-enabled response")
        
        # Verify search is enabled when requested
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        self.assertTrue(request_data['search'])
    
    @patch('llm.requests.post')
    def test_send_prompt_to_perplexity_error(self, mock_post):
        """Test Perplexity API error handling"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_response.text = "Error details"
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception):
            send_prompt_to_perplexity("Test prompt", "fake-api-key")

if __name__ == '__main__':
    unittest.main()