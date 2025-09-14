import pytest


@pytest.fixture
def testfile(tmp_path):
    file = tmp_path / "testfile.txt"
    with open(file, "w") as f:
        for i in range(0, 3):
            f.write(f"Line {i}\n")
    yield file


def test_smoke_pytestdb(pytestdb):
    assert True


def test_smokie_session_storage(session_storage, testfile):
    session_storage.save('testfile.txt', testfile)
    assert True


def test_smokie_test_storage(storage, testfile):
    storage.save('testfile.txt', testfile)
    assert True
