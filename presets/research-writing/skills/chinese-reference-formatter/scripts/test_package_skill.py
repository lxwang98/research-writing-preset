import json
import subprocess
import sys
from zipfile import ZipFile

import pytest

from package_skill import PACKAGE_FILES, package_skill


def test_package_is_portable_complete_and_reproducible(tmp_path):
    archive = package_skill(tmp_path)
    original = archive.read_bytes()
    with ZipFile(archive) as bundle:
        root = "chinese-reference-formatter-skill"
        assert set(bundle.namelist()) == {f"{root}/{path}" for path in PACKAGE_FILES}
        bundle.extractall(tmp_path / "installed")
    installed = tmp_path / "installed" / root
    payload = json.loads(
        (installed / "examples/metadata.json").read_text(encoding="utf-8")
    )
    proc = subprocess.run(
        [sys.executable, str(installed / "scripts/format_reference.py")],
        input=json.dumps(payload),
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    assert proc.stdout.strip() in (installed / "README.md").read_text(encoding="utf-8")
    assert package_skill(tmp_path).read_bytes() == original


def test_release_version_must_match_metadata(tmp_path):
    with pytest.raises(ValueError, match="does not match"):
        package_skill(tmp_path, "0.0.0")
    assert not list(tmp_path.glob("*.zip"))
