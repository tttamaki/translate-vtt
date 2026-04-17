import re
from deep_translator import GoogleTranslator  # type: ignore[import-untyped]
from tqdm import tqdm


class VTTTranslator:
    """VTTファイルの翻訳を行うクラス"""

    def __init__(self) -> None:
        """翻訳エンジンと日本語判定パターンを初期化"""
        self.jp_re = re.compile(
            r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
        self.translator = GoogleTranslator(source='ja', target='en')
        self.translated_count = 0

    def translate_buffer(self, buffer: list[str]) -> str:
        """テキストバッファの翻訳処理

        Args:
            buffer: 翻訳するテキストのリスト

        Returns:
            翻訳されたテキスト
        """
        src = ' '.join(line.strip() for line in buffer if line.strip())
        if not src:
            return ''

        try:
            return self.translator.translate(src)  # type: ignore[no-any-return]
        except Exception:  # pylint: disable=broad-exception-caught
            # one immediate retry without delay
            return self.translator.translate(src)  # type: ignore[no-any-return]

    def flush_buffer(self, buffer: list[str]) -> str:
        """バッファ内の日本語行を翻訳し、翻訳行数を更新

        Args:
            buffer: 翻訳するテキストのバッファ

        Returns:
            翻訳された文字列
        """
        if not buffer:
            return ''

        translated = self.translate_buffer(buffer)
        self.translated_count += len(buffer)
        buffer.clear()
        return translated

    def translate(self, text: str) -> list[str]:
        """テキストを行単位で処理し、日本語部分を翻訳

        Args:
            text: 翻訳するテキスト

        Returns:
            翻訳結果のリスト
        """
        lines = text.splitlines()

        # 行処理用の初期化
        out: list[str] = []
        japanese_buffer: list[str] = []

        # 各行を処理：日本語行をバッファに集め、非日本語行はそのまま出力
        for line in tqdm(lines, desc='Translating', unit='line'):
            if self.jp_re.search(line):
                japanese_buffer.append(line)
            else:
                out.append(self.flush_buffer(japanese_buffer))
                out.append(line)

        out.append(self.flush_buffer(japanese_buffer))

        return out
