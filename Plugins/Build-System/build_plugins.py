"""Build and validate AIPM multi-host Plugin distribution archives."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile
from typing import Any, Iterable


BUILD_ROOT = Path(__file__).resolve().parent
DEFAULT_ROOT = BUILD_ROOT.parents[1]
PROFILES_ROOT = BUILD_ROOT / "profiles"
STATIC_FILES = {
    "AIPM-Capability-Index.json",
    "AIPM-Distribution-Manifest.json",
    "README.md",
    "VERSION",
    "licenses/Apache-2.0.txt",
    "NOTICE",
}
CHATGPT_STATIC_FILES = {"assets/aipm-icon.svg"}
EXCLUDED_SKILLS = {"import-memory", "morning"}
CHATGPT_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AUTHOR = {"name": "Abdulrahman Elbatrah", "url": "https://github.com/Abdulrahman3M"}
PROJECT_URL = "https://github.com/Abdulrahman3M/AI-Project-Manager-AIPM/"
CHATGPT_ICON = """<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"64\" height=\"64\" viewBox=\"0 0 64 64\" role=\"img\" aria-label=\"AI Project Manager\"><rect width=\"64\" height=\"64\" rx=\"14\" fill=\"#082B3A\"/><path d=\"M16 44V20h8l8 12 8-12h8v24h-8V32l-8 12-8-12v12z\" fill=\"#5CE1E6\"/></svg>\n"""


