"""
Utility functions for secure temporary directory and file handling.
"""
import os
import tempfile
import shutil
from typing import Optional, ContextManager, Any
from contextlib import contextmanager


def get_temp_dir(subdir: Optional[str] = None) -> str:
    """
    Get a secure temporary directory path.
    
    Args:
        subdir: Optional subdirectory to create within the temp directory
        
    Returns:
        str: Path to the temporary directory
    """
    # Use system temp directory with a project-specific prefix
    temp_dir = os.path.join(tempfile.gettempdir(), 'itihasa')
    
    # Add subdirectory if specified
    if subdir:
        temp_dir = os.path.join(temp_dir, subdir)
    
    # Ensure the directory exists
    os.makedirs(temp_dir, exist_ok=True, mode=0o700)
    
    return temp_dir


@contextmanager
def temp_directory(prefix: str = 'itihasa_', cleanup: bool = True) -> ContextManager[str]:
    """
    Context manager that creates and cleans up a temporary directory.
    
    Args:
        prefix: Prefix for the temporary directory name
        cleanup: If True, remove the directory when done
        
    Yields:
        str: Path to the created temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield temp_dir
    finally:
        if cleanup:
            shutil.rmtree(temp_dir, ignore_errors=True)


def safe_join(base: str, *paths: str) -> str:
    """
    Safely join path components and ensure they don't escape the base directory.
    
    Args:
        base: Base directory
        *paths: Path components to join
        
    Returns:
        str: Joined path that is a subpath of base
        
    Raises:
        ValueError: If the resulting path would be outside the base directory
    """
    # Normalize paths
    base = os.path.abspath(base)
    full_path = os.path.abspath(os.path.join(base, *paths))
    
    # Check if the path is still within the base directory
    if not full_path.startswith(base):
        raise ValueError(f"Attempted path traversal: {full_path} is outside of {base}")
    
    return full_path
