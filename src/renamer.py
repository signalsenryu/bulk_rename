from pathlib import Path

def generate_new_name(pattern: str, index: int, extension: str) -> str:
    """
    Generate a new filename based on a formatting pattern.
    
    Args:
        pattern: A format pattern containing a placeholder (e.g., "ASMR_{:03d}").
        index: The file index used to fill the placeholder.
        extension: File extension (without a leading dot).
        
    Returns:
        The new filename.
        
    Raises:
        TypeError: If index is not an integer.
        ValueError: If index is negative.
        
    Example:
        >>> generate_new_name("ASMR_{:03d}", 1, "mp4")
        "ASMR_001.mp4"
    """
    if not isinstance(index, int):
        raise TypeError(f"Index must be int, got {type(index).__name__}")

    if index < 0:
        raise ValueError(f"Index must be non-negative, got {index}")

    base_name = pattern.format(index)
    return f"{base_name}.{extension}"


def find_files(directory_path: Path, extension: str) -> list[Path]:
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
    return list(directory_path.glob(f"*.{extension}"))