class PluginBuildError(ValueError):
    """Raised when a distribution archive cannot be safely built or verified."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PluginBuildError(f"Cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise PluginBuildError(f"Expected a JSON object: {path}")
    return value


def _root(root: Path | str) -> Path:
    value = Path(root).resolve()
    if not value.is_dir() or not (value / "Capability-Library" / "Registry.json").is_file():
        raise PluginBuildError("AIPM repository root is invalid")
    return value


def _capabilities(root: Path):
    core = root / "Core-Engine"
    if str(core) not in sys.path:
        sys.path.insert(0, str(core))
    from aipm_core.capabilities import CapabilityError, validate_registry  # noqa: PLC0415

    try:
        result = validate_registry(root)
    except CapabilityError as exc:
        raise PluginBuildError(str(exc)) from exc
    if result.get("status") != "PASS":
        raise PluginBuildError("Capability registry did not validate")
    catalog = _json(root / "Capability-Library" / "Registry.json")
    # `validate_registry` above verifies both the protected registry and its
    # provenance ledger. They deliberately have different schemas, so their
    # JSON documents must not be compared byte-for-byte here.
    return catalog


def load_profiles(root: Path | str = DEFAULT_ROOT) -> list[dict[str, Any]]:
    _root(root)
    profiles: list[dict[str, Any]] = []
    for path in sorted(PROFILES_ROOT.glob("*.json")):
        profile = _json(path)
        required = {"id", "display_name", "archive_prefix", "format_status", "runtime_status", "manifest_paths", "host_notes"}
        if not required.issubset(profile) or not isinstance(profile["manifest_paths"], list):
            raise PluginBuildError(f"Invalid host profile: {path.name}")
        if profile["format_status"] not in {"FORMAT_VERIFIED", "FORMAT_UNVERIFIED"}:
            raise PluginBuildError(f"Invalid host format status: {path.name}")
        profiles.append(profile)
    if {profile["id"] for profile in profiles} != {"chatgpt", "claude", "antigavity"}:
        raise PluginBuildError("Host profile inventory is incomplete")
    return profiles


def _profile(root: Path, name: str) -> dict[str, Any]:
    profiles = {item["id"]: item for item in load_profiles(root)}
    try:
        return profiles[name.casefold()]
    except KeyError as exc:
        raise PluginBuildError(f"Unknown Plugin platform: {name}") from exc


def _safe_relative(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise PluginBuildError(f"Unsafe package path: {value}")
    return path


def _copy_file(source: Path, destination: Path, expected_hash: str, output: bytes | None = None) -> None:
    if source.is_symlink() or not source.is_file():
        raise PluginBuildError(f"Source file is linked or unavailable: {source}")
    source_bytes = source.read_bytes()
    if _sha256_bytes(source_bytes) != expected_hash:
        raise PluginBuildError(f"Source hash mismatch: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if output is None:
        shutil.copy2(source, destination)
    else:
        destination.write_bytes(output)


def _chatgpt_skill_bytes(skill: dict[str, Any], source: Path) -> bytes:
    source_bytes = source.read_bytes()
    if source_bytes.startswith(b"---\n"):
        return source_bytes
    description = skill["description"].replace('"', '\\\\"')
    header = f'---\nname: {skill["slug"]}\ndescription: "{description}"\n---\n\n'.encode("utf-8")
    return header + source_bytes


def _distribution_skill_bytes(profile: dict[str, Any], skill: dict[str, Any], relative: str, source: Path) -> bytes | None:
    if profile["id"] == "chatgpt" and relative == "SKILL.md":
        return _chatgpt_skill_bytes(skill, source)
    return None


def _manifest_payload(profile: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "generated_by": "AIPM Multi-Host Plugin Builder",
        "plugin_id": f"aipm-{profile['id']}-capabilities",
        "display_name": f"AI Project Manager — {profile['display_name']}",
        "source_project_version": catalog["platform_version"],
        "source_commit_sha": catalog["source"]["commit_sha"],
        "status": "LOCAL_ARCHIVE_NOT_PUBLISHED_OR_INSTALLED",
        "format_status": profile["format_status"],
        "runtime_status": profile["runtime_status"],
        "personal_skills_included": False,
        "excluded_skills": sorted(EXCLUDED_SKILLS),
        "skill_count": len(catalog["skills"]),
        "standalone_prompt_count": len(catalog["standalone_prompts"]),
        "host_notes": profile["host_notes"],
    }


def _chatgpt_interface() -> dict[str, Any]:
    return {
        "displayName": "AI Project Manager",
        "shortDescription": "Project Management Skills",
        "longDescription": "Governed project-management workflows, Skills, and Prompts for AI-assisted project delivery.",
        "developerName": AUTHOR["name"],
        "category": "Business & Operations",
        "capabilities": ["Plan projects", "Manage tasks", "Create implementation handoffs", "Track project state", "Design terminal workflows"],
        "websiteURL": PROJECT_URL,
        "logo": "./assets/aipm-icon.svg",
        "composerIcon": "./assets/aipm-icon.svg",
    }


def _host_manifest(profile: dict[str, Any], catalog: dict[str, Any], path: str) -> dict[str, Any]:
    base = {
        "name": f"aipm-{profile['id']}-capabilities",
        "version": catalog["platform_version"],
        "description": "Approved AIPM project-management Skills and Prompts; it does not grant automatic local project access.",
    }
    if profile["id"] == "chatgpt":
        if path == "plugin.json":
            return {
                "$schema": CHATGPT_SCHEMA,
                **base,
                "homepage": PROJECT_URL,
                "repository": PROJECT_URL,
                "author": AUTHOR,
                "extensions": {"com.openai": {"interface": _chatgpt_interface()}},
            }
        return {**base, "homepage": PROJECT_URL, "repository": PROJECT_URL, "author": AUTHOR, "skills": "./skills/", "interface": _chatgpt_interface()}
    return {**base, "skills": "./skills/", "prompts": "./prompts/", "aipm_format_status": profile["format_status"]}


def _capability_index(catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "source_project_version": catalog["platform_version"],
        "skills": [{key: item[key] for key in ("slug", "name", "description", "version", "sha256", "skill_owned_prompts")} for item in catalog["skills"]],
        "standalone_prompts": catalog["standalone_prompts"],
        "exclusions": catalog["exclusions"],
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _materialize(root: Path, stage: Path, profile: dict[str, Any], catalog: dict[str, Any]) -> None:
    for skill in catalog["skills"]:
        slug = skill["slug"]
        if slug in EXCLUDED_SKILLS:
            raise PluginBuildError(f"Excluded Skill cannot be distributed: {slug}")
        source_root = root / _safe_relative(skill["path"])
        for relative, digest in skill["files"].items():
            source = source_root / _safe_relative(relative)
            _copy_file(source, stage / "skills" / slug / _safe_relative(relative), digest, _distribution_skill_bytes(profile, skill, relative, source))
    prompt_root = root / "02-Prompt-General"
    for prompt in catalog["standalone_prompts"]:
        source = root / _safe_relative(prompt["path"])
        target = stage / "prompts" / _safe_relative(str(Path(prompt["path"]).relative_to("02-Prompt-General")))
        _copy_file(source, target, prompt["sha256"])
    _copy_file(root / "LICENSE", stage / "licenses" / "Apache-2.0.txt", catalog["source"]["source_license_sha256"])
    _copy_file(root / "NOTICE", stage / "NOTICE", _sha256_bytes((root / "NOTICE").read_bytes()))
    _write_json(stage / "AIPM-Capability-Index.json", _capability_index(catalog))
    _write_json(stage / "AIPM-Distribution-Manifest.json", _manifest_payload(profile, catalog))
    for relative in profile["manifest_paths"]:
        _write_json(stage / _safe_relative(relative), _host_manifest(profile, catalog, relative))
    if profile["id"] == "chatgpt":
        icon = stage / "assets" / "aipm-icon.svg"
        icon.parent.mkdir(parents=True, exist_ok=True)
        icon.write_bytes(CHATGPT_ICON.encode("utf-8"))
    (stage / "VERSION").write_text(catalog["platform_version"] + "\n", encoding="utf-8")
    (stage / "README.md").write_text(
        f"# AI Project Manager {profile['display_name']}\n\n"
        "This local archive contains approved AIPM Skills and Prompts. It is not installed or published and does not grant automatic access to local AIPM projects.\n\n"
        f"Project Website: [{PROJECT_URL}]({PROJECT_URL})\n",
        encoding="utf-8",
    )


def _files(stage: Path) -> set[str]:
    return {path.relative_to(stage).as_posix() for path in stage.rglob("*") if path.is_file()}


def _expected_files(catalog: dict[str, Any], profile: dict[str, Any]) -> set[str]:
    expected = set(STATIC_FILES) | set(profile["manifest_paths"])
    if profile["id"] == "chatgpt":
        expected.update(CHATGPT_STATIC_FILES)
    for skill in catalog["skills"]:
        if skill["slug"] in EXCLUDED_SKILLS:
            raise PluginBuildError("Registry contains an excluded Skill")
        expected.update(f"skills/{skill['slug']}/{relative}" for relative in skill["files"])
    for prompt in catalog["standalone_prompts"]:
        relative = Path(prompt["path"]).relative_to("02-Prompt-General").as_posix()
        expected.add(f"prompts/{relative}")
    return expected


def _validate_stage(root: Path, stage: Path, profile: dict[str, Any], catalog: dict[str, Any]) -> None:
    actual = _files(stage)
    expected = _expected_files(catalog, profile)
    if actual != expected:
        raise PluginBuildError("Generated Plugin inventory is incomplete or contains unexpected files")
    manifest = _json(stage / "AIPM-Distribution-Manifest.json")
    if manifest != _manifest_payload(profile, catalog):
        raise PluginBuildError("Generated Plugin manifest drifted")
    index = _json(stage / "AIPM-Capability-Index.json")
    if index != _capability_index(catalog):
        raise PluginBuildError("Generated capability index drifted")
    for relative in profile["manifest_paths"]:
        if _json(stage / relative) != _host_manifest(profile, catalog, relative):
            raise PluginBuildError("Generated host manifest drifted")
    for skill in catalog["skills"]:
        for relative, digest in skill["files"].items():
            source = root / _safe_relative(skill["path"]) / _safe_relative(relative)
            expected_bytes = _distribution_skill_bytes(profile, skill, relative, source)
            actual = (stage / "skills" / skill["slug"] / relative).read_bytes()
            if actual != (source.read_bytes() if expected_bytes is None else expected_bytes):
                raise PluginBuildError(f"Generated Skill bytes drifted: {skill['slug']}")
    for prompt in catalog["standalone_prompts"]:
        relative = Path(prompt["path"]).relative_to("02-Prompt-General")
        if _sha256_file(stage / "prompts" / relative) != prompt["sha256"]:
            raise PluginBuildError(f"Generated Prompt bytes drifted: {prompt['name']}")


def _write_zip(stage: Path, destination: Path) -> None:
    temporary = destination.with_name(f".{destination.name}.tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted((item for item in stage.rglob("*") if item.is_file()), key=lambda item: item.relative_to(stage).as_posix()):
            entry = zipfile.ZipInfo(path.relative_to(stage).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    os.replace(temporary, destination)


def _write_sidecar(archive: Path) -> Path:
    sidecar = archive.with_name(archive.name + ".sha256")
    temporary = sidecar.with_name(f".{sidecar.name}.tmp")
    temporary.write_text(f"{_sha256_file(archive)}  {archive.name}\n", encoding="utf-8")
    os.replace(temporary, sidecar)
    return sidecar


def build_archives(root: Path | str, platforms: Iterable[str], output: Path | str | None = None) -> list[dict[str, Any]]:
    project_root = _root(root)
    catalog = _capabilities(project_root)
    output_root = Path(output).resolve() if output is not None else project_root / "Plugins" / "Dist"
    if output_root != project_root / "Plugins" / "Dist" and project_root not in output_root.parents:
        raise PluginBuildError("Plugin output must stay inside the AIPM repository")
    output_root.mkdir(parents=True, exist_ok=True)
    requested = list(dict.fromkeys(item.casefold() for item in platforms))
    if not requested:
        raise PluginBuildError("At least one Plugin platform is required")
    results = []
    workspace = project_root / ".test-workspace"
    workspace.mkdir(exist_ok=True)
    for name in requested:
        profile = _profile(project_root, name)
        with tempfile.TemporaryDirectory(prefix=f"plugin-{name}-", dir=workspace) as raw_stage:
            stage = Path(raw_stage)
            _materialize(project_root, stage, profile, catalog)
            _validate_stage(project_root, stage, profile, catalog)
            archive = output_root / f"{profile['archive_prefix']}-v{catalog['platform_version']}.zip"
            _write_zip(stage, archive)
            sidecar = _write_sidecar(archive)
        validate_archive(project_root, archive, name)
        results.append({"platform": name, "archive": archive, "sha256": sidecar, "format_status": profile["format_status"]})
    return results


def _read_sidecar(archive: Path) -> str:
    sidecar = archive.with_name(archive.name + ".sha256")
    try:
        digest, filename = sidecar.read_text(encoding="utf-8").strip().split("  ", 1)
    except (OSError, ValueError) as exc:
        raise PluginBuildError("Plugin checksum sidecar is invalid") from exc
    if filename != archive.name or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise PluginBuildError("Plugin checksum sidecar is invalid")
    return digest


def validate_archive(root: Path | str, archive: Path | str, platform: str) -> dict[str, Any]:
    project_root = _root(root)
    catalog = _capabilities(project_root)
    profile = _profile(project_root, platform)
    archive_path = Path(archive).resolve()
    if not archive_path.is_file() or project_root not in archive_path.parents:
        raise PluginBuildError("Plugin archive must be an existing file inside the AIPM repository")
    if _read_sidecar(archive_path) != _sha256_file(archive_path):
        raise PluginBuildError("Plugin archive checksum does not match its sidecar")
    with zipfile.ZipFile(archive_path) as package:
        infos = package.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or any(name.startswith("/") or ".." in Path(name).parts for name in names):
            raise PluginBuildError("Plugin archive contains unsafe paths")
        if any((item.external_attr >> 16) & 0o170000 == 0o120000 for item in infos):
            raise PluginBuildError("Plugin archive contains a linked file")
        if set(names) != _expected_files(catalog, profile):
            raise PluginBuildError("Plugin archive inventory does not match the approved catalog")
        manifest = json.loads(package.read("AIPM-Distribution-Manifest.json"))
        index = json.loads(package.read("AIPM-Capability-Index.json"))
        if manifest != _manifest_payload(profile, catalog) or index != _capability_index(catalog):
            raise PluginBuildError("Plugin archive metadata does not match the approved catalog")
        for relative in profile["manifest_paths"]:
            if json.loads(package.read(relative)) != _host_manifest(profile, catalog, relative):
                raise PluginBuildError("Plugin archive host manifest drifted")
        if profile["id"] == "chatgpt" and package.read("assets/aipm-icon.svg") != CHATGPT_ICON.encode("utf-8"):
            raise PluginBuildError("Plugin archive branding asset drifted")
        for skill in catalog["skills"]:
            for relative, digest in skill["files"].items():
                source = project_root / _safe_relative(skill["path"]) / _safe_relative(relative)
                expected_bytes = _distribution_skill_bytes(profile, skill, relative, source)
                actual = package.read(f"skills/{skill['slug']}/{relative}")
                if actual != (source.read_bytes() if expected_bytes is None else expected_bytes):
                    raise PluginBuildError(f"Plugin archive Skill hash mismatch: {skill['slug']}")
        for prompt in catalog["standalone_prompts"]:
            relative = Path(prompt["path"]).relative_to("02-Prompt-General").as_posix()
            if _sha256_bytes(package.read(f"prompts/{relative}")) != prompt["sha256"]:
                raise PluginBuildError(f"Plugin archive Prompt hash mismatch: {prompt['name']}")
    return {"status": "PASS", "platform": profile["id"], "format_status": profile["format_status"], "published": False, "installed": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build verified AIPM multi-host Plugin archives")
    parser.add_argument("--platform", action="append", choices=("chatgpt", "claude", "antigavity", "all"), required=True)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args(argv)
    try:
        platforms = [profile["id"] for profile in load_profiles(args.root)] if "all" in args.platform else args.platform
        if args.validate is not None:
            results = [validate_archive(args.root, args.validate, platform) for platform in platforms]
        else:
            results = build_archives(args.root, platforms, args.output)
        print(json.dumps([{key: str(value) if isinstance(value, Path) else value for key, value in result.items()} for result in results], ensure_ascii=False, sort_keys=True))
        return 0
    except PluginBuildError as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
