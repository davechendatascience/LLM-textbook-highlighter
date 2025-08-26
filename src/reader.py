#!/usr/bin/env python3
"""
Cross-Platform PDF Highlighter using PySide6
Provides reliable dropdown functionality and professional UI across all platforms
"""

import sys
import os
import platform
from datetime import datetime
from typing import Optional, List, Dict, Any

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit,
    QScrollArea, QFrame, QFileDialog, QMessageBox, QSlider
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QObject
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QImage

# PDF processing
import fitz  # PyMuPDF
from PIL import Image
import io

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm import send_prompt_to_perplexity
from config import load_secrets, get_available_apis, DEFAULT_SETTINGS


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
        "error": "Error",
        "please_enter_api_key": "Please enter a Perplexity API key.",
        "api_key_too_short": "API key appears to be too short. Please check your key.",
        "success": "Success",
        "api_key_saved": "API key saved successfully!",
        "failed_to_save_api_key": "Failed to save API key: ",
        "open_pdf_dialog": "Open PDF",
        "pdf_files": "PDF files",
        "opened_pdf": "Opened PDF: ",
        "pages": "pages",
        "failed_to_open_pdf": "Failed to open PDF file.",
        "invalid_page": "Invalid Page",
        "page_number_out_of_range": "Page number out of range.",
        "invalid_input": "Invalid Input",
        "please_enter_valid_page_number": "Please enter a valid page number.",
        "zoom_fit_to_panel": "Zoom: Fit to panel",
        "font_size_changed": "Font size changed to ",
        "pt": "pt",
        "selected_question": "Selected question: ",
        "selection_completed": "Selection completed. ",
        "click_extract_text_to_get_content": "Click 'Extract Text' to get content.",
        "selection_cleared": "Selection cleared",
        "no_selection": "No Selection",
        "please_select_a_text_region_first": "Please select a text region first.",
        "no_pdf": "No PDF",
        "please_open_a_pdf_first": "Please open a PDF first.",
        "text_extracted": "Text extracted from ",
        "page(s)": " page(s): ",
        "characters": " characters",
        "no_text_found_in_selection": "No text found in the selected region.",
        "error_extracting_text": "Error extracting text: ",
        "error_during_text_extraction": "Error during text extraction",
        "no_question": "No Question",
        "please_enter_a_question": "Please enter a question.",
        "please_enter_a_question_or_select_from_dropdown": "Please enter a question or select one from the dropdown.",
        "no_text": "No Text",
        "please_extract_some_text_first": "Please extract some text first.",
        "error_api_key_not_configured": "Error: Perplexity API key not configured. Please enter your API key in the configuration section.",
        "based_on_text_prompt": "Based on the following text, please answer this question:",
        "text": "Text",
        "question": "Question",
        "please_provide_clear_and_accurate_answer_based_only_on_information_in_text_above": "Please provide a clear and accurate answer based only on the information in the text above.",
        "error_could_not_get_response_from_llm": "Error: Could not get response from LLM. ",
        "please_check_your_api_key": "Please check your API key.",
        "perplexity_api_key_not_configured": "Perplexity API key not configured. ",
        "please_enter_your_api_key_in_the_configuration_section": "Please enter your API key in the configuration section.",
        "based_on_text_generate_questions": "Based on the following text, generate exactly 5 relevant questions that could be asked about this content.",
        "make_questions_diverse_and_interesting": "Make the questions diverse and interesting, covering different aspects of the text.",
        "cover_different_aspects_of_the_text": "Cover different aspects of the text.",
        "instructions": "Instructions",
        "generate_exactly_5_questions": "- Generate exactly 5 questions",
        "each_question_should_be_on_its_own_line": "- Each question should be on its own line",
        "do_not_use_numbering": "- Do not use numbering (1., 2., etc.)",
        "do_not_use_bullet_points": "- Do not use bullet points (-, •, *)",
        "make_questions_clear_and_specific": "- Make questions clear and specific",
        "questions": "Questions",
        "could_not_generate_questions": "Could not generate questions. ",
        "no_valid_questions_generated": "No valid questions generated",
        "error_generating_questions": "Error generating questions: ",
        "please_select_a_question_from_the_dropdown": "Please select a question from the dropdown.",
        "error_perplexity_api_key_not_configured": "Error: Perplexity API key not configured. ",
        "based_on_text_please_answer_this_question": "Based on the following text, please answer this question:",
        "please_provide_a_clear_and_accurate_answer_based_only_on_information_in_the_text_above": "Please provide a clear and accurate answer based only on the information in the text above."
    },
    "Traditional Chinese": {
        "window_title": "LLM PDF 閱讀器",
        "open_pdf": "開啟PDF",
        "previous": "上一頁",
        "next": "下一頁",
        "page": "頁面",
        "go_to": "跳轉到:",
        "go": "跳轉",
        "zoom": "縮放:",
        "zoom_in": "放大",
        "zoom_out": "縮小",
        "language": "語言:",
        "auto_detect": "自動檢測",
        "panel": "面板:",
        "wider_pdf": "加寬PDF",
        "narrower_pdf": "收窄PDF",
        "api_configuration": "API 配置:",
        "perplexity_api_key": "Perplexity API 金鑰:",
        "enter_api_key": "輸入您的 Perplexity API 金鑰",
        "save_key": "儲存金鑰",
        "clear_key": "清除金鑰",
        "instructions": "使用說明:\n\n1. 開啟PDF檔案\n2. 透過點擊和拖拽選擇文字\n3. 提取選中的文字\n4. 提問或生成問題\n5. 面板: 使用 Ctrl+左/右箭頭或工具列按鈕\n\n跨平台相容，具有可靠的下拉功能",
        "no_selection": "未選擇",
        "clear_selection": "清除選擇",
        "extract_text": "提取文字",
        "extracted_text": "提取的文字:",
        "ask_question": "提問:",
        "ask_question_btn": "提問",
        "generate_questions_btn": "生成問題",
        "suggested_questions": "建議問題:",
        "font_size": "字體大小:",
        "answer_length": "答案長度:",
        "context_window": "上下文視窗:",
        "ask_selected_question": "詢問選中問題",
        "llm_response": "LLM 回答:",
        "small_10pt": "小 (10pt)",
        "medium_12pt": "中 (12pt)",
        "large_14pt": "大 (14pt)",
        "extra_large_20pt": "特大 (20pt)",
        "short_tokens": "短 (< 250 詞)",
        "medium_tokens": "中 (250-500 詞)",
        "long_tokens": "長 (500-1000 詞)",
        "comprehensive_tokens": "全面 (> 1000 詞)",
        "context_0": "±0 頁 (僅選中)",
        "context_1": "±1 頁",
        "context_2": "±2 頁",
        "context_5": "±5 頁",
        "no_question": "無問題",
        "please_enter_question": "請輸入問題。",
        "no_text": "無文字",
        "please_extract_text": "請先提取一些文字。",
        "api_key_missing": "缺少API金鑰",
        "llm_error": "LLM錯誤",
        "error_occurred": "發生錯誤",
        "select_question": "請從下拉選單中選擇問題。",
        "question_generation_failed": "問題生成失敗",
        "no_valid_questions": "未生成有效問題",
        "question_answered": "問題已回答 ({chars} 字元)",
        "generated_questions": "生成了 {count} 個問題",
        "language_selection": "語言選擇",
        "select_language": "請選擇您偏好的語言:",
        "ok": "確定",
        "cancel": "取消",
        "api_key_configured": "API 金鑰: ✓ 已配置",
        "error": "錯誤",
        "please_enter_api_key": "請輸入 Perplexity API 金鑰。",
        "api_key_too_short": "API 金鑰似乎太短。請檢查您的金鑰。",
        "success": "成功",
        "api_key_saved": "API 金鑰儲存成功！",
        "failed_to_save_api_key": "儲存 API 金鑰失敗: ",
        "open_pdf_dialog": "開啟PDF",
        "pdf_files": "PDF 檔案",
        "opened_pdf": "已開啟 PDF: ",
        "pages": "頁",
        "failed_to_open_pdf": "開啟 PDF 檔案失敗。",
        "invalid_page": "無效頁面",
        "page_number_out_of_range": "頁碼超出範圍。",
        "invalid_input": "無效輸入",
        "please_enter_valid_page_number": "請輸入有效的頁碼。",
        "zoom_fit_to_panel": "縮放: 適合面板",
        "font_size_changed": "字體大小已更改為 ",
        "pt": "pt",
        "selected_question": "選中的問題: ",
        "selection_completed": "選擇完成。",
        "click_extract_text_to_get_content": "點擊「提取文字」以取得內容。",
        "selection_cleared": "選擇已清除",
        "no_selection": "無選擇",
        "please_select_a_text_region_first": "請先選擇文字區域。",
        "no_pdf": "無PDF",
        "please_open_a_pdf_first": "請先開啟 PDF。",
        "text_extracted": "已從 ",
        "page(s)": " 頁提取文字: ",
        "characters": " 字元",
        "no_text_found_in_selection": "在選中的區域中未找到文字。",
        "error_extracting_text": "提取文字時發生錯誤: ",
        "error_during_text_extraction": "文字提取期間發生錯誤",
        "no_question": "無問題",
        "please_enter_a_question": "請輸入問題。",
        "please_enter_a_question_or_select_from_dropdown": "請輸入問題或從下拉選單中選擇一個。",
        "no_text": "無文字",
        "please_extract_some_text_first": "請先提取一些文字。",
        "error_api_key_not_configured": "錯誤: Perplexity API 金鑰未配置。請在配置區段中輸入您的 API 金鑰。",
        "based_on_text_prompt": "根據以下文字，請回答這個問題:",
        "text": "文字",
        "question": "問題",
        "please_provide_clear_and_accurate_answer_based_only_on_information_in_text_above": "請僅根據上述文字中的資訊提供清楚且準確的答案。",
        "error_could_not_get_response_from_llm": "錯誤: 無法從 LLM 取得回應。",
        "please_check_your_api_key": "請檢查您的 API 金鑰。",
        "perplexity_api_key_not_configured": "Perplexity API 金鑰未配置。",
        "please_enter_your_api_key_in_the_configuration_section": "請在配置區段中輸入您的 API 金鑰。",
        "based_on_text_generate_questions": "根據以下文字，生成恰好 5 個可以詢問此內容的相關問題。",
        "make_questions_diverse_and_interesting": "使問題多樣化且有趣，涵蓋文字的不同面向。",
        "cover_different_aspects_of_the_text": "涵蓋文字的不同面向。",
        "instructions": "說明",
        "generate_exactly_5_questions": "- 生成恰好 5 個問題",
        "each_question_should_be_on_its_own_line": "- 每個問題應該在自己的行上",
        "do_not_use_numbering": "- 不要使用編號 (1., 2., 等)",
        "do_not_use_bullet_points": "- 不要使用項目符號 (-, •, *)",
        "make_questions_clear_and_specific": "- 使問題清楚且具體",
        "questions": "問題",
        "could_not_generate_questions": "無法生成問題。",
        "no_valid_questions_generated": "未生成有效問題",
        "error_generating_questions": "生成問題時發生錯誤: ",
        "please_select_a_question_from_the_dropdown": "請從下拉選單中選擇問題。",
        "error_perplexity_api_key_not_configured": "錯誤: Perplexity API 金鑰未配置。",
        "based_on_text_please_answer_this_question": "根據以下文字，請回答這個問題:",
        "please_provide_a_clear_and_accurate_answer_based_only_on_information_in_the_text_above": "請僅根據上述文字中的資訊提供清楚且準確的答案。"
    },
    "Chinese": {
        "window_title": "LLM PDF 阅读器",
        "open_pdf": "打开PDF",
        "previous": "上一页",
        "next": "下一页",
        "page": "页面",
        "go_to": "跳转到:",
        "go": "跳转",
        "zoom": "缩放:",
        "zoom_in": "放大",
        "zoom_out": "缩小",
        "language": "语言:",
        "auto_detect": "自动检测",
        "panel": "面板:",
        "wider_pdf": "加宽PDF",
        "narrower_pdf": "收窄PDF",
        "api_configuration": "API 配置:",
        "perplexity_api_key": "Perplexity API 密钥:",
        "enter_api_key": "输入您的 Perplexity API 密钥",
        "save_key": "保存密钥",
        "clear_key": "清除密钥",
        "instructions": "使用说明:\n\n1. 打开PDF文件\n2. 通过点击和拖拽选择文本\n3. 提取选中的文本\n4. 提问或生成问题\n5. 面板: 使用 Ctrl+左/右箭头或工具栏按钮\n\n跨平台兼容，具有可靠的下拉功能",
        "no_selection": "未选择",
        "clear_selection": "清除选择",
        "extract_text": "提取文本",
        "extracted_text": "提取的文本:",
        "ask_question": "提问:",
        "ask_question_btn": "提问",
        "generate_questions_btn": "生成问题",
        "suggested_questions": "建议问题:",
        "font_size": "字体大小:",
        "answer_length": "答案长度:",
        "context_window": "上下文窗口:",
        "ask_selected_question": "询问选中问题",
        "llm_response": "LLM 回答:",
        "small_10pt": "小 (10pt)",
        "medium_12pt": "中 (12pt)",
        "large_14pt": "大 (14pt)",
        "extra_large_20pt": "特大 (20pt)",
        "short_tokens": "短 (< 250 词)",
        "medium_tokens": "中 (250-500 词)",
        "long_tokens": "长 (500-1000 词)",
        "comprehensive_tokens": "全面 (> 1000 词)",
        "context_0": "±0 页 (仅选中)",
        "context_1": "±1 页",
        "context_2": "±2 页",
        "context_5": "±5 页",
        "no_question": "无问题",
        "please_enter_question": "请输入问题。",
        "please_enter_a_question_or_select_from_dropdown": "请输入问题或从下拉菜单中选择一个。",
        "no_text": "无文本",
        "please_extract_text": "请先提取一些文本。",
        "api_key_missing": "缺少API密钥",
        "llm_error": "LLM错误",
        "error_occurred": "发生错误",
        "select_question": "请从下拉菜单中选择问题。",
        "question_generation_failed": "问题生成失败",
        "no_valid_questions": "未生成有效问题",
        "question_answered": "问题已回答 ({chars} 字符)",
        "generated_questions": "生成了 {count} 个问题",
        "language_selection": "语言选择",
        "select_language": "请选择您偏好的语言:",
        "ok": "确定",
        "cancel": "取消"
    },
    "Japanese": {
        "window_title": "LLM PDF リーダー",
        "open_pdf": "PDFを開く",
        "previous": "前へ",
        "next": "次へ",
        "page": "ページ",
        "go_to": "移動先:",
        "go": "移動",
        "zoom": "ズーム:",
        "zoom_in": "拡大",
        "zoom_out": "縮小",
        "language": "言語:",
        "auto_detect": "自動検出",
        "panel": "パネル:",
        "wider_pdf": "PDFを広く",
        "narrower_pdf": "PDFを狭く",
        "api_configuration": "API設定:",
        "perplexity_api_key": "Perplexity APIキー:",
        "enter_api_key": "Perplexity APIキーを入力してください",
        "save_key": "キーを保存",
        "clear_key": "キーをクリア",
        "instructions": "使用方法:\n\n1. PDFファイルを開く\n2. クリックとドラッグでテキストを選択\n3. 選択したテキストを抽出\n4. 質問するか質問を生成\n5. パネル: Ctrl+左/右矢印またはツールバーボタンを使用\n\nクロスプラットフォーム対応、信頼性の高いドロップダウン機能",
        "no_selection": "選択なし",
        "clear_selection": "選択をクリア",
        "extract_text": "テキストを抽出",
        "extracted_text": "抽出されたテキスト:",
        "ask_question": "質問:",
        "ask_question_btn": "質問する",
        "generate_questions_btn": "質問を生成",
        "suggested_questions": "推奨質問:",
        "font_size": "フォントサイズ:",
        "answer_length": "回答の長さ:",
        "context_window": "コンテキストウィンドウ:",
        "ask_selected_question": "選択した質問を尋ねる",
        "llm_response": "LLM回答:",
        "small_10pt": "小 (10pt)",
        "medium_12pt": "中 (12pt)",
        "large_14pt": "大 (14pt)",
        "extra_large_20pt": "特大 (20pt)",
        "short_tokens": "短い (< 250トークン)",
        "medium_tokens": "中 (250-500トークン)",
        "long_tokens": "長い (500-1000トークン)",
        "comprehensive_tokens": "包括的 (> 1000トークン)",
        "context_0": "±0ページ (選択のみ)",
        "context_1": "±1ページ",
        "context_2": "±2ページ",
        "context_5": "±5ページ",
        "no_question": "質問なし",
        "please_enter_question": "質問を入力してください。",
        "please_enter_a_question_or_select_from_dropdown": "質問を入力するか、ドロップダウンから選択してください。",
        "no_text": "テキストなし",
        "please_extract_text": "まずテキストを抽出してください。",
        "api_key_missing": "APIキーが不足",
        "llm_error": "LLMエラー",
        "error_occurred": "エラーが発生",
        "select_question": "ドロップダウンから質問を選択してください。",
        "question_generation_failed": "質問生成に失敗",
        "no_valid_questions": "有効な質問が生成されませんでした",
        "question_answered": "質問に回答 ({chars} 文字)",
        "generated_questions": "{count}個の質問を生成",
        "language_selection": "言語選択",
        "select_language": "お好みの言語を選択してください:",
        "ok": "OK",
        "cancel": "キャンセル"
    }
}

