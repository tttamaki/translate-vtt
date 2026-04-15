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

---

## 🚀 Installation

Activate your virtual environment and install dependencies:

```bash
source .venv/bin/activate
pip install deep-translator tqdm
```

---

## Usage

Run the script with a `.vtt` file as input:

```bash
python translate_vtt.py <input_file.vtt>
```

### Example

```bash
python translate_vtt.py example.vtt"
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
pip install deep-translator tqdm

# Run translation
python translate_vtt.py sample.vtt
```

---

## License

MIT License
