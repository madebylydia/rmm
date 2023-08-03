from typing import Any

import re


def get_or_first(storage: dict[Any, Any], key: str):
    """
    Make an attempt to get a value from a given key. If not found, take the first occurrence,
    assuming it exist.

    Parameters
    ----------
    key : str
        The key to use for the attempt.
    """
    return storage.get(key, next(iter(storage)))


def to_safe_path(query: str):
    return re.sub(r"[^\w_. -]", "_", query)


def pretty_size_from_bytes(total_size: float, suffix: str = "B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(total_size) < 1024.0:
            return f"{total_size:3.1f}{unit}{suffix}"
        total_size /= 1024.0
    return f"{total_size:.1f}Yi{suffix}"
