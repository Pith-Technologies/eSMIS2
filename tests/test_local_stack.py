"""Tests for the shared local development stack.

Every worktree of this repository must use ONE Docker Compose project, so
local users, configuration and data survive creating a new worktree or
switching between worktrees. Compose otherwise names the project after the
directory, which gave every worktree its own empty database and filestore.
"""

import importlib.machinery
import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
COMPOSE_FILE = ROOT_DIR / "docker-compose.yml"


@pytest.fixture
def esmis(monkeypatch):
    """Import the ./esmis CLI (no .py suffix) as a module, free of the shell's Compose override."""
    monkeypatch.delenv("COMPOSE_PROJECT_NAME", raising=False)
    loader = importlib.machinery.SourceFileLoader("esmis_cli", str(ROOT_DIR / "esmis"))
    spec = importlib.util.spec_from_loader("esmis_cli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def inspect_output(*mounts):
    """A `docker inspect` listing with one container carrying the given (Destination, Source) mounts."""
    return json.dumps([{"Id": "abc", "Mounts": [{"Destination": d, "Source": s, "Type": "bind"} for d, s in mounts]}])


class TestComposeProjectName:
    def test_compose_file_fixes_the_project_name(self):
        compose = yaml.safe_load(COMPOSE_FILE.read_text())
        assert (
            compose.get("name") == "esmis2"
        ), "docker-compose.yml must pin the project name; worktrees share one stack"

    def test_cli_and_compose_file_agree_on_the_name(self, esmis):
        compose = yaml.safe_load(COMPOSE_FILE.read_text())
        assert esmis.COMPOSE_PROJECT == compose["name"]

    def test_empty_override_falls_back_like_compose_does(self, monkeypatch):
        monkeypatch.setenv("COMPOSE_PROJECT_NAME", "")
        loader = importlib.machinery.SourceFileLoader("esmis_cli_empty", str(ROOT_DIR / "esmis"))
        spec = importlib.util.spec_from_loader("esmis_cli_empty", loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        assert module.COMPOSE_PROJECT == "esmis2"

    def test_volumes_are_named_not_bound_to_a_directory(self):
        compose = yaml.safe_load(COMPOSE_FILE.read_text())
        assert set(compose["volumes"]) == {"postgres_data", "odoo_data"}

    def test_every_odoo_service_mounts_the_worktree_at_the_addons_path(self, esmis):
        compose = yaml.safe_load(COMPOSE_FILE.read_text())
        for service in esmis.ODOO_SERVICES:
            mounts = compose["services"][service]["volumes"]
            assert any(m.startswith(f".:{esmis.ADDONS_MOUNT}") for m in mounts), service


class TestServedDir:
    def test_reports_the_source_of_the_addons_mount(self, esmis):
        out = inspect_output(("/var/lib/odoo", "/vol/odoo_data"), (esmis.ADDONS_MOUNT, "/work/feat-x"))
        assert esmis._served_dir_from_inspect(out) == Path("/work/feat-x")

    def test_none_without_the_addons_mount(self, esmis):
        assert esmis._served_dir_from_inspect(inspect_output(("/var/lib/odoo", "/vol/odoo_data"))) is None

    def test_none_on_empty_or_invalid_output(self, esmis):
        assert esmis._served_dir_from_inspect("") is None
        assert esmis._served_dir_from_inspect("not json") is None
        assert esmis._served_dir_from_inspect(json.dumps({"Id": "not-a-list"})) is None
        assert esmis._served_dir_from_inspect(json.dumps(["not-a-dict"])) is None


class TestIsThisWorktree:
    def test_same_directory_through_a_symlink(self, esmis, tmp_path, monkeypatch):
        real = tmp_path / "real"
        real.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real)
        monkeypatch.setattr(esmis, "PROJECT_ROOT", real.resolve())
        assert esmis._is_this_worktree(link)

    def test_another_directory(self, esmis, tmp_path, monkeypatch):
        (tmp_path / "a").mkdir()
        (tmp_path / "b").mkdir()
        monkeypatch.setattr(esmis, "PROJECT_ROOT", tmp_path / "a")
        assert not esmis._is_this_worktree(tmp_path / "b")

    def test_removed_directory_is_not_this_one(self, esmis, tmp_path, monkeypatch):
        monkeypatch.setattr(esmis, "PROJECT_ROOT", tmp_path)
        assert not esmis._is_this_worktree(tmp_path / "gone")
