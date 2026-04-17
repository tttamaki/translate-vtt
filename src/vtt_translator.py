import re
from time import sleep
from deep_translator import GoogleTranslator  # type: ignore[import-untyped]
from tqdm import tqdm


class VTTTranslator:
    """VTTファイルの翻訳を行うクラス"""

    def __init__(self, retries: int = 3) -> None:
        """翻訳エンジンと日本語判定パターンを初期化"""
        self.jp_re = re.compile(
            r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
        self.translator = GoogleTranslator(source='ja', target='en')
        self.translated_count = 0
        self.retries = retries

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

        retries = self.retries
        for attempt in range(retries):
            try:
                result: str = self.translator.translate(src)
                self.translated_count += 1
                return result
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if attempt == retries - 1:
                    raise RuntimeError(
                        f'Failed to translate text after {retries} attempts'
                    ) from exc
                sleep(1)

        return src

    def flush_japanese_buffer(self, japanese_buffer: list[str]) -> tuple[str, bool] | None:
        """日本語バッファを1行にまとめて翻訳対象タプルとして返す"""
        if not japanese_buffer:
            return None

        flattened = ' '.join(line.strip() for line in japanese_buffer if line.strip())
        japanese_buffer.clear()
        return flattened, True

    def translate(self, text: str) -> str:
        """テキストを行単位で処理し、日本語部分を翻訳

        Args:
            text: 翻訳するテキスト

        Returns:
            翻訳されたテキスト
        """
        lines = text.splitlines()

        # 行処理用の初期化: (line, should_translate)
        out: list[tuple[str, bool]] = []
        japanese_buffer: list[str] = []

        # 各行を処理：日本語行をバッファに集め、非日本語行はそのまま出力
        for line in tqdm(lines, desc='Translating', unit='line'):
            if self.jp_re.search(line):
                japanese_buffer.append(line)
            else:
                flushed = self.flush_japanese_buffer(japanese_buffer)
                if flushed is not None:
                    out.append(flushed)
                out.append((line, False))

        flushed = self.flush_japanese_buffer(japanese_buffer)
        if flushed is not None:
            out.append(flushed)

        if not out:
            return ''

        # 翻訳フラグが立っている行のみ翻訳
        translated_lines: list[str] = []
        for line, should_translate in out:
            if should_translate:
                translated_lines.append(self.translate_buffer([line]))
            else:
                translated_lines.append(line)

        translated_text = '\n'.join(translated_lines) + ('\n' if text.endswith('\n') else '')
        return translated_text
