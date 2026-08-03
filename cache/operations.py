from pathlib import Path
import json
import os

def _get_root(
        cache_folder: str
) -> Path:
    root = Path(__file__).resolve().parent / "folders" / cache_folder
    if not os.path.exists(root):
        raise FileNotFoundError(f"Cache folder {cache_folder} does not exist")

    return root

def _get_path(
        cache_folder: str,
        cache_name: str,
) -> Path:

    return _get_root(cache_folder) / f"{cache_name}.json"

def write_cache(
        cache_folder: str,
        cache_name: str,
        cache_data: dict,
) -> None:

    path = _get_path(cache_folder, cache_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=4)

def read_cache(
        cache_folder: str,
        cache_name: str,
) -> dict:

    path = _get_path(cache_folder, cache_name)
    with open(path, "r", encoding="utf-8") as f:
        cache_data = json.load(f)

    return cache_data

def check_cache(
        cache_folder: str,
        cache_name: str,
) -> bool:

    path = _get_path(cache_folder, cache_name)
    return os.path.exists(path)