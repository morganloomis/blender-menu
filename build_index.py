#!/usr/bin/env python3
"""Package the extension and generate index.json for GitHub Pages."""

import argparse
import fnmatch
import hashlib
import json
import tomllib
import zipfile
from pathlib import Path
from urllib.parse import urlencode

INDEX_FIELDS = (
    "id",
    "name",
    "tagline",
    "version",
    "type",
    "blender_version_min",
    "maintainer",
    "tags",
    "license",
    "schema_version",
)


def load_manifest(repo_root: Path) -> dict:
    manifest_path = repo_root / "blender_manifest.toml"
    with manifest_path.open("rb") as manifest_file:
        return tomllib.load(manifest_file)


def should_exclude(rel_path: str, patterns: list[str]) -> bool:
    rel_path = rel_path.replace("\\", "/")
    name = Path(rel_path).name
    parts = rel_path.split("/")

    for pattern in patterns:
        pattern = pattern.replace("\\", "/")

        if pattern.endswith("/"):
            directory = pattern.rstrip("/")
            if rel_path == directory or rel_path.startswith(f"{directory}/"):
                return True
            if directory in parts:
                return True
            continue

        if "/" in pattern:
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            continue

        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in parts):
            return True

    return False


def collect_files(repo_root: Path, patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(repo_root).as_posix()
        if should_exclude(rel_path, patterns):
            continue
        files.append(path)
    return sorted(files)


def sha256_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as archive_file:
        while chunk := archive_file.read(8192):
            digest.update(chunk)
            size += len(chunk)
    return size, f"sha256:{digest.hexdigest()}"


def build_archive_url(base_url: str, zip_name: str, blender_version_min: str) -> str:
    base = base_url.rstrip("/")
    query = urlencode(
        {
            "repository": "./index.json",
            "blender_version_min": blender_version_min,
        }
    )
    return f"{base}/{zip_name}?{query}"


def build_index_entry(manifest: dict, archive_size: int, archive_hash: str, archive_url: str) -> dict:
    entry = {field: manifest[field] for field in INDEX_FIELDS}
    entry["archive_size"] = archive_size
    entry["archive_hash"] = archive_hash
    entry["archive_url"] = archive_url
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="Directory for the zip and index.json (default: dist/)",
    )
    parser.add_argument(
        "--pages-base-url",
        required=True,
        help="GitHub Pages base URL with trailing slash",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    manifest = load_manifest(repo_root)

    extension_id = manifest["id"]
    version = manifest["version"]
    exclude_patterns = manifest.get("build", {}).get("paths_exclude_pattern", [])

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_name = f"{extension_id}-{version}.zip"
    zip_path = output_dir / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in collect_files(repo_root, exclude_patterns):
            archive.write(file_path, file_path.relative_to(repo_root).as_posix())

    archive_size, archive_hash = sha256_file(zip_path)
    archive_url = build_archive_url(args.pages_base_url, zip_name, manifest["blender_version_min"])

    index = {
        "version": "v1",
        "blocklist": [],
        "data": [
            build_index_entry(manifest, archive_size, archive_hash, archive_url),
        ],
    }

    index_path = output_dir / "index.json"
    with index_path.open("w", encoding="utf-8") as index_file:
        json.dump(index, index_file, indent=4)
        index_file.write("\n")

    print(f"Wrote {zip_path}")
    print(f"Wrote {index_path}")


if __name__ == "__main__":
    main()
