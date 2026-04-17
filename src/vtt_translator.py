import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from deep_translator import GoogleTranslator  # type: ignore[import-untyped]
from tqdm import tqdm


class VTTTranslator:
    """VTTファイルの翻訳を行うクラス"""

    def __init__(self, retries: int = 3, max_workers: int = 4) -> None:
        """翻訳エンジンと日本語判定パターンを初期化"""
        self.jp_re = re.compile(
            r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
        self.translator = GoogleTranslator(source='ja', target='en')
        self.translated_count = 0
        self.retries = retries
        self.max_workers = max_workers
        self._count_lock = threading.Lock()
        self._translator_local = threading.local()

    def _create_translator(self) -> GoogleTranslator:
        """新しい翻訳器インスタンスを生成する"""
        return GoogleTranslator(source='ja', target='en')

    def _get_thread_translator(self) -> GoogleTranslator:
        """スレッドごとの翻訳器を取得する"""
        translator = getattr(self._translator_local, 'translator', None)
        if translator is None:
            translator = self._create_translator()
            self._translator_local.translator = translator
        return translator

    def translate_buffer(
        self,
        buffer: list[str],
        translator: GoogleTranslator | None = None,
    ) -> str:
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
        active_translator = translator or self.translator
        for attempt in range(retries):
            try:
                result: str = active_translator.translate(src)
                with self._count_lock:
                    self.translated_count += 1
                return result
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if attempt == retries - 1:
                    raise RuntimeError(
                        f'Failed to translate text after {retries} attempts'
                    ) from exc
                sleep(1)

        return src

    def translate_line(self, line: str) -> str:
        """1行分の翻訳をスレッド専用翻訳器で実行する"""
        return self.translate_buffer([line], translator=self._get_thread_translator())

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

        # 翻訳対象行だけを抽出して並列翻訳
        translate_jobs = [
            (idx, line)
            for idx, (line, should_translate) in enumerate(line_entries)
            if should_translate
        ]
        translate_target_count = len(translate_jobs)

        translated_lines = [line for line, _ in line_entries]
        with tqdm(total=translate_target_count, desc='Translating', unit='line') as progress:
            if translate_target_count > 0:
                worker_count = min(self.max_workers, translate_target_count)
                if worker_count == 1:
                    for idx, line in translate_jobs:
                        translated_lines[idx] = self.translate_buffer([line])
                        progress.update(1)
                else:
                    with ThreadPoolExecutor(max_workers=worker_count) as executor:
                        future_to_idx = {
                            executor.submit(self.translate_line, line): idx
                            for idx, line in translate_jobs
                        }
                        for future in as_completed(future_to_idx):
                            idx = future_to_idx[future]
                            translated_lines[idx] = future.result()
                            progress.update(1)

        translated_text = '\n'.join(translated_lines) + ('\n' if text.endswith('\n') else '')
        return translated_text
