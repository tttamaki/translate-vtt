import argparse
from pathlib import Path
from vtt_translator import VTTTranslator


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=Path, help='Path to input Japanese VTT file')
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of worker threads for parallel translation (default: 4)',
    )
    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        help='Number of retry attempts for each translation request (default: 3)',
    )
    args = parser.parse_args()

    input_path = args.input_file
    output_path = input_path.with_name(
        f'{input_path.stem}_en{input_path.suffix}')

    text = input_path.read_text(encoding='utf-8')

    vtt_translator = VTTTranslator(
        retries=args.retries,
        max_workers=args.workers,
    )
    out = vtt_translator.translate(text)

    output_path.write_text(out, encoding='utf-8')

    print(f'translated_lines={vtt_translator.translated_count}')
    print(f'output_file={output_path}')


if __name__ == '__main__':
    main()
