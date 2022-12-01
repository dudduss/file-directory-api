import os
from pwd import getpwuid

"""
Test that contents of root directory are correctly returned.
"""


def test_get_root_dir(client):
    response = client.get("")
    owner = getpwuid(os.stat("test_root").st_uid).pw_name
    assert response.status_code == 200
    assert response.json() == {
        "pathType": "dir",
        "fullPath": "test_root/",
        "contents": [
            {
                "name": ".hiddenRootFile.txt",
                "type": "file",
                "hidden": True,
                "fullPath": "test_root/.hiddenRootFile.txt",
                "size": 14,
                "owner": owner,
                "permissions": "0o100644",
            },
            {
                "name": "subdir1",
                "type": "directory",
            },
            {
                "name": "rootFile.txt",
                "type": "file",
                "hidden": False,
                "fullPath": "test_root/rootFile.txt",
                "size": 8,
                "owner": owner,
                "permissions": "0o100644",
            },
        ],
    }


"""
Test that contents of a file in root directory are correctly returned.
"""


def test_get_root_file(client):
    response = client.get("/?path=rootFile.txt")
    assert response.status_code == 200
    assert response.json() == {
        "pathType": "file",
        "fullPath": "test_root/rootFile.txt",
        "contents": "rootFile",
    }


"""
Test that contents of a hidden file are correctly returned.
"""


def test_get_hidden_root_file(client):
    response = client.get("/?path=.hiddenRootFile.txt")
    assert response.status_code == 200
    assert response.json() == {
        "pathType": "file",
        "fullPath": "test_root/.hiddenRootFile.txt",
        "contents": "hiddenRootFile",
    }


"""
Test that contents of subdirectory are correctly returned.
"""


def test_get_subdir1(client):
    response = client.get("/?path=subdir1")
    owner = getpwuid(os.stat("test_root").st_uid).pw_name
    assert response.status_code == 200
    assert response.json() == {
        "pathType": "dir",
        "fullPath": "test_root/subdir1",
        "contents": [
            {
                "name": "subdir2",
                "type": "directory",
            },
            {
                "name": "subdir1File.txt",
                "type": "file",
                "hidden": False,
                "fullPath": "test_root/subdir1/subdir1File.txt",
                "size": 11,
                "owner": owner,
                "permissions": "0o100644",
            },
        ],
    }


"""
Tests that contents of a file in a subdirectory are correctly returned.
"""


def test_get_subdir1_file(client):
    response = client.get("/?path=subdir1/subdir1File.txt")
    assert response.status_code == 200
    assert response.json() == {
        "pathType": "file",
        "fullPath": "test_root/subdir1/subdir1File.txt",
        "contents": "subdir1File",
    }


"""
Test that contents of subdirectory two levels deep are correctly returned.
"""


def test_get_subdir2(client):
    response = client.get("/?path=subdir1/subdir2")
    owner = getpwuid(os.stat("test_root").st_uid).pw_name
    assert response.status_code == 200
    assert response.json() == {
        "pathType": "dir",
        "fullPath": "test_root/subdir1/subdir2",
        "contents": [
            {
                "name": "subdir2File.txt",
                "type": "file",
                "hidden": False,
                "fullPath": "test_root/subdir1/subdir2/subdir2File.txt",
                "size": 11,
                "owner": owner,
                "permissions": "0o100644",
            },
        ],
    }


"""
Test that an error is thrown when trying to get a directory that does not exist.
"""


def test_get_nonexistent_dir(client):
    response = client.get("/?path=nonexistent")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Path 'nonexistent' not found",
    }


"""
Test that an error is thrown when a file in a known directory is not found.
"""


def test_get_nonexistent_file_in_existent_dir(client):
    response = client.get("/?path=subdir1/nonexistent.txt")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Path 'subdir1/nonexistent.txt' not found",
    }
