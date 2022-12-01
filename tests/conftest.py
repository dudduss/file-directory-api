from fastapi.testclient import TestClient
import pytest
import os
from main import app
import shutil


@pytest.fixture(scope="function")
def client():
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


@pytest.fixture(scope="function", autouse=True)
def create_and_remove_test_directory():
    """
    Creates the following directory structure for testing:
    test_root/
        rootFile.txt
        .hiddenRootFile.txt
        subdir1/
            subdir1File.txt
            subdir2/
                subdir2File.txt
    """

    os.mkdir("test_root")

    with open("test_root/rootFile.txt", "w") as f:
        f.write("rootFile")

    with open("test_root/.hiddenRootFile.txt", "w") as f:
        f.write("hiddenRootFile")

    os.mkdir("test_root/subdir1")

    with open("test_root/subdir1/subdir1File.txt", "w") as f:
        f.write("subdir1File")

    os.mkdir("test_root/subdir1/subdir2")

    with open("test_root/subdir1/subdir2/subdir2File.txt", "w") as f:
        f.write("subdir2File")

    yield
    shutil.rmtree("test_root")
