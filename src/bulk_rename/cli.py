from pathlib import Path
from datetime import datetime
import argparse
import sys
import os
from importlib.metadata import version, PackageNotFoundError


def generate_new_name(pattern: str, index: int, extension: str) -> str:
    """
    Generate a new filename based on a formatting pattern.

    Args:
        pattern: A format pattern containing a placeholder (e.g., "file_{:03d}").
        index: The file index used to fill the placeholder.
        extension: File extension (without a leading dot).

    Returns:
        The new filename.

    Raises:
        TypeError: If index is not an integer.
        ValueError: If index is negative.

    Example:
        >>> generate_new_name("file_{:03d}", 1, "txt")
        "file_001.txt"
    """
    if not isinstance(index, int):
        raise TypeError(f"Index must be int, got {type(index).__name__}")

    if index < 0:
        raise ValueError(f"Index must be non-negative, got {index}")

    base_name = pattern.format(index)
    return f"{base_name}.{extension}"


def find_files(directory: Path, extension: str) -> list[Path]:
    """
    Find all files with specified extension in directory.

    Args:
        directory: Path to the directory to search
        extension: File extension without dot (e.g., "mp4")

    Returns:
        List of Path objects for found files

    Example:
        >>> find_files(Path("./videos"), "mp4")
        [Path("video1.mp4"), Path("video2.mp4")]
    """
    return list(directory.glob(f"*.{extension}"))


def sort_files(files: list[Path]) -> list[Path]:
    """
    Sort files alphabetically by name.

    Args:
        files: List of file paths

    Returns:
        Sorted list of file paths
    """
    return sorted(files, key=lambda f: f.name)


def generate_rename_plan(
    files: list[Path], pattern: str, start_index: int = 1
) -> list[tuple[Path, Path]]:
    """
    Generate rename plan (old_path, new_path) for each file.

    Args:
        files: List of files to rename
        pattern: Naming pattern (e.g., "file_{:03d}")
        start_index: Starting index for numbering

    Returns:
        List of (old_path, new_path) tuples

    Example:
        >>> files = [Path("a.mp4"), Path("b.mp4")]
        >>> generate_rename_plan(files, "video_{:03d}", start_index=1)
        [(Path("a.mp4"), Path("video_001.mp4")),
         (Path("b.mp4"), Path("video_002.mp4"))]
    """
    plan = []

    for index, old_path in enumerate(files, start=start_index):
        parent_dir = old_path.parent
        extension = old_path.suffix[1:]

        new_filename = generate_new_name(pattern, index, extension)
        new_path = parent_dir / new_filename

        plan.append((old_path, new_path))

    return plan


def validate_rename_plan(rename_plan: list[tuple[Path, Path]]) -> list[tuple[Path, Path, str]]:
    """
    Validate rename operations before execution.

    Args:
        rename_plan: List of (old_path, new_path) tuples

    Returns:
        List of (old_path, new_path, error_message) for problematic operations

    Checks:
        - Source file is not found
        - Target file already exists
    """
    conflicts = []

    for old_path, new_path in rename_plan:
        if not old_path.exists():
            conflicts.append((old_path, new_path, "Source file is not found"))

        elif new_path.exists():
            conflicts.append((old_path, new_path, "Target file already exists"))

    return conflicts


def show_preview(rename_plan: list[tuple[Path, Path]]) -> None:
    """
    Display preview of rename operations.

    Args:
        rename_plan: List of (old_path, new_path) tuples

    Returns:
        None (prints to console)

    Example output:
        ✅ a.mp4 -> video_001.mp4
        ❌ b.mp4 -> video_002.mp4 [Target file already exists]
    """
    conflicts = validate_rename_plan(rename_plan)

    conflict_dict = {(old, new): error for old, new, error in conflicts}

    for old_path, new_path in rename_plan:
        if (old_path, new_path) in conflict_dict:
            error_msg = conflict_dict[(old_path, new_path)]
            print(f"❌ {old_path} -> {new_path} [{error_msg}]")

        else:
            print(f"✅ {old_path} -> {new_path}")


def confirm_action(prompt: str = "Proceed? (y/n): ") -> bool:
    """
    Ask user for confirmation.

    Args:
        prompt: Question to ask user

    Returns:
        True if user confirms, False otherwise
    """
    user_input = input(prompt)
    return user_input.strip().lower() in {"y", "yes"}


