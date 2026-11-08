#!/usr/bin/env python3
"""Inspect a local Apple-silicon VirtualMac IPSW for Henge/Monterey experiments.

This is a metadata preflight only. It does not validate Apple's TSS signing,
restore authorization, firmware compatibility, or successful boot.
"""
from __future__ import annotations

import argparse
import plistlib
import sys
import zipfile
from pathlib import Path
from typing import Any

EXPECTED_PRODUCT = "VirtualMac2,1"
MANIFEST_NAME = "BuildManifest.plist"


class IPSWError(Exception):
    pass


def _find_strings(value: Any, key: str) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key and isinstance(v, str):
                found.append(v)
            found.extend(_find_strings(v, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(_find_strings(item, key))
    return found


def inspect_ipsw(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise IPSWError(f"File not found: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise IPSWError(f"Corrupt ZIP member: {bad_member}")
            try:
                raw = archive.read(MANIFEST_NAME)
            except KeyError as exc:
                raise IPSWError(f"{MANIFEST_NAME} is missing") from exc
    except zipfile.BadZipFile as exc:
        raise IPSWError("Not a valid IPSW/ZIP archive") from exc

    try:
        manifest = plistlib.loads(raw)
    except Exception as exc:
        raise IPSWError(f"Cannot parse {MANIFEST_NAME}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise IPSWError("BuildManifest root is not a dictionary")

    product_version = str(manifest.get("ProductVersion", "unknown"))
    build_version = str(manifest.get("ProductBuildVersion", "unknown"))
    product_types = sorted(set(_find_strings(manifest, "ProductType")))
    device_classes = sorted(set(_find_strings(manifest, "DeviceClass")))
    identity_count = len(manifest.get("BuildIdentities", [])) if isinstance(manifest.get("BuildIdentities"), list) else 0

    version_parts = product_version.split(".")
    is_monterey = bool(version_parts and version_parts[0] == "12")
    has_vmapple_identity = EXPECTED_PRODUCT in product_types or EXPECTED_PRODUCT in device_classes
    return {
        "path": str(path),
        "product_version": product_version,
        "build_version": build_version,
        "product_types": product_types,
        "device_classes": device_classes,
        "build_identity_count": identity_count,
        "is_monterey": is_monterey,
        "has_vmapple_identity": has_vmapple_identity,
        "metadata_candidate": is_monterey and has_vmapple_identity and identity_count > 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ipsw", type=Path, help="Path to a locally stored .ipsw")
    args = parser.parse_args()
    try:
        result = inspect_ipsw(args.ipsw)
    except IPSWError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"IPSW: {result['path']}")
    print(f"ProductVersion: {result['product_version']}")
    print(f"ProductBuildVersion: {result['build_version']}")
    print(f"Build identities: {result['build_identity_count']}")
    print(f"ProductType values: {', '.join(result['product_types']) or '(none found)'}")
    print(f"DeviceClass values: {', '.join(result['device_classes']) or '(none found)'}")
    if result["metadata_candidate"]:
        print("RESULT: Monterey VirtualMac metadata candidate.")
    elif not result["is_monterey"]:
        print("RESULT: Not a macOS 12 (Monterey) image.")
    elif not result["has_vmapple_identity"]:
        print("RESULT: No VirtualMac2,1 identity found; not a Henge restore candidate.")
    else:
        print("RESULT: Incomplete restore metadata; inspect BuildManifest manually.")
    print("LIMIT: This does NOT establish that Apple's TSS will sign/personalize this build.")
    print("LIMIT: This does NOT prove AVPBooter/device/CPU compatibility or successful boot.")
    return 0 if result["metadata_candidate"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
