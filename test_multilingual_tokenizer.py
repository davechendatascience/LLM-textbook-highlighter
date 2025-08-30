#!/usr/bin/env python3
"""
Test Multilingual Tokenizer
Tests the multilingual tokenizer functionality for various languages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.multilingual_tokenizer import MultilingualTokenizer, get_tokenizer
import tiktoken


def test_basic_tokenizer():
    """Test basic tokenizer functionality"""
    print("🧪 Testing basic tokenizer functionality...")
    
    # Test multilingual tokenizer
    multi_tokenizer = MultilingualTokenizer()
    tiktoken_tokenizer = tiktoken.get_encoding("cl100k_base")
    
    # Test English text
    english_text = "This is a test of the multilingual tokenizer."
    multi_tokens = multi_tokenizer.encode(english_text)
    tiktoken_tokens = tiktoken_tokenizer.encode(english_text)
    
    print(f"English text: '{english_text}'")
    print(f"Multilingual tokens: {len(multi_tokens)} tokens")
    print(f"Tiktoken tokens: {len(tiktoken_tokens)} tokens")
    print(f"Token count match: {len(multi_tokens) == len(tiktoken_tokens)}")
    print()


def test_chinese_tokenizer():
    """Test Chinese text tokenization"""
    print("🧪 Testing Chinese text tokenization...")
    
    multi_tokenizer = MultilingualTokenizer()
    
    # Test Chinese text
    chinese_text = "這是一個多語言標記器的測試。我們需要確保中文文本能夠正確處理。"
    tokens = multi_tokenizer.encode(chinese_text)
    
    print(f"Chinese text: '{chinese_text}'")
    print(f"Character count: {len(chinese_text)}")
    print(f"Token count: {len(tokens)}")
    print(f"Tokens: {tokens[:10]}...")  # Show first 10 tokens
    
    # Test decoding
    decoded_text = multi_tokenizer.decode(tokens)
    print(f"Decoded text: '{decoded_text}'")
    print(f"Decoding successful: {decoded_text == chinese_text}")
    print()


def test_mixed_language_detection():
    """Test mixed language detection"""
    print("🧪 Testing mixed language detection...")
    
    multi_tokenizer = MultilingualTokenizer()
    
    # Test mixed Chinese-English text
    mixed_text = "This is a mixed 中文 and English 文本 test."
    
    is_mixed = multi_tokenizer.is_mixed_language(mixed_text)
    detected_lang = multi_tokenizer.detect_language_robust(mixed_text)
    
    print(f"Mixed text: '{mixed_text}'")
    print(f"Is mixed language: {is_mixed}")
    print(f"Detected language: {detected_lang}")
    print()


def test_chunking_functionality():
    """Test text chunking functionality"""
    print("🧪 Testing text chunking functionality...")
    
    multi_tokenizer = MultilingualTokenizer()
    
    # Test English chunking
    english_text = "This is a longer text that should be chunked into smaller pieces. " * 20
    english_chunks = multi_tokenizer.chunk_text(english_text, max_tokens=50, overlap=10)
    
    print(f"English text length: {len(english_text)} characters")
    print(f"English chunks: {len(english_chunks)} chunks")
    for i, chunk in enumerate(english_chunks[:3]):  # Show first 3 chunks
        print(f"  Chunk {i+1}: '{chunk[:50]}...'")
    
    # Test Chinese chunking
    chinese_text = "這是一個較長的文本，應該被分割成較小的片段。" * 20
    chinese_chunks = multi_tokenizer.chunk_text(chinese_text, max_tokens=50, overlap=10)
    
    print(f"\nChinese text length: {len(chinese_text)} characters")
    print(f"Chinese chunks: {len(chinese_chunks)} chunks")
    for i, chunk in enumerate(chinese_chunks[:3]):  # Show first 3 chunks
        print(f"  Chunk {i+1}: '{chunk[:20]}...'")
    print()


def test_vector_store_integration():
    """Test integration with vector store chunking"""
    print("🧪 Testing vector store integration...")
    
    from src.services.vector_store import VectorStoreService
    
    # Test with multilingual tokenizer
    vector_store_multi = VectorStoreService(use_multilingual_tokenizer=True)
    
    # Test with standard tokenizer
    vector_store_standard = VectorStoreService(use_multilingual_tokenizer=False)
    
    # Test text
    test_text = "This is a test document with some Chinese content: 這是一個測試文檔。"
    
    print(f"Test text: '{test_text}'")
    
    # Compare chunking
    multi_chunks = vector_store_multi.chunk_text(test_text, max_tokens=100, overlap=20)
    standard_chunks = vector_store_standard.chunk_text(test_text, max_tokens=100, overlap=20)
    
    print(f"Multilingual chunks: {len(multi_chunks)}")
    print(f"Standard chunks: {len(standard_chunks)}")
    
    for i, (multi_chunk, standard_chunk) in enumerate(zip(multi_chunks, standard_chunks)):
        print(f"Chunk {i+1}:")
        print(f"  Multilingual: '{multi_chunk[:50]}...'")
        print(f"  Standard: '{standard_chunk[:50]}...'")
        print()
    print()


def test_context_retrieval_simulation():
    """Simulate context retrieval to test if chunks are appropriate"""
    print("🧪 Testing context retrieval simulation...")
    
    from src.services.vector_store import VectorStoreService
    
    # Create a test document with mixed content
    test_document = """
    Introduction to Machine Learning
    
    Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed.
    
    機器學習是人工智能的一個子集，它使計算機能夠學習並做出決策，而無需明確編程。
    
    Key Concepts:
    1. Supervised Learning: Learning from labeled data
    2. Unsupervised Learning: Finding patterns in unlabeled data
    3. Reinforcement Learning: Learning through interaction with environment
    
    主要概念：
    1. 監督學習：從標記數據中學習
    2. 無監督學習：在未標記數據中尋找模式
    3. 強化學習：通過與環境互動來學習
    
    Applications:
    - Natural Language Processing
    - Computer Vision
    - Recommendation Systems
    
    應用：
    - 自然語言處理
    - 計算機視覺
    - 推薦系統
    """
    
    # Test with multilingual tokenizer
    vector_store = VectorStoreService(use_multilingual_tokenizer=True)
    
    # Chunk the document
    chunks = vector_store.chunk_text(test_document, max_tokens=150, overlap=30)
    
    print(f"Document length: {len(test_document)} characters")
    print(f"Number of chunks: {len(chunks)}")
    print()
    
    # Simulate context retrieval
    query = "什麼是機器學習？"  # "What is machine learning?" in Chinese
    
    print(f"Query: '{query}'")
    print("Retrieved context chunks:")
    
    for i, chunk in enumerate(chunks):
        # Simple relevance check (in real implementation, this would use embeddings)
        relevance_score = 0
        if "機器學習" in chunk or "machine learning" in chunk.lower():
            relevance_score = 1
        if "學習" in chunk or "learning" in chunk.lower():
            relevance_score += 0.5
        
        if relevance_score > 0:
            print(f"Chunk {i+1} (relevance: {relevance_score}):")
            print(f"  '{chunk.strip()[:100]}...'")
            print()
    
    print()


def test_token_count_accuracy():
    """Test token counting accuracy"""
    print("🧪 Testing token counting accuracy...")
    
    multi_tokenizer = MultilingualTokenizer()
    tiktoken_tokenizer = tiktoken.get_encoding("cl100k_base")
    
    test_cases = [
        "Simple English text for testing.",
        "這是一個中文測試文本。",
        "Mixed 中文 and English text 混合文本。",
        "This is a longer English text that should have more tokens than the previous examples. " * 5,
        "這是一個較長的中文文本，應該比前面的例子有更多的標記。" * 5
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"Test case {i}: '{text[:50]}...'")
        
        multi_count = multi_tokenizer.count_tokens(text)
        tiktoken_count = len(tiktoken_tokenizer.encode(text))
        
        print(f"  Multilingual count: {multi_count}")
        print(f"  Tiktoken count: {tiktoken_count}")
        print(f"  Difference: {abs(multi_count - tiktoken_count)}")
        print()


def test_cjk_script_detection():
    """Test CJK script detection"""
    print("🧪 Testing CJK script detection...")
    
    multi_tokenizer = MultilingualTokenizer()
    
    test_cases = [
        ("純中文", "Chinese"),
        ("日本語のテスト", "Japanese"),
        ("한국어 테스트", "Korean"),
        ("Mixed 中文 and English", "Mixed"),
        ("Pure English text", "English")
    ]
    
    for text, expected in test_cases:
        is_cjk = multi_tokenizer.is_cjk_script(text)
        detected_lang = multi_tokenizer.detect_language_robust(text)
        
        print(f"Text: '{text}'")
        print(f"  Expected: {expected}")
        print(f"  Is CJK: {is_cjk}")
        print(f"  Detected: {detected_lang}")
        print()


def test_language_detection_robustness():
    """Test the robustness of language detection"""
    print("🧪 Testing language detection robustness...")
    
    multi_tokenizer = MultilingualTokenizer()
    
    test_cases = [
        ("Hello world", "en"),
        ("你好世界", "zh"),
        ("こんにちは世界", "ja"),
        ("안녕하세요 세계", "ko"),
        ("مرحبا بالعالم", "ar"),
        ("Привет мир", "ru"),
        ("สวัสดีชาวโลก", "th"),
        ("नमस्ते दुनिया", "hi"),
        ("Hello 世界", "mixed"),
        ("", "en")
    ]
    
    for text, expected in test_cases:
        detected = multi_tokenizer.detect_language_robust(text)
        correct = detected == expected
        print(f"Text: '{text}' -> Detected: {detected}, Expected: {expected}, Correct: {correct}")
    print()


def main():
    """Run all tests"""
    print("🚀 Starting Multilingual Tokenizer Tests")
    print("=" * 50)
    
    try:
        test_basic_tokenizer()
        test_chinese_tokenizer()
        test_mixed_language_detection()
        test_chunking_functionality()
        test_vector_store_integration()
        test_context_retrieval_simulation()
        test_token_count_accuracy()
        test_cjk_script_detection()
        test_language_detection_robustness()
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
