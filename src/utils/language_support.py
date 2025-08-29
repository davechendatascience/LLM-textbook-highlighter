"""
Language Support Module
Handles internationalization and language detection
"""

import re
from typing import Dict, Optional, List


class LanguageSupport:
    """Handles language detection and internationalization"""
    
    # Language translations for UI
    LANGUAGES = {
        "English": {
            "window_title": "LLM PDF Reader",
            "open_pdf": "Open PDF",
            "previous": "Previous",
            "next": "Next",
            "page": "Page",
            "go_to": "Go to:",
            "go": "Go",
            "zoom": "Zoom:",
            "zoom_in": "Zoom In",
            "zoom_out": "Zoom Out",
            "language": "Language:",
            "auto_detect": "Auto-detect",
            "panel": "Panel:",
            "wider_pdf": "Wider PDF",
            "narrower_pdf": "Narrower PDF",
            "api_configuration": "API Configuration:",
            "perplexity_api_key": "Perplexity API Key:",
            "enter_api_key": "Enter your Perplexity API key",
            "save_key": "Save Key",
            "clear_key": "Clear Key",
            "instructions": "Instructions:\n\n1. Open a PDF file\n2. Select text by clicking and dragging\n3. Extract the selected text\n4. Ask questions or generate questions\n5. Panel: Use Ctrl+Left/Right arrows or toolbar buttons\n\nCross-platform compatible with reliable dropdown functionality",
            "no_selection": "No selection",
            "clear_selection": "Clear Selection",
            "extract_text": "Extract Text",
            "extracted_text": "Extracted Text:",
            "ask_question": "Ask a question:",
            "ask_question_btn": "Ask Question",
            "generate_questions_btn": "Generate Questions",
            "suggested_questions": "Suggested Questions:",
            "font_size": "Font size:",
            "answer_length": "Answer length:",
            "context_window": "Context window:",
            "ask_selected_question": "Ask Selected Question",
            "llm_response": "LLM Response:",
            "small_10pt": "Small (10pt)",
            "medium_12pt": "Medium (12pt)",
            "large_14pt": "Large (14pt)",
            "extra_large_20pt": "Extra Large (20pt)",
            "short_tokens": "Short (< 250 tokens)",
            "medium_tokens": "Medium (250-500 tokens)",
            "long_tokens": "Long (500-1000 tokens)",
            "comprehensive_tokens": "Comprehensive (> 1000 tokens)",
            "context_0": "±0 pages (selected only)",
            "context_1": "±1 page",
            "context_2": "±2 pages",
            "context_5": "±5 pages",
            "no_question": "No Question",
            "please_enter_question": "Please enter a question.",
            "no_text": "No Text",
            "please_extract_text": "Please extract some text first.",
            "api_key_missing": "API key missing",
            "llm_error": "LLM error",
            "error_occurred": "Error occurred",
            "select_question": "Please select a question from the dropdown.",
            "question_generation_failed": "Question generation failed",
            "no_valid_questions": "No valid questions generated",
            "question_answered": "Question answered in {language} ({chars} characters)",
            "generated_questions": "Generated {count} questions in {language}",
            "language_selection": "Language Selection",
            "select_language": "Please select your preferred language:",
            "ok": "OK",
            "cancel": "Cancel",
            "api_key_configured": "API Key: ✓ Configured",
            "research_assistant": "Research Assistant",
            "search_for_papers": "Search for papers...",
            "search": "Search",
            "category": "Category:",
            "max_results": "Max Results:",
            "download_paper": "Download Paper",
            "find_related": "Find Related",
            "controls": "Controls",
            "extract_text_btn": "Extract Text",
            "ask_question_btn": "Ask Question",
            "generate_questions_btn": "Generate Questions",
            "find_related_papers": "Find Related Papers",
            "context_window_label": "Context Window:",
            "select_text_placeholder": "Select text from PDF to extract...",
            "ask_question_placeholder": "Ask a question about the extracted text...",
            "about_title": "About LLM PDF Reader",
            "about_text": "LLM PDF Reader v1.0\n\nAn intelligent PDF reader powered by Perplexity AI.\nFeatures include text extraction, AI-powered questions, and research paper discovery.",
            "wider_pdf": "Wider",
            "narrower_pdf": "Narrower",
            "pdf_width": "PDF Width:",
            "question_label": "Question:",
            "answer_length_label": "Answer Length:",
            "extracted_text_tab": "Extracted Text",
            "ai_response_tab": "AI Response",
            "enhance_with_research": "Enhance with Research",
            "enhance_with_research_tooltip": "Automatically find and include related research papers",
            "related_research_papers": "Related Research Papers",
            "research_context_note": "These papers provide additional context and research background for the topics discussed above.",
            "api_key_label": "API Key:",
            "configure_api_key": "Configure API Key",
            "change_api_key": "Change API Key",
            "test_connection": "Test Connection",
            "api_key_configured": "✅ Configured",
            "api_key_not_configured": "❌ Not Configured",
            "api_key_saved": "API key saved successfully!",
            "no_api_key_to_test": "No API key configured to test.",
            "api_test_failed": "API test failed",
            "api_test_successful": "API connection test successful!",
            "api_test_error": "API test error"
        },
        "Chinese": {
            "window_title": "LLM PDF 阅读器",
            "open_pdf": "打开PDF",
            "previous": "上一页",
            "next": "下一页",
            "page": "页面",
            "zoom": "缩放:",
            "extract_text": "提取文本",
            "ask_question_btn": "提问",
            "generate_questions_btn": "生成问题",
            "research_assistant": "研究助手",
            "search_for_papers": "搜索论文...",
            "search": "搜索",
            "category": "分类:",
            "max_results": "最大结果数:",
            "download_paper": "下载论文",
            "find_related": "查找相关",
            "controls": "控制",
            "context_window_label": "上下文窗口:",
            "select_text_placeholder": "从PDF中选择文本进行提取...",
            "ask_question_placeholder": "询问关于提取文本的问题...",
            "about_title": "关于 LLM PDF 阅读器",
            "about_text": "LLM PDF 阅读器 v1.0\n\n由 Perplexity AI 驱动的智能PDF阅读器。\n功能包括文本提取、AI驱动的问题生成和研究论文发现。",
            "wider_pdf": "更宽",
            "narrower_pdf": "更窄",
            "pdf_width": "PDF宽度:",
            "question_label": "问题:",
            "answer_length_label": "答案长度:",
            "extracted_text_tab": "提取文字",
            "ai_response_tab": "AI回應",
            "enhance_with_research": "增强研究",
            "enhance_with_research_tooltip": "自动查找并包含相关研究论文",
            "related_research_papers": "相关研究论文",
            "research_context_note": "这些论文为上述讨论的主题提供了额外的背景和研究背景。",
            "api_key_label": "API密钥:",
            "configure_api_key": "配置API密钥",
            "change_api_key": "更改API密钥",
            "test_connection": "测试连接",
            "api_key_configured": "✅ 已配置",
            "api_key_not_configured": "❌ 未配置",
            "api_key_saved": "API密钥保存成功！",
            "no_api_key_to_test": "没有配置API密钥进行测试。",
            "api_test_failed": "API测试失败",
            "api_test_successful": "API连接测试成功！",
            "api_test_error": "API测试错误"
        },
        "Traditional Chinese": {
            "window_title": "LLM PDF 閱讀器",
            "open_pdf": "開啟PDF",
            "previous": "上一頁",
            "next": "下一頁",
            "page": "頁面",
            "zoom": "縮放:",
            "extract_text": "提取文字",
            "ask_question_btn": "提問",
            "generate_questions_btn": "生成問題",
            "research_assistant": "研究助手",
            "search_for_papers": "搜尋論文...",
            "search": "搜尋",
            "category": "分類:",
            "max_results": "最大結果數:",
            "download_paper": "下載論文",
            "find_related": "查找相關",
            "controls": "控制",
            "context_window_label": "上下文視窗:",
            "select_text_placeholder": "從PDF中選擇文字進行提取...",
            "ask_question_placeholder": "詢問關於提取文字的問題...",
            "about_title": "關於 LLM PDF 閱讀器",
            "about_text": "LLM PDF 閱讀器 v1.0\n\n由 Perplexity AI 驅動的智能PDF閱讀器。\n功能包括文字提取、AI驅動的問題生成和研究論文發見。",
            "wider_pdf": "更寬",
            "narrower_pdf": "更窄",
            "pdf_width": "PDF寬度:",
            "question_label": "問題:",
            "answer_length_label": "答案長度:",
            "extracted_text_tab": "提取文字",
            "ai_response_tab": "AI回應",
            "enhance_with_research": "增強研究",
            "enhance_with_research_tooltip": "自動查找並包含相關研究論文",
            "related_research_papers": "相關研究論文",
            "research_context_note": "這些論文為上述討論的主題提供了額外的背景和研究背景。",
            "api_key_label": "API密鑰:",
            "configure_api_key": "配置API密鑰",
            "change_api_key": "更改API密鑰",
            "test_connection": "測試連接",
            "api_key_configured": "✅ 已配置",
            "api_key_not_configured": "❌ 未配置",
            "api_key_saved": "API密鑰保存成功！",
            "no_api_key_to_test": "沒有配置API密鑰進行測試。",
            "api_test_failed": "API測試失敗",
            "api_test_successful": "API連接測試成功！",
            "api_test_error": "API測試錯誤"
        },
        "Japanese": {
            "window_title": "LLM PDF リーダー",
            "open_pdf": "PDFを開く",
            "previous": "前へ",
            "next": "次へ",
            "page": "ページ",
            "zoom": "ズーム:",
            "extract_text": "テキスト抽出",
            "ask_question_btn": "質問する",
            "generate_questions_btn": "質問生成",
            "research_assistant": "研究アシスタント",
            "search_for_papers": "論文を検索...",
            "search": "検索",
            "category": "カテゴリ:",
            "max_results": "最大結果数:",
            "download_paper": "論文をダウンロード",
            "find_related": "関連を検索",
            "controls": "コントロール",
            "context_window_label": "コンテキストウィンドウ:",
            "select_text_placeholder": "PDFからテキストを選択して抽出...",
            "ask_question_placeholder": "抽出されたテキストについて質問...",
            "about_title": "LLM PDF リーダーについて",
            "about_text": "LLM PDF リーダー v1.0\n\nPerplexity AI 搭載のインテリジェントPDFリーダー。\nテキスト抽出、AI駆動の質問生成、研究論文発見機能を提供。",
            "wider_pdf": "広く",
            "narrower_pdf": "狭く",
            "pdf_width": "PDF幅:",
            "question_label": "質問:",
            "answer_length_label": "回答の長さ:",
            "extracted_text_tab": "抽出されたテキスト",
            "ai_response_tab": "AI応答",
            "enhance_with_research": "研究を強化",
            "enhance_with_research_tooltip": "関連する研究論文を自動的に検索して含める",
            "related_research_papers": "関連研究論文",
            "research_context_note": "これらの論文は、上記で議論されたトピックの追加コンテキストと研究背景を提供します。",
            "api_key_label": "APIキー:",
            "configure_api_key": "APIキーを設定",
            "change_api_key": "APIキーを変更",
            "test_connection": "接続をテスト",
            "api_key_configured": "✅ 設定済み",
            "api_key_not_configured": "❌ 未設定",
            "api_key_saved": "APIキーが正常に保存されました！",
            "no_api_key_to_test": "テストするAPIキーが設定されていません。",
            "api_test_failed": "APIテストが失敗しました",
            "api_test_successful": "API接続テストが成功しました！",
            "api_test_error": "APIテストエラー"
        }
    }
    
    def __init__(self, default_language: str = "English"):
        self.current_language = default_language
        self.detected_language = None
        
    def set_language(self, language: str):
        """Set the current language"""
        if language in self.LANGUAGES:
            self.current_language = language
        else:
            print(f"Warning: Language '{language}' not supported, using English")
            self.current_language = "English"
            
    def get_text(self, key: str, language: Optional[str] = None) -> str:
        """Get translated text for a key"""
        lang = language or self.current_language
        
        if lang in self.LANGUAGES and key in self.LANGUAGES[lang]:
            return self.LANGUAGES[lang][key]
        elif key in self.LANGUAGES["English"]:
            # Fallback to English
            return self.LANGUAGES["English"][key]
        else:
            # Return the key itself if not found
            return key
            
    def detect_language(self, text: str) -> str:
        """Detect the language of the given text"""
        if not text:
            return "English"
            
        # Count characters by script
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
        korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
        arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
        cyrillic_chars = len(re.findall(r'[\u0400-\u04ff]', text))
        thai_chars = len(re.findall(r'[\u0e00-\u0e7f]', text))
        devanagari_chars = len(re.findall(r'[\u0900-\u097f]', text))
        
        # Count total non-ASCII characters
        total_non_ascii = len(re.findall(r'[^\x00-\x7f]', text))
        
        # Determine language based on character counts
        if chinese_chars > 10:
            return "Chinese"
        elif japanese_chars > 10:
            return "Japanese"
        elif korean_chars > 10:
            return "Korean"
        elif arabic_chars > 10:
            return "Arabic"
        elif cyrillic_chars > 10:
            return "Russian"
        elif thai_chars > 10:
            return "Thai"
        elif devanagari_chars > 10:
            return "Hindi"
        elif total_non_ascii > 20:
            return "Non-English"
        else:
            return "English"
            
    def get_language_instruction(self, language: str) -> str:
        """Get language-specific instruction for LLM prompts"""
        language_instructions = {
            "Chinese": "请用中文回答。请用中文生成问题。",
            "Traditional Chinese": "請用繁體中文回答。請用繁體中文生成問題。",
            "Japanese": "日本語で答えてください。日本語で質問を生成してください。",
            "Korean": "한국어로 답변해 주세요. 한국어로 질문을 생성해 주세요.",
            "Arabic": "يرجى الإجابة باللغة العربية. يرجى إنشاء الأسئلة باللغة العربية.",
            "Russian": "Пожалуйста, отвечайте на русском языке. Пожалуйста, создавайте вопросы на русском языке.",
            "Thai": "กรุณาตอบเป็นภาษาไทย กรุณาสร้างคำถามเป็นภาษาไทย",
            "Hindi": "कृपया हिंदी में जवाब दें। कृपया हिंदी में प्रश्न उत्पन्न करें।",
            "Non-English": "Please respond in the same language as the text. Please generate questions in the same language as the text.",
            "English": "Please respond in English. Please generate questions in English."
        }
        return language_instructions.get(language, "Please respond in the same language as the text.")
        
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.LANGUAGES.keys())
        
    def format_message(self, key: str, **kwargs) -> str:
        """Format a message with placeholders"""
        message = self.get_text(key)
        try:
            return message.format(**kwargs)
        except KeyError:
            return message
            
    def get_context_window_options(self) -> List[str]:
        """Get context window options for the current language"""
        return [
            self.get_text("context_0"),
            self.get_text("context_1"),
            self.get_text("context_2"),
            "±3 pages",
            "±4 pages",
            self.get_text("context_5")
        ]
        
    def get_font_size_options(self) -> List[str]:
        """Get font size options for the current language"""
        return [
            self.get_text("small_10pt"),
            self.get_text("medium_12pt"),
            self.get_text("large_14pt"),
            self.get_text("extra_large_20pt")
        ]
        
    def get_answer_length_options(self) -> List[str]:
        """Get answer length options for the current language"""
        return [
            self.get_text("short_tokens"),
            self.get_text("medium_tokens"),
            self.get_text("long_tokens"),
            self.get_text("comprehensive_tokens")
        ]
