from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

import pytest


class Storage:

    def __init__(self, path):
        self._path = path

    def save(self, file: Path):
        file = Path(file)
        dest = self._path / file.name
        if dest.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(file, dest)

    def sub_storage(self, path):
        return Storage(self._path / path)


@pytest.fixture(scope="session")
def session_storage(request):
    yield Storage(request.config.option.artifacts_path)


@pytest.fixture
def storage(request, session_storage):
    yield session_storage.sub_storage(request.node.nodeid)


def pytest_addoption(parser: pytest.Parser):
    artifacts = parser.getgroup("artifacts")
    default_storage = Path.cwd() / f"{datetime.now()}"
    artifacts.addoption(
        "--artifacts-path",
        type=Path,
        default=default_storage,
        help=f"Path to store the artifacts [default: {default_storage}]"
    )


def pytest_configure(config: pytest.Config):
    artifact_path = config.option.artifacts_path
    artifact_path.mkdir(exist_ok=True)
