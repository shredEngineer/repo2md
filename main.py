import typer
import pathlib
import hashlib
import datetime
import re
import subprocess
from typing import List, Optional

app = typer.Typer()

WHITELIST = {'.md', '.py', '.c', '.h', '.cpp'}
REPO2MD_RE = re.compile(r'repo2md-\d{14}-[0-9a-f]{12}\.md', re.IGNORECASE)

def get_git_commit(root: pathlib.Path) -> Optional[str]:
    """Return current commit hash if root is a git repo, else None."""
    git_dir = root / ".git"
    if not git_dir.is_dir():
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            check=True,
            text=True
        )
        return result.stdout.strip()
    except Exception:
        return None

def collect_files(root: pathlib.Path) -> List[pathlib.Path]:
    files = []
    for path in sorted(root.rglob('*')):
        if any(part.startswith('.') for part in path.parts):
            continue
        if not path.is_file():
            continue
        name = path.name
        ext = path.suffix.lower()
        if ext not in WHITELIST:
            continue
        if REPO2MD_RE.fullmatch(name):
            continue
        try:
            content = path.read_text(encoding='utf-8').strip()
        except Exception:
            continue
        if not content:
            continue
        rel = path.relative_to(root)
        files.append(rel)
    # README.md always first, if present
    try:
        idx = files.index(pathlib.Path('README.md'))
        files.insert(0, files.pop(idx))
    except ValueError:
        pass
    return files

def toc(files: List[pathlib.Path]) -> str:
    lines = ["## TOC"]
    for f in files:
        anchor = f.as_posix().replace('/', '').replace('.', '').replace(' ', '-').lower()
        lines.append(f"- [{f.as_posix()}](##{anchor})")
    return '\n'.join(lines) + '\n\n'

def heading(rel_path: pathlib.Path) -> str:
    return f"## {rel_path.as_posix()}\n"

def tab_block(text: str) -> str:
    return ''.join('\t' + line + '\n' for line in text.splitlines())

@app.command()
def repo2md(repo_path: str):
    """
    Traverse repo and dump whitelisted files as a single Markdown document,
    bounded by '--', with standard header, TOC, and tab-indented file blocks.
    Empty files and previous repo2md output files are skipped.
    """
    root = pathlib.Path(repo_path).resolve()
    repo_name = root.name
    git_commit = get_git_commit(root)
    files = collect_files(root)
    if not files:
        typer.echo("No files to include.")
        raise typer.Exit(1)
    doc = [
        "--\n\n",
        "# Repository Dump\n",
        f"- Folder: `{repo_name}`\n"
    ]
    if git_commit:
        doc.append(f"- Git commit: `{git_commit}`\n")
    doc.append('\n')
    doc.append(toc(files))
    for f in files:
        absf = root / f
        try:
            content = absf.read_text(encoding='utf-8')
        except Exception:
            continue
        if not content.strip():
            continue
        doc.append(heading(f))
        doc.append(tab_block(content))
        doc.append('\n')
    doc.append("--\n")
    full = ''.join(doc)
    h = hashlib.sha256(full.encode('utf-8')).hexdigest()[:12]
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    outfile = root / f"repo2md-{ts}-{h}.md"
    outfile.write_text(full, encoding='utf-8')
    typer.echo(f"Wrote {outfile.resolve()}")

if __name__ == "__main__":
    app()
