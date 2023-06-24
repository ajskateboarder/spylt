"""Test building functions that are used for modules"""
from tempfile import TemporaryDirectory
from pathlib import Path
import subprocess
import runpy
import ast
import os

import spylt
from spylt.module import Module
from spylt import builder
from spylt.cli.helpers import REQUIREMENTS

from tests.constants import PY_MODULE, SVELTE_MODULE


def write_mock_file(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)


def test_create_link():
    """Test if `create_link()` creates a proper App initializer"""
    with TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir)
        write_mock_file(tempdir / "App.py", PY_MODULE(tempdir=tempdir))
        write_mock_file(tempdir / "App.svelte", SVELTE_MODULE)
        linker_code = builder.create_link(f"{tempdir / 'App.py'}:app")

        error_output = None
        try:
            subprocess.run(
                ["node", "--input-type=module"],
                input=linker_code,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as err:
            error_output = err.stderr
        # Check if Node complains about .svelte file extension in linker
        # which indicates a syntactically correct JS file
        assert "node:internal/errors:490" in error_output


def test_create_html():
    """Test if `create_html()` correctly compiles Svelte and bundles to HTML/CSS/JS"""
    with TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir)
        write_mock_file(tempdir / "App.py", PY_MODULE(tempdir=tempdir))
        write_mock_file(tempdir / "App.svelte", SVELTE_MODULE)
        linker_code = builder.create_link(f"{tempdir / 'App.py'}:app")
        rollup_config = (Path(spylt.__file__).parent / "rollup.config.txt").read_text(
            "utf-8"
        )
        with open(tempdir / "rollup.config.js", "w", encoding="utf-8") as fh:
            fh.write(rollup_config)
        assert (tempdir / "rollup.config.js").exists()
        os.chdir(tempdir)

        subprocess.call(["npm", "init", "--y"])
        subprocess.call(["npm", "install", *REQUIREMENTS])

        html = builder.create_html(linker_code)
        # Check if JavaScript compiled correctly
        assert "var app=function()" in html


def test__create_api():
    """Test if inner `create_api()` returns correct function information and converts code"""
    with TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir)
        write_mock_file(tempdir / "App.py", PY_MODULE(tempdir=tempdir))
        # Required to import the module with runpy
        write_mock_file(tempdir / "App.svelte", SVELTE_MODULE)
        module: Module = runpy.run_path(str(tempdir / "App.py"))["app"]

        _, source, _, imports = builder._create_api(  # pylint:disable=W0212
            module._apis, tempdir / "App.py"  # pylint:disable=W0212
        )
        assert len(imports) == 0
        assert len(source.values()) == 1
        # Check if the generated code has the same return value
        # should convert something like f"Hello {name}" to {"response": f"Hello {name}"}
        return_obj = (
            list(source.values())[0][0].strip().split(" ", 1)[1].split(" ", 1)[1][:-1]
        )
        assert return_obj in PY_MODULE(tempdir=tempdir)


def test_create_api():
    """Test if `create_api()` produces a syntactically correct API"""
    with TemporaryDirectory() as _tempdir:
        tempdir = Path(_tempdir)
        write_mock_file(tempdir / "App.py", PY_MODULE(tempdir=tempdir))
        # Required to import the module with runpy
        write_mock_file(tempdir / "App.svelte", SVELTE_MODULE)
        module: Module = runpy.run_path(str(tempdir / "App.py"))["app"]
        api_string = builder.create_api(
            module._apis, tempdir / "App.py"  # pylint:disable=W0212
        )
        assert ast.parse(api_string)