# Global language variable
CURRENT_LANGUAGE = "English"

def tr(key):
    """Translate a key to the current language"""
    return LANGUAGES.get(CURRENT_LANGUAGE, LANGUAGES["English"]).get(key, key)


class LanguageSelectionDialog(QWidget):
    """Dialog for language selection before main window opens"""
    
    def __init__(self):
        super().__init__()
        self.selected_language = "English"
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the language selection UI"""
        self.setWindowTitle(tr("language_selection"))
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel(tr("select_language"))
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Language dropdown
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "English",
            "Chinese", 
            "Traditional Chinese",
            "Japanese"
        ])
        self.language_combo.setCurrentText("English")
        self.language_combo.setFixedHeight(40)
        layout.addWidget(self.language_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton(tr("ok"))
        self.cancel_btn = QPushButton(tr("cancel"))
        self.ok_btn.setFixedHeight(35)
        self.cancel_btn.setFixedHeight(35)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def accept(self):
        """Accept the language selection"""
        global CURRENT_LANGUAGE
        CURRENT_LANGUAGE = self.language_combo.currentText()
        self.selected_language = CURRENT_LANGUAGE
        self.close()
    
    def reject(self):
        """Cancel and use default language"""
        global CURRENT_LANGUAGE
        CURRENT_LANGUAGE = "English"
        self.selected_language = "English"
        self.close()


class PDFRenderer(QObject):
    """Thread-safe PDF rendering"""
    page_rendered = Signal(QPixmap, int, int)  # pixmap, width, height
    
    def __init__(self):
        super().__init__()
        self.pdf_doc = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.fit_to_panel_zoom = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.zoom_step = 0.25
    
    def load_pdf(self, file_path: str):
        """Load PDF document"""
        try:
            self.pdf_doc = fitz.open(file_path)
            self.current_page = 0
            return len(self.pdf_doc)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return 0
    
    def render_page(self, page_num: int, canvas_width: int, canvas_height: int):
        """Render PDF page with current zoom"""
        if not self.pdf_doc or page_num >= len(self.pdf_doc):
            return
        
        try:
            self.current_page = page_num
            page = self.pdf_doc[page_num]
            
            # Calculate fit-to-panel zoom
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            padding = 20
            fit_width_zoom = (canvas_width - padding) / page_width
            fit_height_zoom = (canvas_height - padding) / page_height
            self.fit_to_panel_zoom = max(min(fit_width_zoom, fit_height_zoom), 0.5)
            
            # Calculate actual zoom
            actual_zoom = self.fit_to_panel_zoom * self.zoom_level
            
            # Render page
            mat = fitz.Matrix(actual_zoom, actual_zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to QPixmap
            image = Image.open(io.BytesIO(img_data))
            qimage = QImage(image.tobytes(), image.width, image.height, 
                          image.width * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            
            self.page_rendered.emit(pixmap, image.width, image.height)
            
        except Exception as e:
            print(f"Error rendering page: {e}")
    
    def set_zoom(self, zoom_level: float):
        """Set zoom level"""
        self.zoom_level = max(self.min_zoom, min(zoom_level, self.max_zoom))
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level + self.zoom_step, self.max_zoom)
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level - self.zoom_step, self.min_zoom)
    
    def reset_zoom(self):
        """Reset to fit panel"""
        self.zoom_level = 1.0
    
    def get_zoom_percentage(self) -> int:
        """Get zoom as percentage"""
        return int(self.zoom_level * 100)


class SelectionOverlay(QWidget):
    """Overlay widget for drawing selection rectangle"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
        # Make overlay transparent
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
    def set_selection(self, start, end, selecting=False):
        """Update selection coordinates"""
        self.selection_start = start
        self.selection_end = end
        self.is_selecting = selecting
        self.update()
        
    def paintEvent(self, event):
        """Paint selection rectangle"""
        if not self.selection_start or not self.selection_end:
            return
            
        painter = QPainter(self)
        painter.setPen(QPen(QColor(255, 0, 0), 3))
        
        # Calculate rectangle coordinates
        x1 = min(self.selection_start.x(), self.selection_end.x())
        y1 = min(self.selection_start.y(), self.selection_end.y())
        x2 = max(self.selection_start.x(), self.selection_end.x())
        y2 = max(self.selection_start.y(), self.selection_end.y())
        
        # Draw selection rectangle
        painter.drawRect(x1, y1, x2 - x1, y2 - y1)


