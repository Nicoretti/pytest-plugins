from __future__ import annotations

from datetime import datetime
import pytest
import logging
import sqlite3
from inspect import cleandoc
from pathlib import Path

_logger = logging.getLogger(__name__)


class PytestDb:
    default_name = "pytest.db"

    # add plugin mechanism for init hook of tables for db
    def __init__(self, path=Path.cwd(), name=None):
        default_name = name or self.default_name
        self._db = path / default_name
        _logger.debug("Creating database in %s", self._db)
        #self._db.touch(exist_ok=True)

    @property
    def path(self):
        return self._db


class Session:
    """Represents a pytest test run session"""

    @staticmethod
    def create_table(db):
        with sqlite3.connect(db) as con:
            query = cleandoc(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id integer primary key,
                    start text
                );
                """
            )
            result = con.execute(query)
            return result

    @staticmethod
    def session_id(db):
        with sqlite3.connect(db) as con:
            query = "SELECT id FROM sessions ORDER BY id desc LIMIT 1;"
            result = con.execute(query).fetchone()
            if result:
                return result[0]
            return None

    @staticmethod
    def next_session_id(db):
        current_id = Session.session_id(db)
        next_id = 1 if current_id is None else current_id + 1
        return next_id

    @staticmethod
    def new(db):
        """Creates a new session with a new session id"""
        with sqlite3.connect(db) as con:
            start = f'{datetime.now()}'
            query = "INSERT INTO sessions (id, start) VALUES (?, ?);"
            result = con.execute(query, (Session.next_session_id(db), start))
            return result

    def __init__(self, db: Path):
        self._db = db


class Artifact:

    @staticmethod
    def create_table(db):
        with sqlite3.connect(db) as con:
            query = cleandoc(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    id integer primary key,
                    session integer not null,
                    test_id text,
                    name text,
                    data blob,
                    foreign key (session) REFERENCES sessions(id)
                );
                """
            )
            result = con.execute(query)
            return result

    def __init__(self, db):
        self._db = db

    def save(self, name, file):
        with sqlite3.connect(self._db) as con:
            file = Path(file)
            query = "INSERT INTO artifacts (session, name, data) VALUES (?, ?, ?);"
            session = Session(self._db)
            result = con.execute(
                query,
                (session.session_id(self._db), name, file.read_bytes()))
            return result.lastrowid


class TestArtifact:

    def __init__(self, db, test_id):
        self._test_id = test_id
        self._db = db

    def save(self, name, file):
        with sqlite3.connect(self._db) as con:
            file = Path(file)
            query = "INSERT INTO artifacts (session, test_id, name, data) VALUES (?, ?, ?, ?);"
            session = Session(self._db)
            result = con.execute(
                query,
                (session.session_id(self._db), self._test_id, name, file.read_bytes()))
            return result.lastrowid


@pytest.fixture(scope="session")
def pytestdb(request):
    db = PytestDb()
    Session.create_table(db.path)  # make sure new session is created
    yield db


@pytest.fixture(scope="session")
def session_storage(request, pytestdb):
    Session.new(pytestdb.path)
    Artifact.create_table(pytestdb.path)
    yield Artifact(pytestdb.path)


@pytest.fixture()
def storage(request, pytestdb):
    Artifact.create_table(pytestdb.path)
    test_id = request.node.nodeid
    yield TestArtifact(pytestdb.path, test_id)


def pytest_configure(config):
    pass

def pytest_sessionfinish(session):
    # TODO: save each session artifact to zip/tar file based on config parameters
    pass


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
