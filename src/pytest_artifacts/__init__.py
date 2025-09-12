from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import pytest
import logging
from contextlib import contextmanager

_logger = logging.getLogger(__name__)


class Storage:

    def __init__(self, path, parent=None):
        self._path = path

    @property
    def path(self):
        return self._path

    @contextmanager
    def open(self, path, mode='w'):
        path = self.path / path
        path.parent.mkdir(exist_ok=True)
        file = open(path, mode)
        try:
            yield file
        finally:
            if file:
                file.close()

    def save(self, file: Path):
        file = Path(file)
        dest = self._path / file.name
        if dest.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
        _logger.debug(f"Saving artifact '%s' to '%s'", file, dest)
        shutil.copy(file, dest)

    def sub_storage(self, path):
        return Storage(self._path / path, parent=self)


@pytest.fixture(scope="session")
def session_storage(request, tmp_path_factory):
    storage_path = tmp_path_factory.mktemp("storage")
    _logger.debug("Creating storage folder '%s'", storage_path)

    yield Storage(storage_path)

    name = f"Test-Artifacts-{datetime.now()}"
    archive = shutil.make_archive(
        base_name=name, format="zip", root_dir=storage_path)
    _logger.debug("Storing compressed artifacts in '%s'", archive)


@pytest.fixture
def storage(request, session_storage):
    yield session_storage.sub_storage(request.node.nodeid)


def pytest_addoption(parser: pytest.Parser):
    artifacts = parser.getgroup("artifacts")
    path = Path.cwd() / f"{datetime.now()}"
    artifacts.addoption(
        "--artifacts-path",
        type=Path,
        help=f"Path to store the artifacts zip to [default: {path}]"
    )
    artifacts.addoption(
        "--artifacts-archive-format",
        choices=["zip", "tar.gz"],
        default="zip",
        help="Path to store the artifacts zip to"
    )
