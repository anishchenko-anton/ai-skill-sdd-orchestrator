#!/usr/bin/env python3
"""
verify_release_gate.py
Automated Pre-Completion Checklist Gate verification script.
Ensures that any changes to backend source files are synchronously accompanied
by updates in the versioning triad (version.json, package.json, CHANGELOG.md)
and that versions match exactly.

Usage:
    python verify_release_gate.py [--root <project_root>] [--strict]
"""

import os
import sys
import json
import argparse
import subprocess
import re

def get_git_modified_files(root_dir):
    """Returns list of modified, added or staged files relative to root."""
    try:
        cmd = ["git", "status", "--porcelain"]
        result = subprocess.run(cmd, cwd=root_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        files = []
        for line in result.stdout.strip().splitlines():
            if not line.strip():
                continue
            # status is 2 chars + space + file path (or old -> new path)
            status_part = line[:2]
            path_part = line[3:].strip()
            if " -> " in path_part:
                path_part = path_part.split(" -> ")[1].strip()
            files.append(path_part.replace("\\", "/"))
        return files
    except Exception as e:
        print(f"[Warning] Could not get git status: {e}", file=sys.stderr)
        return []

def check_gate(root_dir, backend_prefix="backend/", version_json_path="version.json", backend_pkg_path="backend/package.json", changelog_path="CHANGELOG.md"):
    print("=" * 60)
    print("🔒 RUNNING PRE-COMPLETION CHECKLIST GATE VERIFICATION")
    print("=" * 60)

    modified_files = get_git_modified_files(root_dir)
    print(f"📁 Total modified/staged files detected: {len(modified_files)}")

    backend_modified = [f for f in modified_files if f.startswith(backend_prefix) or "/backend/" in f]
    
    # Exclude release artifacts themselves from triggering backend check if they are in backend/
    backend_code_modified = [f for f in backend_modified if not f.endswith("package.json") and not f.endswith("package-lock.json")]

    if not backend_code_modified:
        print("✅ Filter check: No functional backend files were modified.")
        print("ℹ️ Version bump is optional (UI-only or non-backend changes).")
        print("🔒 GATE STATUS: PASSED (Non-backend scope)")
        return True

    print(f"⚠️ Backend changes detected ({len(backend_code_modified)} files):")
    for f in backend_code_modified[:5]:
        print(f"   - {f}")
    if len(backend_code_modified) > 5:
        print(f"   ... and {len(backend_code_modified) - 5} more files")

    errors = []

    # 1. Check version.json
    full_vjson = os.path.join(root_dir, version_json_path)
    vjson_version = None
    if not os.path.exists(full_vjson):
        errors.append(f"Missing '{version_json_path}' at project root.")
    else:
        try:
            with open(full_vjson, 'r', encoding='utf-8') as f:
                vdata = json.load(f)
                vjson_version = vdata.get("version")
                if not vjson_version:
                    errors.append(f"Field 'version' is empty in '{version_json_path}'.")
                release_notes = vdata.get("releaseNotes", [])
                if not release_notes:
                    errors.append(f"'releaseNotes' is missing or empty in '{version_json_path}'.")
        except Exception as e:
            errors.append(f"Failed to parse '{version_json_path}': {e}")

    # 2. Check backend package.json
    full_pkg = os.path.join(root_dir, backend_pkg_path)
    pkg_version = None
    if not os.path.exists(full_pkg):
        # Check root package.json if backend/package.json does not exist
        full_pkg = os.path.join(root_dir, "package.json")
    
    if os.path.exists(full_pkg):
        try:
            with open(full_pkg, 'r', encoding='utf-8') as f:
                pdata = json.load(f)
                pkg_version = pdata.get("version")
        except Exception as e:
            errors.append(f"Failed to parse '{backend_pkg_path}': {e}")
    else:
        errors.append(f"Missing package.json for backend at '{backend_pkg_path}'.")

    # 3. Synchronize versions between version.json and package.json
    if vjson_version and pkg_version:
        if vjson_version != pkg_version:
            errors.append(f"Version mismatch: '{version_json_path}' has '{vjson_version}', but package.json has '{pkg_version}'. They must be identical!")
        else:
            print(f"✅ Version synchronization: '{vjson_version}' matches across version.json and package.json.")

    # 4. Check CHANGELOG.md
    full_changelog = os.path.join(root_dir, changelog_path)
    if not os.path.exists(full_changelog):
        errors.append(f"Missing '{changelog_path}' at project root.")
    else:
        try:
            with open(full_changelog, 'r', encoding='utf-8') as f:
                content = f.read()
                if vjson_version and vjson_version not in content:
                    errors.append(f"CHANGELOG.md does not contain an entry for current version '{vjson_version}'.")
                else:
                    print(f"✅ CHANGELOG.md contains release entry for version '{vjson_version}'.")
        except Exception as e:
            errors.append(f"Failed to read '{changelog_path}': {e}")

    # Check git diff inclusion
    if version_json_path not in modified_files and any(f.endswith("version.json") for f in modified_files) is False:
        errors.append(f"'{version_json_path}' was not modified in the current working copy/commit.")

    print("-" * 60)
    if errors:
        print("❌ PRE-COMPLETION GATE FAILED! BLOCKED BY REASON(S):")
        for err in errors:
            print(f"   ⛔ {err}")
        print("\n💡 ACTION REQUIRED: Update version.json, package.json, and CHANGELOG.md before marking task as complete!")
        print("=" * 60)
        return False
    else:
        print("✅ ALL PRE-COMPLETION INVARIANTS PASSED SUCCESSFULLY!")
        print("🔒 GATE STATUS: UNLOCKED FOR COMPLETION")
        print("=" * 60)
        return True

def main():
    parser = argparse.ArgumentParser(description="Pre-Completion Checklist Gate Verifier")
    parser.add_argument("--root", default=".", help="Root directory of the project")
    parser.add_argument("--backend-prefix", default="backend/", help="Path prefix for backend files")
    parser.add_argument("--version-json", default="version.json", help="Relative path to version.json")
    parser.add_argument("--package-json", default="backend/package.json", help="Relative path to backend package.json")
    parser.add_argument("--changelog", default="CHANGELOG.md", help="Relative path to CHANGELOG.md")

    args = parser.parse_args()
    passed = check_gate(
        root_dir=os.path.abspath(args.root),
        backend_prefix=args.backend_prefix,
        version_json_path=args.version_json,
        backend_pkg_path=args.package_json,
        changelog_path=args.changelog
    )

    sys.exit(0 if passed else 1)

if __name__ == '__main__':
    main()
