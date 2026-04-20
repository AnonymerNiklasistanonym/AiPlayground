from pathlib import Path

from tool import tool

LATEX_DIRECTORIES: [Path] = []
LATEX_AUX_DIRECTORIES: [Path] = []
LATEX_AUX_FILES: [Path] = []

FILTER_DIRS = {"build", "dist", "__pycache__", ".idea", ".vscode", "bin"}


def _is_within(path: Path, allowed: Path) -> bool:
    try:
        path = path.resolve()
        allowed = allowed.resolve()
        return allowed in path.parents or path == allowed
    except Exception:
        return False


def _check_read_permission(path: Path) -> bool:
    # Explicit file allowlist
    for f in LATEX_AUX_FILES:
        if path.resolve() == f.resolve():
            return True

    # Directory allowlist
    for d in LATEX_DIRECTORIES + LATEX_AUX_DIRECTORIES:
        if _is_within(path, d):
            return True

    return False


def _check_write_permission(path: Path) -> bool:
    # Writes should generally be more restrictive:
    # allow only inside AUX dirs or explicitly listed files
    for f in LATEX_AUX_FILES:
        if path.resolve() == f.resolve():
            return True

    for d in LATEX_AUX_DIRECTORIES:
        if _is_within(path, d):
            return True

    for d in LATEX_DIRECTORIES:
        if _is_within(path, d):
            return True

    return False


@tool
def tool_list_files() -> str:
    """
    List all files of this LaTeX project with access
    """
    files = set()

    for directory in LATEX_DIRECTORIES + LATEX_AUX_DIRECTORIES:
        try:
            for p in directory.rglob("*"):
                if p.is_file() and FILTER_DIRS.isdisjoint(p.parts):
                    files.add(str(p.resolve()))
        except Exception as e:
            return f"Error accessing directory {directory}: {e}"

    for f in LATEX_AUX_FILES:
        try:
            if f.exists():
                files.add(str(f.resolve()))
        except Exception as e:
            return f"Error accessing file {f}: {e}"

    return "\n".join(sorted(files))


@tool
def tool_read_file(file_path: str) -> str:
    """
    Read a file (returns error if no permission)
    """
    try:
        path = Path(file_path)

        if not _check_read_permission(path):
            return "Error: Permission denied."

        if not path.exists():
            return "Error: File does not exist."

        if not path.is_file():
            return "Error: Not a file."

        return path.read_text(encoding="utf-8")

    except Exception as e:
        return f"Error reading file: {e}"


@tool
def tool_write_file(file_path: str, content: str) -> str:
    """
    Write a file (returns error if no permission)
    """
    try:
        path = Path(file_path)

        if not _check_write_permission(path):
            return "Error: Permission denied."

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")
        return "OK"

    except Exception as e:
        return f"Error writing file: {e}"
