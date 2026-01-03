"""Node schemas for the backend."""

from pathlib import Path
from typing import Any, Dict, List

from psynapse.utils import (
    generate_node_schema_from_python_function,
    get_functions_from_file,
)

# Cache for node schemas to avoid repeated file scanning
_SCHEMA_CACHE: List[Dict[str, Any]] = []


def _get_nodepacks_dir() -> Path:
    """Get the nodepacks directory, checking installed package location first."""
    # First, try to find nodepacks within the installed package
    package_nodepacks = Path(__file__).resolve().parent.parent / "nodepacks"
    if package_nodepacks.exists():
        return package_nodepacks
    
    # Fallback: Look for project root (for editable installs)
    current = Path(__file__).resolve().parent
    while current != current.parent:
        nodepacks_dir = current / "nodepacks"
        if nodepacks_dir.exists():
            return nodepacks_dir
        if (current / "pyproject.toml").exists():
            nodepacks_dir = current / "nodepacks"
            if nodepacks_dir.exists():
                return nodepacks_dir
        current = current.parent
    
    # Final fallback: current working directory
    return Path.cwd() / "nodepacks"


def populate_node_schemas() -> List[Dict[str, Any]]:
    """Populate the node schemas from the nodepacks directory."""
    global _SCHEMA_CACHE

    # Return cached schemas if already populated
    if _SCHEMA_CACHE:
        return _SCHEMA_CACHE

    node_schemas = []
    nodepacks_dir = _get_nodepacks_dir()

    if nodepacks_dir.exists():
        # Iterate through subdirectories in nodepacks
        for nodepack_dir in nodepacks_dir.iterdir():
            # Skip non-directories and special directories like __pycache__
            if not nodepack_dir.is_dir() or nodepack_dir.name.startswith("__"):
                continue

            # Look for ops.py in each nodepack directory
            ops_file = nodepack_dir / "ops.py"
            if ops_file.exists():
                functions = get_functions_from_file(str(ops_file))
                for func in functions:
                    node_schema = generate_node_schema_from_python_function(func)
                    node_schema["filepath"] = str(ops_file)
                    node_schemas.append(node_schema)

    _SCHEMA_CACHE = node_schemas
    return node_schemas


def get_node_schemas() -> List[Dict[str, Any]]:
    """Get all node schemas."""
    return populate_node_schemas()


def get_node_schema(name: str) -> Dict[str, Any]:
    """Get a specific node schema by name."""
    for schema in populate_node_schemas():
        if schema["name"] == name:
            return schema
    return None