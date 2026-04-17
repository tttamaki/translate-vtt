import argparse
from pathlib import Path
from vtt_translator import VTTTranslator


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=Path, help='Path to input Japanese VTT file')
    args = parser.parse_args()

    input_path = args.input_file
    output_path = input_path.with_name(
        f'{input_path.stem}_en{input_path.suffix}')

    text = input_path.read_text(encoding='utf-8')

    vtt_translator = VTTTranslator()
    out = vtt_translator.translate(text)

    output_path.write_text(
        '\n'.join(out) + ('\n' if text.endswith('\n') else ''),
        encoding='utf-8',
    )

    print(f'translated_lines={vtt_translator.translated_count}')
    print(f'output_file={output_path}')


if __name__ == '__main__':
    main()
