import pytest
from tempfile import TemporaryDirectory
from pathlib import Path

from spylt.builder import create_link
from tests.constants import PY_MODULE, SVELTE_MODULE

def write_mock_file(path, data):
    with open(path, "w") as fh:
        fh.write(data)

@pytest.mark.skip
def test_create_link():
    tempdir = Path(TemporaryDirectory().name)

    write_mock_file(tempdir / "App.py", PY_MODULE)
    write_mock_file(tempdir / "App.svelte", SVELTE_MODULE)

