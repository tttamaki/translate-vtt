import argparse
from pathlib import Path
import re
from deep_translator import GoogleTranslator  # type: ignore[import-untyped]
from tqdm import tqdm


def translate_buffer(buffer: list[str], translator: GoogleTranslator) -> str:
    src = ' '.join(line.strip() for line in buffer if line.strip())
    if not src:
        return ''

    try:
        return translator.translate(src)  # type: ignore[no-any-return]
    except Exception:  # pylint: disable=broad-exception-caught
        # one immediate retry without delay
        return translator.translate(src)  # type: ignore[no-any-return]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=Path, help='Path to input Japanese VTT file')
    args = parser.parse_args()

    input_path = args.input_file
    output_path = input_path.with_name(
        f'{input_path.stem}_en{input_path.suffix}')

    text = input_path.read_text(encoding='utf-8')
    lines = text.splitlines()

    jp_re = re.compile(
        r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uff66-\uff9f]')
    translator = GoogleTranslator(source='ja', target='en')

    out = []
    translated_count = 0
    japanese_buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal translated_count
        if not japanese_buffer:
            return

        out.append(translate_buffer(japanese_buffer, translator))
        translated_count += len(japanese_buffer)
        japanese_buffer.clear()

    for line in tqdm(lines, desc='Translating', unit='line'):
        if jp_re.search(line):
            japanese_buffer.append(line)
        else:
            flush_buffer()
            out.append(line)

    flush_buffer()

    output_path.write_text(
        '\n'.join(out) + ('\n' if text.endswith('\n') else ''),
        encoding='utf-8',
    )
    print(f'translated_lines={translated_count}')
    print(f'output_file={output_path}')


if __name__ == '__main__':
    main()
