# repo2md

`repo2md` walks a repository, gathers whitelisted files, and concatenates them into a single Markdown artifact with a TOC and one tab-indented section per file. The resulting document is saved inside the source repo as `repo2md-<timestamp>-<hash>.md`.

## Requirements

- Python 3.9+
- Dependencies from `requirements.txt` (install with `pip install -r requirements.txt`)

## Usage

```
python main.py REPO_PATH
```

Key options:

- `--only-docs`: restricts the output to `.md` and `.txt` files only. This is useful when you only want documentation artifacts and not source files. The flag can be combined with any repo path, e.g. `python main.py ../my-repo --only-docs`.

Without the flag the default whitelist includes `.md`, `.py`, `.c`, `.h`, and `.cpp` files.

The command ignores hidden directories/files, empty files, and previous `repo2md` output files.
