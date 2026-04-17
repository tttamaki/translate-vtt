# VTT Translation Tool

A Python utility for translating Japanese WebVTT (`.vtt`) subtitle files into English while preserving the original subtitle structure.

## Features

- **Preserves VTT structure**
  Maintains block formatting, timestamps, and cue identifiers.

- **Selective translation**
  Only lines containing Japanese text are translated. Non-Japanese lines remain unchanged.

- **Context-aware merging**
  Consecutive Japanese lines are grouped and translated together, which may result in:
  - Multiple Japanese lines → Single English line

- **Automatic output naming**
  Generates output files with `_en` suffix:

  ```text
  sample.vtt → sample_en.vtt
  ```

- **Progress visualization**
  Displays a real-time progress bar using `tqdm`.

---

## Requirements

- Python 3.x
- [`deep-translator`](https://pypi.org/project/deep-translator/)
- [`tqdm`](https://pypi.org/project/tqdm/)
- `pytest`

## 🚀 Installation

Activate your virtual environment and install dependencies:

```bash
source .venv/bin/activate
pip install deep-translator tqdm pytest
```

---

## Usage

### Running the translation

Navigate to the `src` directory and run the script with a `.vtt` file as input:

```bash
python src/translate_vtt.py <input_file.vtt>
```

Or run from the project root:

```bash
python src/translate_vtt.py <input_file.vtt>
```

### Example

```bash
python src/translate_vtt.py ../example.vtt
```

---

## Test

Run the test suite using pytest:

```bash
# From project root
python -m pytest test/test_vtt_translator.py -v

# Run with coverage
python -m pytest test/test_vtt_translator.py --cov --cov-report=html
```

---

## Project Structure

```text
translate-vtt/
├── src/
│   ├── __init__.py
│   ├── translate_vtt.py      # Main script
│   └── vtt_translator.py     # VTTTranslator class
├── test/
│   └── test_vtt_translator.py # Pytest test suite
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

## Output

- A translated `.vtt` file will be generated in the same directory.

- File naming convention:

  ```text
  <original_filename>_en.vtt
  ```

- Upon completion:
  - Number of translated lines is displayed
  - Output file path is shown

---

## Notes

- **Internet connection required**
  The tool relies on external translation services via `deep-translator`.

- **Translation quality**
  This tool uses automated translation:
  - Technical terms may require manual review
  - Informal or spoken language may not translate perfectly

---

## Example Workflow

```bash
# Activate environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -v

# Run translation
python src/translate_vtt.py example.vtt

# 6. Output file will be generated as example_en.vtt
```

---

## License

MIT License
