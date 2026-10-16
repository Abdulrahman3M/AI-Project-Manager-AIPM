"""P06 capability registry, provenance, versioning, and Plugin distribution."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
from typing import Any


REGISTRY_PATH = Path("Capability-Library/Registry.json")
PROVENANCE_PATH = Path("Project-Documentation/Provenance/Capability-Library-Ledger.json")
MIGRATION_PATH = Path("Project-Documentation/Provenance/Skill-Migration-Record.json")
SOURCE_REVISION_PATH = Path("Project-Documentation/Provenance/Source-Revision.json")
SOURCE_LICENSE_PATH = Path("Project-Documentation/Provenance/Source-Licenses/Universal-AI-ToolKit-LICENSE.txt")
PLUGIN_VERSION_INITIAL = "0.1.0"
EXCLUDED_SKILLS = {"import-memory", "morning"}
DERIVATIVE_FILES = {
    "CHANGELOG.md",
    "README.md",
    "SKILL.md",
    "references/Orchestration-Model.md",
    "references/Skill-Selection-Protocol.md",
    "templates/Orchestration-Brief.md",
}
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PRIVATE_KEY_RE = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
AWS_KEY_RE = re.compile(rb"\bAKIA[0-9A-Z]{16}\b")
SENSITIVE_NAMES = {".env", ".env.local", ".env.production", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".secret"}


class CapabilityError(ValueError):
    """Raised when capability metadata or a generated package is unsafe or stale."""


def _root(path: str | Path) -> Path:
    root = Path(path).resolve()
    if not root.is_dir():
        raise CapabilityError("AIPM root is not a directory")
    return root


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CapabilityError(f"Cannot read valid JSON: {path.name}") from exc


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _has_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError as exc:
        raise CapabilityError(f"Cannot inspect path: {path}") from exc
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse)


def _tree_files(root: Path) -> dict[str, str]:
    if _has_reparse_point(root):
        raise CapabilityError(f"Linked or reparse-point directory is not allowed: {root}")
    result: dict[str, str] = {}
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in list(directories):
            child = current_path / name
            if _has_reparse_point(child):
                raise CapabilityError(f"Linked or reparse-point directory is not allowed: {child}")
        for name in filenames:
            child = current_path / name
            if _has_reparse_point(child) or not child.is_file():
                raise CapabilityError(f"Linked or non-regular file is not allowed: {child}")
            result[child.relative_to(root).as_posix()] = _sha256_file(child)
    return dict(sorted(result.items()))


def _tree_hash(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in sorted(files.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(file_hash))
        digest.update(b"\n")
    return digest.hexdigest()


def _check_sensitive_files(root: Path) -> None:
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in list(directories):
            child = current_path / name
            if _has_reparse_point(child):
                raise CapabilityError(f"Linked or reparse-point directory is not allowed: {child}")
        for name in filenames:
            path = current_path / name
            folded = name.casefold()
            if folded in SENSITIVE_NAMES or Path(folded).suffix in SENSITIVE_SUFFIXES or folded.endswith(".env.example") is False and folded.startswith(".env."):
                raise CapabilityError(f"Sensitive-looking file blocks Plugin distribution: {path.name}")
            if _has_reparse_point(path):
                raise CapabilityError(f"Linked or reparse-point file is not allowed: {path.name}")
            try:
                content = path.read_bytes()
            except OSError as exc:
                raise CapabilityError(f"Cannot inspect file before distribution: {path.name}") from exc
            if PRIVATE_KEY_RE.search(content) or AWS_KEY_RE.search(content):
                raise CapabilityError(f"Credential-like content blocks Plugin distribution: {path.name}")


def _semver_tuple(value: str) -> tuple[int, int, int]:
    if not isinstance(value, str) or not SEMVER_RE.fullmatch(value):
        raise CapabilityError(f"Invalid SemVer: {value!r}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def bump_semver(version: str, increment: str, *, project: bool = False) -> str:
    major, minor, patch = _semver_tuple(version)
    if increment == "patch":
        patch += 1
    elif increment == "minor":
        minor += 1
        if not project:
            patch = 0
    elif increment == "major":
        major, minor, patch = major + 1, 0, 0
    elif increment != "none":
        raise CapabilityError(f"Unsupported SemVer increment: {increment}")
    return f"{major}.{minor}.{patch}"


def classify_version_change(before: dict[str, str], after: dict[str, str], *, breaking: bool = False) -> str:
    if breaking:
        return "major"
    if set(before) != set(after):
        return "minor"
    if any(before[key] != after[key] for key in before):
        return "patch"
    return "none"


def _at_least_version(actual: str, required: str) -> bool:
    return _semver_tuple(actual) >= _semver_tuple(required)


def _heading_has_version(path: Path, version: str) -> bool:
    escaped = re.escape(version)
    pattern = re.compile(rf"^#{{1,6}}\s+\[?v?{escaped}(?:\])?(?:\s|[-—]|$)", re.MULTILINE)
    try:
        return bool(pattern.search(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError):
        return False


def _read_version(path: Path, *, changelog: Path | None = None) -> str:
    try:
        version = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        raise CapabilityError(f"Missing or unreadable VERSION: {path}") from exc
    _semver_tuple(version)
    if changelog is not None and (not changelog.is_file() or not _heading_has_version(changelog, version)):
        raise CapabilityError(f"CHANGELOG.md does not contain current VERSION heading: {path.parent.name}")
    return version


def _parse_frontmatter(path: Path, expected_name: str) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CapabilityError(f"Missing or unreadable SKILL.md: {expected_name}") from exc
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if not match:
        raise CapabilityError(f"SKILL.md frontmatter is missing: {expected_name}")
    lines = match.group(1).splitlines()
    values: dict[str, str] = {}
    for index, line in enumerate(lines):
        field = re.match(r"^(name|description):\s*(.*)$", line)
        if not field:
            continue
        key, raw = field.groups()
        if raw in {">", ">-", "|", "|-"}:
            parts = []
            for following in lines[index + 1 :]:
                if following and not following[0].isspace():
                    break
                if following.strip():
                    parts.append(following.strip())
            values[key] = ("\n" if raw.startswith("|") else " ").join(parts)
        else:
            values[key] = raw.strip().strip("\"'")
    name, description = values.get("name", ""), values.get("description", "")
    if name != expected_name or not description:
        raise CapabilityError(f"SKILL.md requires matching name and nonempty description: {expected_name}")
    return name, description


def _migration_record(root: Path) -> dict[str, Any]:
    record = _json(root / MIGRATION_PATH)
    if not isinstance(record, dict):
        raise CapabilityError("Skill migration record is not an object")
    return record


def _initial_migration_check(root: Path, skill_slugs: set[str], migration: dict[str, Any]) -> None:
    preserved = set(migration.get("byte_preserved_skills", []))
    derivative = migration.get("derivative_skill")
    if not isinstance(derivative, str) or skill_slugs != preserved | {derivative}:
        raise CapabilityError("Initial Skill inventory does not match the owner-approved migration record")
    if len(skill_slugs) != 17 or skill_slugs & EXCLUDED_SKILLS:
        raise CapabilityError("Initial inventory must contain the approved 17 Skills and no excluded Skill")
    if (root / "02-Skills-Personal").exists():
        raise CapabilityError("Personal Skills root is forbidden in AIPM")
    source_hashes = migration.get("source_hashes", {})
    changed_files = set(migration.get("derivative_changed_markdown_files", []))
    if set(source_hashes) != preserved or changed_files != DERIVATIVE_FILES:
        raise CapabilityError("P01 provenance does not describe the approved 16+1 migration boundary")
    actual_map = {slug: _tree_files(root / "01-Skills-General" / slug) for slug in skill_slugs}
    for slug in preserved:
        if actual_map[slug] != source_hashes.get(slug):
            raise CapabilityError(f"Byte-preserved Skill differs from the P01 source hashes: {slug}")
    derivative_files = actual_map[derivative]
    if not derivative_files or not changed_files.issubset(derivative_files):
        raise CapabilityError(f"Documented derivative is missing approved files: {derivative}")


def _owned_prompt_paths(skill_root: Path) -> list[str]:
    result = []
    for path in skill_root.rglob("*.md"):
        relative = path.relative_to(skill_root)
        if relative.as_posix() == "PROMPT.md" or any(part in {"prompts", "Prompts"} for part in relative.parts[:-1]):
            result.append(relative.as_posix())
    return sorted(result)


def _prompt_metadata(path: Path) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CapabilityError(f"Cannot read Prompt: {path.name}") from exc
    header = text[:2000]
    name = re.search(r"(?m)^Prompt:\s*(.+?)\s*$", header)
    version = re.search(r"(?m)^Version:\s*(\d+\.\d+\.\d+)\s*$", header)
    if not name or not version or "Type: Standalone" not in header:
        raise CapabilityError(f"Standalone Prompt needs name, SemVer, and Standalone type: {path.name}")
    _semver_tuple(version.group(1))
    return name.group(1).strip(), version.group(1)


def _source_revision(root: Path) -> dict[str, Any]:
    source = _json(root / SOURCE_REVISION_PATH)
    required = ("repository", "ref", "commit_sha", "commit_status", "source_license_sha256", "source_writes")
    if not isinstance(source, dict) or any(key not in source for key in required):
        raise CapabilityError("Source revision provenance is incomplete")
    if source["commit_status"] != "VERIFIED" or not re.fullmatch(r"[0-9a-f]{40}", source["commit_sha"]):
        raise CapabilityError("Live source Git commit is not verified")
    if source["source_writes"] != 0:
        raise CapabilityError("Source repository provenance reports a write")
    license_path = root / SOURCE_LICENSE_PATH
    if _sha256_file(license_path) != source["source_license_sha256"]:
        raise CapabilityError("Source license copy does not match its recorded SHA-256")
    return source


def _catalog(root: Path) -> dict[str, Any]:
    root = _root(root)
    skills_root = root / "01-Skills-General"
    if not skills_root.is_dir() or _has_reparse_point(skills_root):
        raise CapabilityError("General Skill master root is missing or linked")
    active_slugs = {path.name for path in skills_root.iterdir() if path.is_dir()}
    if active_slugs & EXCLUDED_SKILLS or (root / "02-Skills-Personal").exists():
        raise CapabilityError("Excluded or Personal Skills are present")
    migration = _migration_record(root)
    # Keep the P01 migration record authoritative even after registry creation;
    # a registry refresh must never legitimize edits to the 16 byte-preserved imports.
    _initial_migration_check(root, active_slugs, migration)
    _check_sensitive_files(skills_root)
    project_version = _read_version(root / "VERSION", changelog=root / "CHANGELOG.md")
    source = _source_revision(root)
    skills = []
    owned: dict[str, list[str]] = {}
    owned_prompt_hashes: set[str] = set()
    for slug in sorted(active_slugs):
        skill_root = skills_root / slug
        files = _tree_files(skill_root)
        name, description = _parse_frontmatter(skill_root / "SKILL.md", slug)
        version = _read_version(skill_root / "VERSION", changelog=skill_root / "CHANGELOG.md")
        prompts = _owned_prompt_paths(skill_root)
        owned[slug] = prompts
        for relative in prompts:
            owned_prompt_hashes.add(files[relative])
        notices = [path for path in files if Path(path).name.casefold().startswith(("license", "notice"))]
        skills.append({
            "slug": slug,
            "name": name,
            "description": description,
            "version": version,
            "path": f"01-Skills-General/{slug}",
            "sha256": _tree_hash(files),
            "files": files,
            "skill_owned_prompts": prompts,
            "license": {
                "source_license": "Universal AI ToolKit Personal Use License",
                "source_license_path": SOURCE_LICENSE_PATH.as_posix(),
                "retained_skill_notices": notices,
                "aipm_apache_applies": False,
            },
            "customization": "P01 owner-approved derivative" if slug == migration.get("derivative_skill") else "None",
        })
    prompt_root = root / "02-Prompt-General"
    if not prompt_root.is_dir():
        raise CapabilityError("Owner-approved standalone Prompt library is missing")
    standalone = []
    for path in sorted(prompt_root.rglob("*.md")):
        if path.name == "README.md":
            continue
        name, version = _prompt_metadata(path)
        file_hash = _sha256_file(path)
        if file_hash in owned_prompt_hashes:
            raise CapabilityError(f"Standalone Prompt duplicates a Skill-owned Prompt: {path.name}")
        standalone.append({
            "name": name,
            "version": version,
            "path": path.relative_to(root).as_posix(),
            "sha256": file_hash,
            "license_scope": "AIPM-authored material; root Apache-2.0 applies",
        })
    if not standalone:
        raise CapabilityError("No approved standalone Prompt is registered")
    return {
        "schema_version": "1.0",
        "platform_version": project_version,
        "source": {
            "repository": source["repository"],
            "ref": source["ref"],
            "commit_sha": source["commit_sha"],
            "commit_status": source["commit_status"],
            "verified_on": source.get("verified_on"),
            "source_archive_sha256": source.get("source_archive_sha256"),
            "source_license_sha256": source["source_license_sha256"],
            "writes": source["source_writes"],
        },
        "skills": skills,
        "skill_owned_prompts": {slug: paths for slug, paths in owned.items() if paths},
        "standalone_prompts": standalone,
        "exclusions": {"personal_skills_imported": False, "skill_slugs": sorted(EXCLUDED_SKILLS)},
    }


def scan_library(root: str | Path) -> dict[str, Any]:
    """Return a deterministic catalog derived from the authoritative local masters."""
    return _catalog(_root(root))


def _provenance_ledger(catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "source": catalog["source"],
        "skills": [
            {
                "slug": skill["slug"],
                "original_author": "Abdulrahman Elbatrah; see retained third-party notices where present",
                "source_repository": catalog["source"]["repository"],
                "source_path": skill["path"],
                "source_commit_sha": catalog["source"]["commit_sha"],
                "source_license": skill["license"]["source_license"],
                "source_license_sha256": catalog["source"]["source_license_sha256"],
                "retained_skill_notices": skill["license"]["retained_skill_notices"],
                "local_version": skill["version"],
                "local_sha256": skill["sha256"],
                "customization": skill["customization"],
            }
            for skill in catalog["skills"]
        ],
        "standalone_prompts": catalog["standalone_prompts"],
        "license_scope": "Root Apache-2.0 applies only to AIPM-authored files; imported Skill terms and notices remain controlling.",
        "distribution": "Local sample only; not published or installed.",
    }


def _write_json_atomic(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(document, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        raise CapabilityError(f"Atomic JSON write failed: {path.name}") from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _write_records(root: Path, catalog: dict[str, Any]) -> None:
    registry_path, provenance_path = root / REGISTRY_PATH, root / PROVENANCE_PATH
    existed = {path: path.read_bytes() if path.exists() else None for path in (registry_path, provenance_path)}
    try:
        _write_json_atomic(registry_path, catalog)
        _write_json_atomic(provenance_path, _provenance_ledger(catalog))
    except Exception:
        for path, old in existed.items():
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(old)
        raise


def initialize_registry(root: str | Path) -> dict[str, Any]:
    """Create the protected initial registry once, from the P01-verified masters."""
    root = _root(root)
    if (root / REGISTRY_PATH).exists() or (root / PROVENANCE_PATH).exists():
        raise CapabilityError("Integrity baseline already exists; initialization never overwrites it")
    catalog = _catalog(root)
    _write_records(root, catalog)
    return {"status": "PASS", "skill_count": len(catalog["skills"]), "standalone_prompt_count": len(catalog["standalone_prompts"])}


def _assert_version_policy(previous: dict[str, Any], current: dict[str, Any]) -> None:
    before = {item["slug"]: item["sha256"] for item in previous["skills"]}
    after = {item["slug"]: item["sha256"] for item in current["skills"]}
    change = classify_version_change(before, after)
    if change != "none":
        required = bump_semver(previous["platform_version"], change, project=True)
        if not _at_least_version(current["platform_version"], required):
            raise CapabilityError(f"AIPM VERSION must advance to at least {required} for this Skill change")
    old_skills = {item["slug"]: item for item in previous["skills"]}
    for item in current["skills"]:
        old = old_skills.get(item["slug"])
        if old and old["sha256"] != item["sha256"]:
            required = bump_semver(old["version"], "patch")
            if not _at_least_version(item["version"], required):
                raise CapabilityError(f"Skill VERSION must advance to at least {required}: {item['slug']}")


def validate_registry(root: str | Path) -> dict[str, Any]:
    root = _root(root)
    catalog = _catalog(root)
    registry = _json(root / REGISTRY_PATH)
    ledger = _json(root / PROVENANCE_PATH)
    if registry != catalog:
        raise CapabilityError("Capability registry is stale or differs from the authoritative masters")
    if ledger != _provenance_ledger(catalog):
        raise CapabilityError("Capability provenance ledger is stale")
    return {"status": "PASS", "skill_count": len(catalog["skills"]), "standalone_prompt_count": len(catalog["standalone_prompts"])}


def refresh_registry(root: str | Path, *, confirmed: bool, reason: str) -> dict[str, Any]:
    root = _root(root)
    if confirmed is not True or not isinstance(reason, str) or not reason.strip():
        raise CapabilityError("Baseline refresh requires explicit confirmation and a nonempty reason")
    previous = _json(root / REGISTRY_PATH)
    current = _catalog(root)
    _assert_version_policy(previous, current)
    _write_records(root, current)
    return {"status": "PASS", "reason": reason.strip(), "skill_count": len(current["skills"]), "standalone_prompt_count": len(current["standalone_prompts"])}


def _within(root: Path, target: Path) -> Path:
    root_resolved = root.resolve()
    target_resolved = target.resolve(strict=False)
    if target_resolved == root_resolved or not target_resolved.is_relative_to(root_resolved):
        raise CapabilityError("Plugin output path must remain inside the AIPM repository")
    current = root_resolved
    for part in target_resolved.relative_to(root_resolved).parts:
        current = current / part
        if current.exists() and _has_reparse_point(current):
            raise CapabilityError("Plugin output path contains a symlink or reparse point")
    return target_resolved


def _plugin_json(version: str) -> dict[str, Any]:
    return {
        "name": "aipm-general-skills",
        "version": version,
        "description": "A local sample package of the approved AIPM General Skills.",
        "skills": "./skills/",
        "interface": {
            "displayName": "AIPM General Skills",
            "shortDescription": "Owner-approved general Skill masters",
            "longDescription": "Generated copies of the AIPM General Skill masters. This local sample is not published or automatically installed.",
            "developerName": "AI Project Manager",
            "category": "Productivity",
            "capabilities": ["General Skills"],
        },
    }


def _distribution_manifest(catalog: dict[str, Any], version: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "generated_by": "AIPM Capability Library",
        "plugin_name": "aipm-general-skills",
        "plugin_version": version,
        "status": "LOCAL_SAMPLE_NOT_PUBLISHED",
        "source_commit_sha": catalog["source"]["commit_sha"],
        "source_project_version": catalog["platform_version"],
        "source_license_sha256": catalog["source"]["source_license_sha256"],
        "personal_skills_included": False,
        "standalone_prompts_included": False,
        "skills": [
            {
                "slug": item["slug"],
                "version": item["version"],
                "source_sha256": item["sha256"],
                "files": item["files"],
            }
            for item in catalog["skills"]
        ],
    }


def _plugin_readme(count: int) -> str:
    return (
        "# AIPM General Skills\n\n"
        f"This generated local sample contains {count} approved General Skills copied from `01-Skills-General`.\n\n"
        "It excludes Personal Skills and standalone Prompts. Skill-owned Prompts remain in their owning Skill folders.\n\n"
        "This package is not published or installed. Imported Skill files retain the Universal AI ToolKit Personal Use License and any per-Skill notices; the AIPM Apache-2.0 license does not relicense them.\n"
    )


def _plugin_changelog(version: str) -> str:
    return f"# AIPM General Skills Change Log\n\n## [{version}] — Initial Local Sample\n\n- Generated from the approved AIPM General Skill masters.\n- Preserved Skill file bytes and included source license notices.\n- Not published or installed.\n"


def _plugin_expected_files(catalog: dict[str, Any], version: str) -> dict[str, bytes]:
    manifest = _distribution_manifest(catalog, version)
    files = {
        ".codex-plugin/plugin.json": (json.dumps(_plugin_json(version), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        "AIPM-Distribution-Manifest.json": (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        "README.md": _plugin_readme(len(catalog["skills"])).encode("utf-8"),
        "VERSION": (version + "\n").encode("utf-8"),
        "CHANGELOG.md": _plugin_changelog(version).encode("utf-8"),
        "licenses/Universal-AI-ToolKit-LICENSE.txt": (catalog["source"]["source_license_sha256"],),
    }
    return files  # The license entry is replaced with bytes by _materialize_plugin.


def _materialize_plugin(root: Path, stage: Path, catalog: dict[str, Any], version: str) -> None:
    (stage / "skills").mkdir(parents=True)
    for item in catalog["skills"]:
        source = root / item["path"]
        destination = stage / "skills" / item["slug"]
        shutil.copytree(source, destination, copy_function=shutil.copy2, symlinks=False)
        if _tree_files(destination) != item["files"]:
            raise CapabilityError(f"Generated Skill copy failed byte-parity check: {item['slug']}")
    for relative, content in _plugin_expected_files(catalog, version).items():
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, tuple):
            content = (root / SOURCE_LICENSE_PATH).read_bytes()
        target.write_bytes(content)


def _manifest_from_plugin(target: Path) -> dict[str, Any]:
    path = target / "AIPM-Distribution-Manifest.json"
    manifest = _json(path)
    if not isinstance(manifest, dict) or manifest.get("generated_by") != "AIPM Capability Library":
        raise CapabilityError("Existing output is not a recognized AIPM-generated Plugin")
    return manifest


def _validate_embedded_plugin(target: Path) -> dict[str, Any]:
    if not target.is_dir() or _has_reparse_point(target):
        raise CapabilityError("Generated Plugin directory is missing or linked")
    manifest = _manifest_from_plugin(target)
    version = manifest.get("plugin_version")
    _semver_tuple(version)
    manifest_skills = manifest.get("skills")
    if not isinstance(manifest_skills, list) or manifest.get("personal_skills_included") is not False or manifest.get("standalone_prompts_included") is not False:
        raise CapabilityError("Generated Plugin manifest has invalid scope")
    if manifest.get("plugin_name") != "aipm-general-skills" or manifest.get("status") != "LOCAL_SAMPLE_NOT_PUBLISHED":
        raise CapabilityError("Generated Plugin identity or publication state is invalid")
    expected_paths = {
        ".codex-plugin/plugin.json",
        "AIPM-Distribution-Manifest.json",
        "README.md",
        "VERSION",
        "CHANGELOG.md",
        "licenses/Universal-AI-ToolKit-LICENSE.txt",
    }
    for skill in manifest_skills:
        slug, files = skill.get("slug"), skill.get("files")
        if not isinstance(slug, str) or not isinstance(files, dict) or slug in EXCLUDED_SKILLS:
            raise CapabilityError("Generated Plugin contains an invalid Skill record")
        expected_paths.update(f"skills/{slug}/{relative}" for relative in files)
    actual_paths = set(_tree_files(target))
    if actual_paths != expected_paths:
        raise CapabilityError("Generated Plugin contains missing or unexpected files")
    for skill in manifest_skills:
        slug = skill["slug"]
        copied = _tree_files(target / "skills" / slug)
        if copied != skill["files"] or _tree_hash(copied) != skill["source_sha256"]:
            raise CapabilityError(f"Generated Plugin Skill bytes are changed: {slug}")
    if _read_version(target / "VERSION", changelog=target / "CHANGELOG.md") != version:
        raise CapabilityError("Generated Plugin version metadata is inconsistent")
    for relative, content in {
        ".codex-plugin/plugin.json": (json.dumps(_plugin_json(version), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        "README.md": _plugin_readme(len(manifest_skills)).encode("utf-8"),
        "CHANGELOG.md": _plugin_changelog(version).encode("utf-8"),
    }.items():
        if (target / relative).read_bytes() != content:
            raise CapabilityError(f"Generated Plugin metadata drifted: {relative}")
    plugin_data = _json(target / ".codex-plugin" / "plugin.json")
    if plugin_data.get("license") is not None or plugin_data.get("skills") != "./skills/":
        raise CapabilityError("Plugin must not claim a blanket license and must declare its Skill root")
    return manifest


def validate_plugin(root: str | Path, target: str | Path) -> dict[str, Any]:
    root = _root(root)
    target_path = _within(root, Path(target) if Path(target).is_absolute() else root / target)
    catalog = _catalog(root)
    _check_sensitive_files(target_path)
    manifest = _validate_embedded_plugin(target_path)
    if manifest != _distribution_manifest(catalog, manifest["plugin_version"]):
        raise CapabilityError("Generated Plugin is not in parity with the current capability registry")
    for item in catalog["skills"]:
        if _tree_files(target_path / "skills" / item["slug"]) != item["files"]:
            raise CapabilityError(f"Plugin source parity failure: {item['slug']}")
    if (target_path / "licenses" / "Universal-AI-ToolKit-LICENSE.txt").read_bytes() != (root / SOURCE_LICENSE_PATH).read_bytes():
        raise CapabilityError("Generated Plugin did not preserve the source license bytes")
    return {"status": "PASS", "skill_count": len(catalog["skills"]), "standalone_prompt_count": 0, "published": False, "installed": False}


def build_plugin(root: str | Path, target: str | Path, *, replace_generated: bool = False) -> dict[str, Any]:
    root = _root(root)
    target_path = _within(root, Path(target) if Path(target).is_absolute() else root / target)
    catalog = _catalog(root)
    registry = _json(root / REGISTRY_PATH)
    if registry != catalog or _json(root / PROVENANCE_PATH) != _provenance_ledger(catalog):
        raise CapabilityError("Registry and provenance must validate before Plugin generation")
    _check_sensitive_files(root / "01-Skills-General")
    if target_path.exists():
        try:
            validate_plugin(root, target_path)
            return {"status": "UNCHANGED", "skill_count": len(catalog["skills"]), "path": target_path.relative_to(root).as_posix()}
        except CapabilityError:
            if replace_generated is not True:
                raise CapabilityError("Existing Plugin is stale; explicit --replace-generated is required")
            old_manifest = _validate_embedded_plugin(target_path)
            old_hashes = {item["slug"]: item["source_sha256"] for item in old_manifest["skills"]}
            new_hashes = {item["slug"]: item["sha256"] for item in catalog["skills"]}
            change = classify_version_change(old_hashes, new_hashes)
            if change != "none":
                required = bump_semver(old_manifest["plugin_version"], change)
                target_version = _read_version(target_path / "VERSION", changelog=target_path / "CHANGELOG.md")
                if not _at_least_version(target_version, required):
                    raise CapabilityError(f"Plugin VERSION must advance to at least {required} before replacement")
            version = _read_version(target_path / "VERSION", changelog=target_path / "CHANGELOG.md")
        backup: Path | None = None
    else:
        version, backup = PLUGIN_VERSION_INITIAL, None
    workspace = root / ".test-workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="p06-plugin-stage-", dir=workspace))
    preserve_backup = False
    backup_directory: Path | None = None
    try:
        _materialize_plugin(root, stage, catalog, version)
        # Validate the staged package's own checksums before it can replace a target.
        _validate_embedded_plugin(stage)
        if target_path.exists():
            backup_directory = Path(tempfile.mkdtemp(prefix="p06-plugin-backup-", dir=workspace))
            backup = backup_directory / "previous"
            os.replace(target_path, backup)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.replace(stage, target_path)
        except OSError as install_error:
            if backup is not None and backup.exists():
                try:
                    os.replace(backup, target_path)
                except OSError as restore_error:
                    preserve_backup = True
                    raise CapabilityError(f"Plugin replacement failed; previous sample is preserved at {backup}") from restore_error
            raise CapabilityError("Plugin replacement failed; the previous sample was restored") from install_error
        validate_plugin(root, target_path)
        if backup_directory is not None and backup_directory.exists():
            shutil.rmtree(backup_directory)
    except OSError as exc:
        raise CapabilityError("Plugin generation could not be completed safely") from exc
    finally:
        if stage.exists():
            shutil.rmtree(stage)
        if backup_directory is not None and backup_directory.exists() and not preserve_backup:
            shutil.rmtree(backup_directory)
    return {"status": "PASS", "skill_count": len(catalog["skills"]), "path": target_path.relative_to(root).as_posix()}
