# Bulk Rename

A CLI utility for bulk renaming files based on a pattern.

[![PyPI version](https://img.shields.io/pypi/v/bulk-rename-signalsenryu.svg)](https://pypi.org/project/bulk-rename-signalsenryu)

## Installation

Install via pip:
```bash
pip install bulk-rename-signalsenryu
```

Or install via uv:
```bash
uv pip install bulk-rename-signalsenryu
```

## Usage

After installation:
```bash
bulk-rename --help
```

Or run without installing:
```bash
# Using Python module
python -m bulk_rename --help

# Using uv run (from project directory)
uv run bulk-rename --help

# Using uvx (runs directly without installation)
uvx bulk-rename-signalsenryu --help
```

### Available Options
```
-d, --path PATH        Directory containing files to rename (required)
-p, --pattern PATTERN  Naming pattern, e.g., "video_{:03d}" (required)
-e, --extension EXT    File extension to filter, e.g., "mp4" (required)
-s, --start NUM        Starting index for numbering (default: 1)
--version              Show version and exit
```

## Examples

### Basic Usage

Suppose you have a directory with video files:
```bash
ls videos/
a.mp4  b.mp4  c.mp4
```

Rename them with zero-padded numbering:
```bash
bulk-rename -d ./videos -p "video_{:03d}" -e mp4
```

Or with uvx:
```bash
uvx bulk-rename -d ./videos -p "video_{:03d}" -e mp4
```

Preview and confirm:
```
✅ videos/a.mp4 -> videos/video_001.mp4
✅ videos/b.mp4 -> videos/video_002.mp4
✅ videos/c.mp4 -> videos/video_003.mp4
Proceed? (y/n): y
```

Result:
```bash
ls videos/
backup_2026-01-20_08-48-13.txt  video_001.mp4  video_002.mp4  video_003.mp4
```

A backup file is automatically created:
```bash
cat videos/backup_2026-01-20_08-48-13.txt
videos/a.mp4 -> videos/video_001.mp4
videos/b.mp4 -> videos/video_002.mp4
videos/c.mp4 -> videos/video_003.mp4
```

### Custom Starting Index

Start numbering from 10:
```bash
bulk-rename -d ./photos -p "IMG_{:02d}" -e jpg -s 10
```

Result:
```
photos/x.jpg -> photos/IMG_10.jpg
photos/y.jpg -> photos/IMG_11.jpg
photos/z.jpg -> photos/IMG_12.jpg
```

### Handling Conflicts

If target files already exist, the tool detects conflicts:
```
❌ videos/video_001.mp4 -> videos/video_001.mp4 [Target file already exists]
Found 1 conflict
Continue with skipping conflicts? (y/n): n
```

## Features

- ✅ Preview changes before applying
- ✅ Automatic conflict detection
- ✅ Asks for confirmation before renaming
- ✅ Backup file creation with timestamps
- ✅ Alphabetical sorting of source files
- ✅ Customizable numbering patterns

## Development

### Setup

Clone the repository and install in editable mode:

**Using pip:**
```bash
git clone https://github.com/signalsenryu/bulk-rename.git
cd bulk-rename
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

**Using uv:**
```bash
git clone https://github.com/signalsenryu/bulk-rename.git
cd bulk-rename
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

Or even simpler with uv sync:
```bash
git clone https://github.com/signalsenryu/bulk-rename.git
cd bulk-rename
uv sync --extra dev
```

### Run Tests

**Using pip:**
```bash
pytest tests/ -vv -s
```

**Using uv:**
```bash
uv run pytest tests/ -vv -s
```

### Project Structure
```
bulk-rename/
├── src/
│   └── bulk_rename/
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py
├── tests/
│   └── test_renamer.py
├── pyproject.toml
└── README.md
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