class PDFViewer(QWidget):
    """PDF display widget with selection capabilities"""
    
    def __init__(self, renderer: PDFRenderer):
        super().__init__()
        self.renderer = renderer
        self.current_pixmap = None
        self.is_selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the PDF viewer UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # PDF display area
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setMinimumSize(400, 600)
        self.pdf_label.setStyleSheet("QLabel { background-color: #f5f5f5; border: 2px dashed #ccc; }")
        
        # Set placeholder text when no PDF is loaded
        self.pdf_label.setText("No PDF loaded\n\nClick 'Open PDF' to load a document")
        self.pdf_label.setStyleSheet("QLabel { background-color: #f5f5f5; border: 2px dashed #ccc; color: #666; font-size: 14px; }")
        
        # Scroll area for PDF with visible scrollbars
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.pdf_label)
        scroll_area.setWidgetResizable(False)  # Don't resize widget automatically
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMinimumSize(400, 600)
        layout.addWidget(scroll_area)
        
        # Store reference to scroll area
        self.scroll_area = scroll_area
        
        # Connect scrollbar value changes to clear selection
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.clear_selection_on_scroll)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.clear_selection_on_scroll)
        
        # Create selection overlay
        self.selection_overlay = SelectionOverlay(self.scroll_area.viewport())
        self.selection_overlay.setGeometry(0, 0, 400, 600)
        self.selection_overlay.show()
        
        # Mouse tracking for selection
        self.pdf_label.setMouseTracking(True)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.renderer.page_rendered.connect(self.display_page)
    
    def display_page(self, pixmap: QPixmap, width: int, height: int):
        """Display rendered PDF page"""
        self.current_pixmap = pixmap
        self.pdf_label.setPixmap(pixmap)
        self.pdf_label.resize(width, height)
        
        # Clear placeholder text and update styling when PDF is displayed
        self.pdf_label.setText("")
        self.pdf_label.setStyleSheet("QLabel { background-color: white; border: 1px solid #ccc; }")
        
        # Resize the selection overlay to match the PDF content
        if hasattr(self, 'selection_overlay'):
            self.selection_overlay.setGeometry(0, 0, width, height)
            self.selection_overlay.raise_()  # Ensure overlay is on top
        
        # Ensure scrollbars appear when needed
        if hasattr(self, 'scroll_area'):
            # Force scroll area to update its scroll region
            self.scroll_area.viewport().update()
            
            # Explicitly set scrollbar policies based on content size
            viewport_width = self.scroll_area.viewport().width()
            viewport_height = self.scroll_area.viewport().height()
            
            if width > viewport_width:
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            else:
                self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                
            if height > viewport_height:
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            else:
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.LeftButton and self.current_pixmap:
            self.is_selecting = True
            # Get position relative to this widget
            self.selection_start = event.pos()
            self.selection_end = event.pos()
            # Update the overlay
            if hasattr(self, 'selection_overlay'):
                self.selection_overlay.set_selection(self.selection_start, self.selection_end, True)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for selection"""
        if self.is_selecting and self.current_pixmap:
            # Get position relative to this widget
            self.selection_end = event.pos()
            # Update the overlay
            if hasattr(self, 'selection_overlay'):
                self.selection_overlay.set_selection(self.selection_start, self.selection_end, True)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for selection"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            # Get position relative to this widget
            self.selection_end = event.pos()
            # Update the overlay
            if hasattr(self, 'selection_overlay'):
                self.selection_overlay.set_selection(self.selection_start, self.selection_end, False)
            # Emit selection signal
            if self.selection_start and self.selection_end:
                self.selection_completed.emit(self.selection_start, self.selection_end)
    

    
    def force_update(self):
        """Force update of the PDF viewer"""
        self.update()
        if hasattr(self, 'pdf_label'):
            self.pdf_label.update()
    
    def clear_selection_on_scroll(self):
        """Clear selection when scrolling"""
        if hasattr(self, 'selection_overlay'):
            self.selection_overlay.set_selection(None, None, False)
        # Reset selection state
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
    
    # Signal for selection completion
    selection_completed = Signal(object, object)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.renderer = PDFRenderer()
        self.session_notes = []
        self.suggested_questions = []
        
        # Initialize flags to prevent recursive changes
        self._font_size_changing = False
        self._question_selection_changing = False
        
        # API configuration
        self.api_keys = load_secrets()
        self.available_apis = get_available_apis()
        
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle(tr("window_title"))
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Toolbar (fixed height)
        toolbar_widget = self.setup_toolbar()
        toolbar_widget.setFixedHeight(50)
        main_layout.addWidget(toolbar_widget)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # PDF viewer
        self.pdf_viewer = PDFViewer(self.renderer)
        content_splitter.addWidget(self.pdf_viewer)
        
        # Control panel
        self.setup_control_panel(content_splitter)
        
        # Set splitter proportions
        content_splitter.setSizes([800, 400])
    
    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(5)
        
        # File operations
        self.open_btn = QPushButton(tr("open_pdf"))
        self.open_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.open_btn)
        
        # Navigation
        self.prev_btn = QPushButton(tr("previous"))
        self.next_btn = QPushButton(tr("next"))
        self.page_label = QLabel(f"{tr('page')}: 0 / 0")
        self.prev_btn.setFixedHeight(30)
        self.next_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.prev_btn)
        toolbar_layout.addWidget(self.page_label)
        toolbar_layout.addWidget(self.next_btn)
        
        # Page input
        toolbar_layout.addWidget(QLabel(tr("go_to") + ":"))
        self.page_input = QLineEdit()
        self.page_input.setMaximumWidth(60)
        self.page_input.setFixedHeight(30)
        toolbar_layout.addWidget(self.page_input)
        self.go_btn = QPushButton(tr("go"))
        self.go_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.go_btn)
        
        toolbar_layout.addStretch()
        
        # Zoom controls
        toolbar_layout.addWidget(QLabel(tr("zoom") + ":"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems([tr("small_10pt"), tr("medium_12pt"), tr("large_14pt"), tr("extra_large_20pt"), "Fit", "125%", "150%", "200%", "300%", "400%"])
        self.zoom_combo.setCurrentText("Fit")
        self.zoom_combo.setMaximumWidth(80)
        self.zoom_combo.setFixedHeight(30)
        toolbar_layout.addWidget(self.zoom_combo)
        
        self.zoom_in_btn = QPushButton(tr("zoom_in"))
        self.zoom_out_btn = QPushButton(tr("zoom_out"))
        self.zoom_in_btn.setFixedHeight(30)
        self.zoom_out_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.zoom_in_btn)
        toolbar_layout.addWidget(self.zoom_out_btn)
        
        # Panel controls
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(QLabel(tr("panel") + ":"))
        self.wider_btn = QPushButton(tr("wider_pdf"))
        self.narrower_btn = QPushButton(tr("narrower_pdf"))
        self.wider_btn.setFixedHeight(30)
        self.narrower_btn.setFixedHeight(30)
        toolbar_layout.addWidget(self.wider_btn)
        toolbar_layout.addWidget(self.narrower_btn)
        
        return toolbar
    
    def setup_control_panel(self, splitter):
        """Setup the right control panel"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        
        # API Key Configuration
        api_section = QLabel(tr("api_configuration"))
        api_section.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(api_section)
        
        # API Key input
        api_layout = QHBoxLayout()
        api_layout.addWidget(QLabel(tr("perplexity_api_key") + ":"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)  # Hide the key
        self.api_key_input.setPlaceholderText(tr("enter_api_key"))
        api_layout.addWidget(self.api_key_input)
        
        # Load existing key if available
        if self.api_keys.get('perplexity_api_key'):
            self.api_key_input.setText(self.api_keys['perplexity_api_key'])
        
        # Save button
        self.save_api_key_btn = QPushButton(tr("save_key"))
        self.save_api_key_btn.setFixedWidth(60)
        api_layout.addWidget(self.save_api_key_btn)
        control_layout.addLayout(api_layout)
        
        # API status
        self.api_status_label = QLabel(tr("api_key_missing"))
        self.api_status_label.setStyleSheet("color: red;")
        control_layout.addWidget(self.api_status_label)
        
        # Update API status
        self.update_api_status()
        
        # Instructions
        instructions = QLabel(tr("instructions"))
        instructions.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(instructions)
        
        instruction_text = QLabel(
            tr("instructions_text")
        )
        instruction_text.setWordWrap(True)
        control_layout.addWidget(instruction_text)
        
        # Status
        self.status_label = QLabel(tr("no_selection"))
        self.status_label.setStyleSheet("color: gray;")
        control_layout.addWidget(self.status_label)
        
        # Selection controls
        selection_layout = QHBoxLayout()
        self.clear_selection_btn = QPushButton(tr("clear_selection"))
        self.extract_text_btn = QPushButton(tr("extract_text"))
        selection_layout.addWidget(self.clear_selection_btn)
        selection_layout.addWidget(self.extract_text_btn)
        control_layout.addLayout(selection_layout)
        
        # Extracted text
        control_layout.addWidget(QLabel(tr("extracted_text") + ":"))
        self.extracted_text = QTextEdit()
        self.extracted_text.setMaximumHeight(100)
        control_layout.addWidget(self.extracted_text)
        
        # Question input
        control_layout.addWidget(QLabel(tr("ask_question") + ":"))
        self.question_input = QLineEdit()
        control_layout.addWidget(self.question_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ask_btn = QPushButton(tr("ask_question_btn"))
        self.generate_questions_btn = QPushButton(tr("generate_questions_btn"))
        button_layout.addWidget(self.ask_btn)
        button_layout.addWidget(self.generate_questions_btn)
        control_layout.addLayout(button_layout)
        
        # Suggested questions
        control_layout.addWidget(QLabel(tr("suggested_questions") + ":"))
        self.suggested_questions_combo = QComboBox()
        control_layout.addWidget(self.suggested_questions_combo)
        
        # Font size
        control_layout.addWidget(QLabel(tr("font_size") + ":"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([
            tr("small_10pt"),
            tr("medium_12pt"),
            tr("large_14pt"),
            tr("extra_large_20pt")
        ])
        self.font_size_combo.setCurrentText(tr("medium_12pt"))
        self.font_size_combo.setEditable(False)  # Prevent editing to avoid instability
        control_layout.addWidget(self.font_size_combo)
        
        # Answer length
        control_layout.addWidget(QLabel(tr("answer_length") + ":"))
        self.answer_length_combo = QComboBox()
        self.answer_length_combo.addItems([
            tr("short_tokens"),
            tr("medium_tokens"),
            tr("long_tokens"),
            tr("comprehensive_tokens")
        ])
        self.answer_length_combo.setCurrentText(tr("medium_tokens"))
        control_layout.addWidget(self.answer_length_combo)
        
        # Context window
        control_layout.addWidget(QLabel(tr("context_window") + ":"))
        self.context_window_combo = QComboBox()
        self.context_window_combo.addItems([
            tr("context_0"),
            tr("context_1"), 
            tr("context_2"),
            tr("context_5")
        ])
        self.context_window_combo.setCurrentText(tr("context_0"))
        control_layout.addWidget(self.context_window_combo)
        
        # Response
        control_layout.addWidget(QLabel(tr("llm_response") + ":"))
        self.response_text = QTextEdit()
        control_layout.addWidget(self.response_text)
        
        splitter.addWidget(control_widget)
    
    def setup_connections(self):
        """Setup signal connections"""
        # File operations
        self.open_btn.clicked.connect(self.open_pdf)
        
        # Navigation
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.go_btn.clicked.connect(self.go_to_page)
        
        # Zoom controls
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_change)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        
        # Font size control
        self.font_size_combo.currentTextChanged.connect(self.on_font_size_change)
        
        # Question selection control
        self.suggested_questions_combo.currentTextChanged.connect(self.on_question_selection_change)
        
        # Panel controls
        self.wider_btn.clicked.connect(self.widen_panel)
        self.narrower_btn.clicked.connect(self.narrow_panel)
        
        # Selection
        self.pdf_viewer.selection_completed.connect(self.on_selection_completed)
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        self.extract_text_btn.clicked.connect(self.extract_selected_text)
        
        # API key management
        self.save_api_key_btn.clicked.connect(self.save_api_key)
        
        # LLM operations
        self.ask_btn.clicked.connect(self.ask_question)
        self.generate_questions_btn.clicked.connect(self.generate_questions)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Zoom shortcuts
        self.zoom_in_btn.setShortcut("Ctrl++")
        self.zoom_out_btn.setShortcut("Ctrl+-")
        
        # Panel shortcuts
        self.wider_btn.setShortcut("Ctrl+Right")
        self.narrower_btn.setShortcut("Ctrl+Left")
    
    def update_api_status(self):
        """Update the API status label"""
        api_key = self.api_keys.get('perplexity_api_key')
        if api_key and len(api_key) > 10:  # Basic validation
            self.api_status_label.setText(tr("api_key_configured"))
            self.api_status_label.setStyleSheet("color: green;")
        else:
            self.api_status_label.setText(tr("api_key_missing"))
            self.api_status_label.setStyleSheet("color: red;")
    
    def save_api_key(self):
        """Save the API key from the input field"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, tr("error"), tr("please_enter_api_key"))
            return
        
        if len(api_key) < 10:
            QMessageBox.warning(self, tr("error"), tr("api_key_too_short"))
            return
        
        try:
            # Update the API keys dictionary
            self.api_keys['perplexity_api_key'] = api_key
            
            # Save to secrets.json file
            import json
            secrets_path = os.path.join(os.path.dirname(__file__), '..', 'secrets.json')
            
            # Create the secrets.json file if it doesn't exist
            with open(secrets_path, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
            
            # Update the status
            self.update_api_status()
            
            QMessageBox.information(self, tr("success"), tr("api_key_saved"))
            
        except Exception as e:
            QMessageBox.critical(self, tr("error"), tr("failed_to_save_api_key") + str(e))
    
    def get_api_key(self):
        """Get the current API key, checking both the input field and saved keys"""
        # First check the input field (in case user just entered it)
        input_key = self.api_key_input.text().strip()
        if input_key and len(input_key) > 10:
            return input_key
        
        # Then check the saved API keys
        return self.api_keys.get('perplexity_api_key')
    
    def open_pdf(self):
        """Open PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("open_pdf_dialog"), "", tr("pdf_files") + " (*.pdf)"
        )
        if file_path:
            try:
                num_pages = self.renderer.load_pdf(file_path)
                if num_pages > 0:
                    self.update_page_label()
                    self.render_current_page()
                    self.status_label.setText(tr("opened_pdf") + os.path.basename(file_path) + f" ({num_pages} " + tr("pages") + ")")
                else:
                    QMessageBox.warning(self, tr("error"), tr("failed_to_open_pdf"))
            except Exception as e:
                QMessageBox.critical(self, tr("error"), tr("failed_to_open_pdf") + str(e))
    
    def render_current_page(self):
        """Render the current page"""
        if hasattr(self, 'pdf_viewer'):
            canvas_width = self.pdf_viewer.width()
            canvas_height = self.pdf_viewer.height()
            self.renderer.render_page(self.renderer.current_page, canvas_width, canvas_height)
    
    def update_page_label(self):
        """Update page label"""
        if self.renderer.pdf_doc:
            self.page_label.setText(f"{tr('page')}: {self.renderer.current_page + 1} / {len(self.renderer.pdf_doc)}")
        else:
            self.page_label.setText(f"{tr('page')}: 0 / 0")
    
    def prev_page(self):
        """Go to previous page"""
        if self.renderer.pdf_doc and self.renderer.current_page > 0:
            self.renderer.current_page -= 1
            self.render_current_page()
            self.update_page_label()
            # Clear selection when changing pages
            self.clear_selection()
    
    def next_page(self):
        """Go to next page"""
        if self.renderer.pdf_doc and self.renderer.current_page < len(self.renderer.pdf_doc) - 1:
            self.renderer.current_page += 1
            self.render_current_page()
            self.update_page_label()
            # Clear selection when changing pages
            self.clear_selection()
    
    def go_to_page(self):
        """Go to specific page"""
        try:
            page_num = int(self.page_input.text()) - 1
            if self.renderer.pdf_doc and 0 <= page_num < len(self.renderer.pdf_doc):
                self.renderer.current_page = page_num
                self.render_current_page()
                self.update_page_label()
                self.page_input.clear()
                # Clear selection when changing pages
                self.clear_selection()
            else:
                QMessageBox.warning(self, tr("invalid_page"), tr("page_number_out_of_range"))
        except ValueError:
            QMessageBox.warning(self, tr("invalid_input"), tr("please_enter_valid_page_number"))
    
    def on_zoom_change(self, zoom_text: str):
        """Handle zoom dropdown change"""
        if zoom_text == "Fit":
            self.renderer.reset_zoom()
        elif zoom_text and '%' in zoom_text:
            try:
                zoom_percent = int(zoom_text.replace('%', ''))
                zoom_level = zoom_percent / 100.0
                self.renderer.set_zoom(zoom_level)
            except ValueError:
                return
        
        self.render_current_page()
        self.update_zoom_status()
        # Clear selection when zooming since coordinates change
        self.clear_selection()
    
    def zoom_in(self):
        """Zoom in"""
        self.renderer.zoom_in()
        self.update_zoom_display()
        self.render_current_page()
        self.update_zoom_status()
        # Clear selection when zooming since coordinates change
        self.clear_selection()
    
    def zoom_out(self):
        """Zoom out"""
        self.renderer.zoom_out()
        self.update_zoom_display()
        self.render_current_page()
        self.update_zoom_status()
        # Clear selection when zooming since coordinates change
        self.clear_selection()
    
    def update_zoom_display(self):
        """Update zoom dropdown display"""
        zoom_percent = self.renderer.get_zoom_percentage()
        zoom_text = f"{zoom_percent}%"
        
        # Update combo box if value exists, otherwise add it
        if zoom_text in [self.zoom_combo.itemText(i) for i in range(self.zoom_combo.count())]:
            self.zoom_combo.setCurrentText(zoom_text)
        else:
            self.zoom_combo.addItem(zoom_text)
            self.zoom_combo.setCurrentText(zoom_text)
    
    def update_zoom_status(self):
        """Update zoom status"""
        if self.renderer.zoom_level == 1.0:
            self.status_label.setText(tr("zoom_fit_to_panel"))
        else:
            zoom_percent = self.renderer.get_zoom_percentage()
            self.status_label.setText(f"{tr('zoom')}: {zoom_percent}%")
    
    def on_font_size_change(self, font_size_text):
        """Handle font size dropdown selection"""
        # Prevent recursive changes
        if self._font_size_changing:
            return
        
        self._font_size_changing = True
        
        try:
            # Extract font size from text (e.g., "Medium (12pt)" -> 12)
            if tr("small_10pt") in font_size_text:
                font_size = 10
            elif tr("medium_12pt") in font_size_text:
                font_size = 12
            elif tr("extra_large_20pt") in font_size_text:
                font_size = 20
            elif tr("large_14pt") in font_size_text:
                font_size = 14
            else:
                font_size = 12  # Default
            
            # Apply font size to text areas
            font = QFont("Arial", font_size)
            self.extracted_text.setFont(font)
            self.response_text.setFont(font)
            
            # Update status
            self.status_label.setText(tr("font_size_changed") + str(font_size) + tr("pt"))
        except Exception as e:
            print(f"Error changing font size: {e}")
        finally:
            self._font_size_changing = False
    
    def on_question_selection_change(self, selected_question):
        """Handle question selection dropdown change"""
        # Prevent automatic changes from programmatic updates
        if self._question_selection_changing:
            return
        
        # Only update status if there's actually a selection
        if selected_question:
            self.status_label.setText(tr("selected_question") + selected_question)
    
    def widen_panel(self):
        """Make PDF panel wider"""
        splitter = self.findChild(QSplitter)
        if splitter:
            sizes = splitter.sizes()
            new_width = min(sizes[0] + 50, splitter.width() - 300)
            splitter.setSizes([new_width, splitter.width() - new_width])
    
    def narrow_panel(self):
        """Make PDF panel narrower"""
        splitter = self.findChild(QSplitter)
        if splitter:
            sizes = splitter.sizes()
            new_width = max(sizes[0] - 50, 200)
            splitter.setSizes([new_width, splitter.width() - new_width])
    
    def on_selection_completed(self, start_pos, end_pos):
        """Handle text selection completion"""
        self.status_label.setText(tr("selection_completed") + tr("click_extract_text_to_get_content"))
        # Store selection coordinates for text extraction
        self.selection_start = start_pos
        self.selection_end = end_pos
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selection_start = None
        self.selection_end = None
        self.extracted_text.clear()
        self.status_label.setText(tr("selection_cleared"))
        
        # Clear visual selection by clearing the overlay
        if hasattr(self, 'pdf_viewer') and hasattr(self.pdf_viewer, 'selection_overlay'):
            self.pdf_viewer.selection_overlay.set_selection(None, None, False)
    
    def extract_selected_text(self):
        """Extract text from the selected region using fitz"""
        if not self.selection_start or not self.selection_end:
            QMessageBox.warning(self, tr("no_selection"), tr("please_select_a_text_region_first"))
            return
        
        if not self.renderer.pdf_doc:
            QMessageBox.warning(self, tr("no_pdf"), tr("please_open_a_pdf_first"))
            return
        
        try:
            # Get context window setting
            context_window = self.context_window_combo.currentText()
            
            # Parse the context window setting
            if tr("context_0") in context_window:
                pages_around = 0
            else:
                # Extract number from "±1 page", "±2 pages", etc.
                pages_around = int(context_window.split('±')[1].split()[0])
            
            # Get the current page
            current_page_num = self.renderer.current_page
            total_pages = len(self.renderer.pdf_doc)
            
            # Calculate page range based on context window
            start_page = max(0, current_page_num - pages_around)
            end_page = min(total_pages - 1, current_page_num + pages_around)
            
            extracted_text_parts = []
            
            for page_num in range(start_page, end_page + 1):
                page = self.renderer.pdf_doc[page_num]
                
                if page_num == current_page_num:
                    # For the current page, extract from selected region
                    # Convert screen coordinates to PDF coordinates
                    scale_factor = self.renderer.fit_to_panel_zoom * self.renderer.zoom_level
                    
                    # Get scroll area offsets
                    scroll_x = self.pdf_viewer.scroll_area.horizontalScrollBar().value()
                    scroll_y = self.pdf_viewer.scroll_area.verticalScrollBar().value()
                    
                    # Convert screen coordinates to PDF coordinates
                    pdf_x1 = (min(self.selection_start.x(), self.selection_end.x()) + scroll_x) / scale_factor
                    pdf_y1 = (min(self.selection_start.y(), self.selection_end.y()) + scroll_y) / scale_factor
                    pdf_x2 = (max(self.selection_start.x(), self.selection_end.x()) + scroll_x) / scale_factor
                    pdf_y2 = (max(self.selection_start.y(), self.selection_end.y()) + scroll_y) / scale_factor
                    
                    # Create a rectangle for text extraction
                    rect = fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
                    
                    # Extract text from the selected region
                    page_text = page.get_text("text", clip=rect)
                    
                    if page_text.strip():
                        extracted_text_parts.append(page_text.strip())
                else:
                    # For other pages, extract all text
                    page_text = page.get_text("text")
                    if page_text.strip():
                        extracted_text_parts.append(page_text.strip())
            
            # Combine all extracted text
            if extracted_text_parts:
                full_text = "\n\n".join(extracted_text_parts)
                self.extracted_text.setText(full_text)
                self.status_label.setText(tr("text_extracted") + str(len(extracted_text_parts)) + tr("page(s)") + ": " + str(len(full_text)) + tr("characters"))
            else:
                self.extracted_text.setText(tr("no_text_found_in_selection"))
                self.status_label.setText(tr("no_text_found_in_selection"))
                
        except Exception as e:
            self.extracted_text.setText(tr("error_extracting_text") + str(e))
            self.status_label.setText(tr("error_during_text_extraction"))
            print(f"Text extraction error: {e}")
    
    def ask_question(self):
        """Ask a question about the selected text - handles both manual input and selected questions"""
        # Check if there's a question in the input field
        question = self.question_input.text().strip()
        
        # If no question in input, check if there's a selected question from dropdown
        if not question:
            selected_question = self.suggested_questions_combo.currentText()
            if selected_question:
                question = selected_question
            else:
                QMessageBox.warning(self, tr("no_question"), tr("please_enter_a_question_or_select_from_dropdown"))
                return
        
        extracted_text = self.extracted_text.toPlainText().strip()
        if not extracted_text:
            QMessageBox.warning(self, tr("no_text"), tr("please_extract_some_text_first"))
            return
        
        try:
            # Check if API key is available
            api_key = self.get_api_key()
            if not api_key:
                self.response_text.setText(tr("error_api_key_not_configured"))
                self.status_label.setText(tr("api_key_missing"))
                return
            
            # Get language (user selection or auto-detection)
            selected_language = self.get_selected_language()
            if selected_language:
                detected_language = selected_language
            else:
                detected_language = self.detect_language(extracted_text)
            language_instruction = self.get_language_instruction(detected_language)
            
            # Prepare the prompt for the LLM
            prompt = f"""{tr('based_on_text_prompt')}

{tr('text')}: {extracted_text}

{tr('question')}: {question}

{language_instruction}

{tr('please_provide_clear_and_accurate_answer_based_only_on_information_in_text_above')}"""

            # Get answer length preference and choose appropriate model
            answer_length = self.answer_length_combo.currentText()
            
            # Choose model based on answer length
            if tr("short_tokens") in answer_length or tr("medium_tokens") in answer_length:
                model = "sonar"  # Faster for shorter answers
            else:
                model = "sonar-reasoning"  # Better reasoning for longer answers
            
            # Call the LLM
            response = send_prompt_to_perplexity(prompt, api_key, model=model)
            
            if response:
                # Clean up response - remove <think> tags if present
                cleaned_response = self.clean_llm_response(response)
                self.response_text.setText(cleaned_response)
                self.status_label.setText(tr("question_answered").format(language=detected_language, chars=len(cleaned_response)))
            else:
                self.response_text.setText(tr("error_could_not_get_response_from_llm") + tr("please_check_your_api_key"))
                self.status_label.setText(tr("llm_error"))
                
        except Exception as e:
            self.response_text.setText(tr("error") + str(e))
            self.status_label.setText(tr("error_occurred"))
            print(f"LLM error: {e}")
    
    def generate_questions(self):
        """Generate suggested questions"""
        extracted_text = self.extracted_text.toPlainText().strip()
        if not extracted_text:
            QMessageBox.warning(self, tr("no_text"), tr("please_extract_some_text_first"))
            return
        
        try:
            # Check if API key is available
            api_key = self.get_api_key()
            if not api_key:
                QMessageBox.warning(self, tr("error"), tr("perplexity_api_key_not_configured") + tr("please_enter_your_api_key_in_the_configuration_section"))
                self.status_label.setText(tr("api_key_missing"))
                return
            
            # Get language (user selection or auto-detection)
            selected_language = self.get_selected_language()
            if selected_language:
                detected_language = selected_language
            else:
                detected_language = self.detect_language(extracted_text)
            language_instruction = self.get_language_instruction(detected_language)
            
            # Prepare the prompt for question generation
            prompt = f"""{tr('based_on_text_generate_questions')}
{tr('make_questions_diverse_and_interesting')}
{tr('cover_different_aspects_of_the_text')}

{tr('text')}: {extracted_text}

{language_instruction}

{tr('instructions')}:
{tr('generate_exactly_5_questions')}
{tr('each_question_should_be_on_its_own_line')}
{tr('do_not_use_numbering')}
{tr('do_not_use_bullet_points')}
{tr('make_questions_clear_and_specific')}
{tr('questions')}:"""

            # Call the LLM - use sonar for question generation (faster and cleaner)
            response = send_prompt_to_perplexity(prompt, api_key, model="sonar")
            
            if response:
                # Parse the response to extract questions
                # Clean up the response and split by lines
                lines = response.strip().split('\n')
                questions = []
                
                for line in lines:
                    line = line.strip()
                    # Skip empty lines and common prefixes
                    if line and not line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                        # Remove any numbering at the start
                        if line[0].isdigit() and '. ' in line:
                            line = line.split('. ', 1)[1]
                        questions.append(line)
                
                # Limit to 5 questions and filter out duplicates
                unique_questions = []
                seen = set()
                for q in questions[:5]:
                    if q and q not in seen:
                        unique_questions.append(q)
                        seen.add(q)
                
                # Update the suggested questions dropdown
                self._question_selection_changing = True
                self.suggested_questions_combo.clear()
                if unique_questions:
                    self.suggested_questions_combo.addItems(unique_questions)
                    self.status_label.setText(tr("generated_questions").format(count=len(unique_questions), language=detected_language))
                else:
                    self.status_label.setText(tr("no_valid_questions_generated"))
                self._question_selection_changing = False
            else:
                QMessageBox.warning(self, tr("error"), tr("could_not_generate_questions") + tr("please_check_your_api_key"))
                self.status_label.setText(tr("question_generation_failed"))
                
        except Exception as e:
            QMessageBox.warning(self, tr("error"), tr("error_generating_questions") + str(e))
            self.status_label.setText(tr("error_occurred"))
            print(f"Question generation error: {e}")
    
    def detect_language(self, text):
        """Simple language detection based on character sets"""
        if not text:
            return "English"
        
        # Count characters from different scripts
        import re
        
        # Chinese characters (simplified and traditional)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # Japanese characters (hiragana, katakana, kanji)
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', text))
        
        # Korean characters
        korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
        
        # Arabic characters
        arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
        
        # Cyrillic characters (Russian, etc.)
        cyrillic_chars = len(re.findall(r'[\u0400-\u04ff]', text))
        
        # Thai characters
        thai_chars = len(re.findall(r'[\u0e00-\u0e7f]', text))
        
        # Hindi/Devanagari characters
        devanagari_chars = len(re.findall(r'[\u0900-\u097f]', text))
        
        # Count total non-ASCII characters
        total_non_ascii = len(re.findall(r'[^\x00-\x7f]', text))
        
        # Determine language based on character counts
        if chinese_chars > 10:
            # Try to distinguish between Simplified and Traditional Chinese
            # This is a simple heuristic - Traditional Chinese has more complex characters
            traditional_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            # For now, we'll use "Chinese" for both, but you could add more sophisticated detection
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
            return "Non-English"  # Generic for other languages
        else:
            return "English"
    
    def get_selected_language(self):
        """Get the language selected by the user from the initial dialog"""
        global CURRENT_LANGUAGE
        # If user selected a specific language, use it
        if CURRENT_LANGUAGE in ["English", "Chinese", "Traditional Chinese", "Japanese"]:
            return CURRENT_LANGUAGE
        # Otherwise, use auto-detection
        return None
    
    def get_language_instruction(self, language):
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
    
    def clean_llm_response(self, response):
        """Clean up LLM response by removing <think> tags and other formatting"""
        if not response:
            return response
        
        # Remove <think> tags and their content
        import re
        # Remove <think>...</think> blocks
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        # Remove any remaining <think> tags
        response = re.sub(r'<think>', '', response)
        response = re.sub(r'</think>', '', response)
        
        # Clean up extra whitespace
        response = re.sub(r'\n\s*\n', '\n\n', response)
        response = response.strip()
        
        return response
    
def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Show language selection dialog first
    language_dialog = LanguageSelectionDialog()
    language_dialog.show()
    
    # Wait for the dialog to close
    app.exec()
    
    # Create and show main window with selected language
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
