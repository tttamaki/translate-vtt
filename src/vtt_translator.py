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

    def build_line_entries(self, lines: list[str]) -> list[tuple[str, bool]]:
        """各行を走査して、翻訳対象フラグ付きの出力行を収集する"""
        line_entries: list[tuple[str, bool]] = []
        japanese_buffer: list[str] = []

        for line in lines:
            if self.jp_re.search(line):
                japanese_buffer.append(line)
            else:
                flushed = self.flush_japanese_buffer(japanese_buffer)
                if flushed is not None:
                    line_entries.append(flushed)
                line_entries.append((line, False))

        flushed = self.flush_japanese_buffer(japanese_buffer)
        if flushed is not None:
            line_entries.append(flushed)

        return line_entries

    def translate(self, text: str) -> str:
        """テキストを行単位で処理し、日本語部分を翻訳

        Args:
            text: 翻訳するテキスト

        Returns:
            翻訳されたテキスト
        """
        lines = text.splitlines()
        line_entries = self.build_line_entries(lines)

        if not line_entries:
            return ''

        # 翻訳対象数を事前計算し、翻訳進捗をその総数で表示
        translate_target_count = sum(
            1 for _, should_translate in line_entries if should_translate
        )

        # 翻訳フラグが立っている行のみ翻訳
        translated_lines: list[str] = []
        with tqdm(total=translate_target_count, desc='Translating', unit='line') as progress:
            for line, should_translate in line_entries:
                if should_translate:
                    translated_lines.append(self.translate_buffer([line]))
                    progress.update(1)
                else:
                    translated_lines.append(line)

        translated_text = '\n'.join(translated_lines) + ('\n' if text.endswith('\n') else '')
        return translated_text
