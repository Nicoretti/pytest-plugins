def test_something(storage):
    name = "somefile.txt" 
    with open(name, 'w') as f:
        for i in range(0,100):
            f.write(f"Line {i}\n")
    storage.save(name)
    assert True

