from src.vtt_translator import VTTTranslator


class TestVTTTranslator:
    """VTTTranslatorクラスのテスト"""

    def setup_method(self):
        """各テストメソッド前に実行"""
        self.translator = VTTTranslator()

    def test_translator_initialization(self):
        """翻訳器の初期化をテスト"""
        assert self.translator.translated_count == 0
        assert self.translator.jp_re is not None
        assert self.translator.translator is not None

    def test_flush_buffer_empty(self):
        """空のバッファをフラッシュ"""
        result = self.translator.flush_buffer([])
        assert result == ''
        assert self.translator.translated_count == 0

    def test_flush_buffer_count_update(self):
        """バッファフラッシュ時の行数カウント更新"""
        buffer = ['これはテストです', '日本語です']
        self.translator.flush_buffer(buffer)
        assert self.translator.translated_count == 2
        assert len(buffer) == 0

    def test_translate_empty_text(self):
        """空のテキストを翻訳"""
        result = self.translator.translate('')
        assert result == ['']
        assert self.translator.translated_count == 0

    def test_translate_japanese_pattern_detection(self):
        """日本語パターン検出のテスト"""
        # 日本語を含む行
        assert self.translator.jp_re.search('これはテストです') is not None
        # 英数字のみの行
        assert self.translator.jp_re.search('This is test') is None
        # タイムコード行（VTT形式）
        assert self.translator.jp_re.search('00:00:01.000 --> 00:00:05.000') is None

    def test_translate_mixed_content(self):
        """日本語と非日本語の混合テキスト"""
        mixed_text = '''00:00:01.000 --> 00:00:05.000
これはテストです

00:00:06.000 --> 00:00:10.000
Another test'''
        result = self.translator.translate(mixed_text)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_translate_buffer_with_content(self):
        """コンテンツを含むバッファの翻訳

        注: 実際の翻訳にはインターネット接続が必要なため、
        翻訳結果の内容ではなく戻り値の型をテスト
        """
        buffer = ['テスト']
        result = self.translator.flush_buffer(buffer)
        assert isinstance(result, str)
        assert self.translator.translated_count == 1

    def test_translate_preserves_line_order(self):
        """翻訳後のテキストで行の順序が保持されることをテスト"""
        text = '''00:00:01.000 --> 00:00:05.000
テスト1

00:00:06.000 --> 00:00:10.000
テスト2'''
        result = self.translator.translate(text)
        # タイムコード行は変わらず出力されるはず
        assert '00:00:01.000 --> 00:00:05.000' in result
        assert '00:00:06.000 --> 00:00:10.000' in result

    def test_buffer_clear_after_flush(self):
        """フラッシュ後のバッファクリア"""
        buffer = ['テスト1', 'テスト2']
        self.translator.flush_buffer(buffer)
        assert len(buffer) == 0

    def test_translated_count_accumulation(self):
        """翻訳行数のカウント蓄積"""
        buffer1 = ['テスト1', 'テスト2']
        buffer2 = ['テスト3']

        self.translator.flush_buffer(buffer1)
        assert self.translator.translated_count == 2

        self.translator.flush_buffer(buffer2)
        assert self.translator.translated_count == 3
