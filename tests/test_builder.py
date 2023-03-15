import pytest
from tempfile import TemporaryDirectory
from pathlib import Path
import subprocess

from spylt.builder import create_link, create_html
import spylt

from tests.constants import PY_MODULE, SVELTE_MODULE


def write_mock_file(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)


def test_create_link():
    with TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir)
        write_mock_file(tempdir / "App.py", PY_MODULE(tempdir=tempdir))
        write_mock_file(tempdir / "App.svelte", SVELTE_MODULE)
        create_link(f"{tempdir / 'App.py'}:app", tempdir / "main.js")
        assert (tempdir / "main.js").exists()

        cat_node = subprocess.run(
            ["cat", str(tempdir / "main.js")], stdout=subprocess.PIPE, check=True
        )
        error_output = None
        try:
            subprocess.run(
                ["node", "--input-type=module"],
                input=cat_node.stdout.decode("utf-8"),
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as err:
            error_output = err.stderr
        # Check if Node complains about .svelte file extension
        # which indicates a syntactically correct JS file
        assert "node:internal/errors:490" in error_output

def test_create_html(capsys):
    with TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir)
        assert tempdir.exists()
        write_mock_file(tempdir / "App.py", PY_MODULE(tempdir=tempdir))
        write_mock_file(tempdir / "App.svelte", SVELTE_MODULE)
        create_link(f"{tempdir / 'App.py'}:app", tempdir / "main.js")
    rollup_text = (Path(spylt.__file__).parent / "rollup.config.txt")
    assert rollup_text.exists()
    write_mock_file(tempdir / "rollup.config.js", "")
    write_mock_file(tempdir / "rollup.config.js", rollup_text.read_text("utf-8"))
    create_html(tempdir / "index.html", tempdir / "main.js")
    assert (tempdir / "index.html").exists()