import pytest
import logging

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

@pytest.fixture(scope="session")
def pytestdb(request):
    db = PytestDb() # TODO: make sure db exists or throw error if can't be created
    yield db

def pytest_configure(config):
    # TODO: read config, read env
    pass

def pytest_addoption(parser: pytest.Parser):
    pass