def save_backup(rename_plan: list[tuple[Path, Path]], backup_dir: Path) -> Path:
    """
    Save original filenames to a backup file in the specified directory.

    Args:
        rename_plan: List of (old_path, new_path) tuples
        backup_dir: Directory where the backup file will be saved

    Returns:
        Path to the created backup file

    File format:
        old_name.mp4 -> new_name.mp4
        another.mp4 -> another_001.mp4
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    backup_path = backup_dir / f"backup_{timestamp}.txt"

    with backup_path.open("w", encoding="utf-8") as backup:
        for old_path, new_path in rename_plan:
            backup.write(f"{old_path} -> {new_path}\n")

    return backup_path


def execute_rename(rename_plan: list[tuple[Path, Path]]) -> None:
    """
    Execute rename operations after validation, skipping conflics, and display results.

    Args:
        rename_plan: List of (old_path, new_path) tuples

    Returns:
        None (prints to console)

    Example output:
        ✅ a.mp4 -> video_001.mp4
        ⚠️ [SKIPPED] b.mp4 -> video_002.mp4 [Target file already exists]
    """
    conflicts = validate_rename_plan(rename_plan)

    conflict_dict = {(old, new): error for old, new, error in conflicts}

    for old_path, new_path in rename_plan:
        if (old_path, new_path) in conflict_dict:
            error_msg = conflict_dict[(old_path, new_path)]
            print(f"⚠️ [SKIPPED] {old_path} -> {new_path} [{error_msg}]")
        else:
            old_path.rename(new_path)


def parse_args():
    """
    Parse command-line arguments.

    This function sets up and parses the command-line arguments required to run the tool.
    It defines the following arguments:

    - --path / -d (Path, required): The directory containing the files to rename.
    - --pattern / -p (str, required): The naming pattern for the new files (e.g., 'file_{:03d}').
    - --extension / -e (str, required): The file extension to filter files by (e.g., 'mp4').
    - --start / -s (int, optional): The starting index for numbering files (default is 1).
    - --version: Displays the program's version and exits.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    try:
        __version__ = version("bulk-rename")
    except PackageNotFoundError:
        __version__ = "0.0.0-dev [PACKAGE IS NOT FOUND]"

    parser = argparse.ArgumentParser(
        prog=f"Bulk Rename Utility v{__version__}",
        description="Bulk rename files based on a pattern.",
    )

    parser.add_argument(
        "-d",
        "--path",
        type=Path,
        required=True,
        help="Directory containing the files to rename",
    )

    parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        required=True,
        help="Naming pattern for new files (e.g., 'file_{:03d}')",
    )

    parser.add_argument(
        "-e",
        "--extension",
        type=str,
        required=True,
        help="File extension to filter (e.g., 'mp4')",
    )

    parser.add_argument(
        "-s",
        "--start",
        default=1,
        type=int,
        help="Starting index for numbering (default: 1)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Show program's version number and exit",
    )

    return parser.parse_args()


def main():
    """Entry point for CLI."""
    args = parse_args()

    if not args.path.exists():
        print(f"Path {args.path} doesn't exist", file=sys.stderr)
        sys.exit(1)
    elif not os.access(args.path, os.R_OK):
        print(f"No permission to read {args.path}", file=sys.stderr)
        sys.exit(1)

    files = find_files(args.path, args.extension)

    if not files:
        print(f"No .{args.extension} files found in {args.path}", file=sys.stderr)
        sys.exit(1)

    sorted_files = sort_files(files)

    plan = generate_rename_plan(sorted_files, args.pattern, args.start)

    conflicts = validate_rename_plan(plan)

    show_preview(plan)

    if conflicts:
        suffix = "s" if len(conflicts) != 1 else ""
        print(f"\nFound {len(conflicts)} conflict{suffix}")
        if not confirm_action(f"Continue with skipping conflict{suffix}? (y/n): "):
            sys.exit(0)
    elif not confirm_action():
        sys.exit(0)

    if not os.access(args.path, os.W_OK):
        print(f"No permission to write {args.path}", file=sys.stderr)
        sys.exit(1)

    conflicted_pairs = {(old, new) for old, new, _ in conflicts}
    effective_ops = [(old, new) for old, new in plan if (old, new) not in conflicted_pairs]

    if not effective_ops:
        print("Nothing to rename. All operations are conflics.")
        sys.exit(0)

    save_backup(effective_ops, args.path)

    execute_rename(effective_ops)


if __name__ == "__main__":
    main()
