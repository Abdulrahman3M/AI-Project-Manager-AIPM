"""Deterministic, local-only source release packaging for AIPM."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat
from typing import Any
import zipfile


SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PRIVATE_KEY_RE = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
AWS_KEY_RE = re.compile(rb"\bAKIA[0-9A-Z]{16}\b")
SENSITIVE_NAMES = {".env", ".env.local", ".env.production", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".secret"}
ROOT_FILES = ("AGENTS.md", "CHANGELOG.md", "Index.md", "LICENSE", "README.md", "VERSION", ".gitignore")
PUBLIC_DIRECTORIES = (
    "01-Skills-General",
    "02-Prompt-General",
    "Capability-Library",
    "Core-Engine",
    "Maintenance-Tools",
    "Plugins/README.md",
    "Plugins/Adapters",
    "Plugins/Build-System",
    "Plugins/aipm-project-agent-bridge",
    "TUI",
    "UX-TUI",
    "docs/README.md",
    "docs/project/Architecture/Plugin-Distribution-Architecture.md",
    "docs/project/Provenance",
    "docs/guides",
)
EXCLUDED_DIRECTORY_NAMES = {".git", ".agents", ".codex", ".migration-staging", ".superpowers", ".test-workspace", "__pycache__", ".pytest_cache"}


class ReleaseError(ValueError):
    """Raised when release construction or verification cannot prove safety."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_version(path: Path, changelog: Path) -> str:
    try:
        version = path.read_text(encoding="utf-8").strip()
        history = changelog.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ReleaseError(f"Missing release metadata: {path}") from exc
    if not SEMVER_RE.fullmatch(version):
        raise ReleaseError(f"Invalid SemVer: {version!r}")
    if not re.search(rf"^#{{1,6}}\s+\[?v?{re.escape(version)}\]?\b", history, re.MULTILINE):
        raise ReleaseError(f"Changelog does not contain current version: {path.parent.name}")
    return version


def _validate_versions(root: Path) -> tuple[str, str]:
    version = _read_version(root / "VERSION", root / "CHANGELOG.md")
    tui_version = _read_version(root / "TUI" / "AI-Project-Manager" / "VERSION", root / "TUI" / "AI-Project-Manager" / "CHANGELOG.md")
    if tui_version != version:
        raise ReleaseError("Platform and TUI versions must match")
    plugin_version = _read_version(root / "Plugins" / "aipm-project-agent-bridge" / "VERSION", root / "Plugins" / "aipm-project-agent-bridge" / "CHANGELOG.md")
    return version, plugin_version


def _is_reparse(path: Path) -> bool:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode):
        return True
    return bool(getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _walk_public(root: Path, relative: Path) -> list[Path]:
    base = root / relative
    if not base.exists():
        return []
    if _is_reparse(base):
        raise ReleaseError(f"Linked path cannot enter a release: {relative.as_posix()}")
    if base.is_file():
        return [base]
    result: list[Path] = []
    for path in sorted(base.rglob("*")):
        relative_parts = path.relative_to(root).parts
        if any(part.casefold() in EXCLUDED_DIRECTORY_NAMES for part in relative_parts):
            continue
        if path.is_dir():
            if _is_reparse(path):
                raise ReleaseError(f"Linked path cannot enter a release: {path.relative_to(root).as_posix()}")
            continue
        if _is_reparse(path) or not path.is_file():
            raise ReleaseError(f"Non-regular file cannot enter a release: {path.relative_to(root).as_posix()}")
        result.append(path)
    return result


def _public_files(root: Path, version: str) -> list[Path]:
    selected = [root / name for name in ROOT_FILES if (root / name).is_file()]
    selected.extend(path for name in PUBLIC_DIRECTORIES for path in _walk_public(root, Path(name)))
    for name in (f"docs/project/Release-Notes-v{version}.md", "docs/project/Support-Matrix.md", "docs/project/Project-Rules.md"):
        candidate = root / name
        if candidate.is_file():
            selected.append(candidate)
    return sorted({path.resolve() for path in selected}, key=lambda path: path.relative_to(root).as_posix())


def _assert_safe(root: Path, files: list[Path]) -> None:
    root_marker = str(root).encode("utf-8").replace(b"\\", b"/").lower()
    for path in files:
        name = path.name.casefold()
        if name in SENSITIVE_NAMES or path.suffix.casefold() in SENSITIVE_SUFFIXES or (name.startswith(".env.") and not name.endswith(".env.example")):
            raise ReleaseError(f"Sensitive-looking file blocks release: {path.relative_to(root).as_posix()}")
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise ReleaseError(f"Cannot read release file: {path.relative_to(root).as_posix()}") from exc
        normalized = data.replace(b"\\", b"/").lower()
        if root_marker in normalized:
            raise ReleaseError(f"Hardcoded local checkout path blocks release: {path.relative_to(root).as_posix()}")
        if PRIVATE_KEY_RE.search(data) or AWS_KEY_RE.search(data):
            raise ReleaseError(f"Credential-like content blocks release: {path.relative_to(root).as_posix()}")


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o100644 & 0xFFFF) << 16
    info.create_system = 3
    return info


