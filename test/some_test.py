import pytest


@pytest.fixture
def testfile(tmp_path):
    file = tmp_path / "testfile.txt"
    with open(file, "w") as f:
        for i in range(0, 3):
            f.write(f"Line {i}\n")
    yield file


def test_something(storage, testfile):
    storage.save(testfile)
    assert True


def test_something2(storage):
    from inspect import cleandoc
    with storage.open("somefile2.txt", "w") as f:
        content = cleandoc(
            """
            Line 1
            Line 2
            Line 3
            """
        )
        f.write(content)
    assert True