def _manifest(version: str, plugin_version: str, files: dict[str, str]) -> bytes:
    document: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_kind": "AIPM_SOURCE_RELEASE",
        "artifact_status": "PREPARED_FOR_OWNER_RELEASE",
        "version": version,
        "plugin_version": plugin_version,
        "license": "AI Project Manager Personal Use License",
        "files": files,
    }
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_release(root: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Build an allowlisted source ZIP and SHA-256 sidecar under the given root."""
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise ReleaseError("AIPM root is not a directory")
    version, plugin_version = _validate_versions(root_path)
    files = _public_files(root_path, version)
    _assert_safe(root_path, files)
    file_hashes = {path.relative_to(root_path).as_posix(): _sha256(path.read_bytes()) for path in files}
    output = Path(output_dir).resolve()
    try:
        output.relative_to(root_path)
    except ValueError as exc:
        raise ReleaseError("Release output must stay inside the AIPM repository") from exc
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"AI-Project-Manager-v{version}.zip"
    prefix = f"AI-Project-Manager-v{version}"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        entries = [(f"{prefix}/{path.relative_to(root_path).as_posix()}", path.read_bytes()) for path in files]
        entries.append((f"{prefix}/Release-Manifest.json", _manifest(version, plugin_version, file_hashes)))
        for name, data in sorted(entries):
            package.writestr(_zip_info(name), data)
    checksum = archive.with_suffix(".zip.sha256")
    digest = _sha256(archive.read_bytes())
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="ascii", newline="\n")
    return {"status": "PASS", "archive": archive, "checksum": checksum, "sha256": digest, "version": version, "file_count": len(files)}


def verify_release(root: str | Path, archive: str | Path, checksum: str | Path | None = None) -> dict[str, Any]:
    """Verify checksum, deterministic release layout, and manifest payload hashes."""
    root_path = Path(root).resolve()
    version, plugin_version = _validate_versions(root_path)
    archive_path = Path(archive)
    checksum_path = Path(checksum) if checksum is not None else archive_path.with_suffix(".zip.sha256")
    try:
        expected, recorded_name = checksum_path.read_text(encoding="ascii").strip().split(maxsplit=1)
    except (OSError, ValueError) as exc:
        raise ReleaseError("Release checksum is missing or invalid") from exc
    if recorded_name.strip() != archive_path.name or _sha256(archive_path.read_bytes()) != expected:
        raise ReleaseError("Release checksum mismatch")
    prefix = f"AI-Project-Manager-v{version}/"
    manifest_name = prefix + "Release-Manifest.json"
    try:
        with zipfile.ZipFile(archive_path) as package:
            names = package.namelist()
            if names != sorted(names) or any(not name.startswith(prefix) for name in names) or manifest_name not in names:
                raise ReleaseError("Release archive layout is invalid")
            manifest = json.loads(package.read(manifest_name))
            if manifest.get("version") != version or manifest.get("plugin_version") != plugin_version:
                raise ReleaseError("Release manifest version metadata is invalid")
            files = manifest.get("files")
            if not isinstance(files, dict):
                raise ReleaseError("Release manifest file map is invalid")
            payload = [name[len(prefix):] for name in names if name != manifest_name]
            if set(payload) != set(files):
                raise ReleaseError("Release manifest paths do not match archive payload")
            for relative, digest in files.items():
                if not isinstance(relative, str) or not isinstance(digest, str) or _sha256(package.read(prefix + relative)) != digest:
                    raise ReleaseError("Release manifest payload hash mismatch")
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        raise ReleaseError("Release archive cannot be verified") from exc
    return {"status": "PASS", "version": version, "file_count": len(files), "archive": archive_path}
