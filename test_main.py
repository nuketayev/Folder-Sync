import os
import pytest
import shutil
import hashlib
import tempfile
from main import checksum, sync_folders

@pytest.fixture
def temp_dir():
    dir = tempfile.mkdtemp()
    yield dir
    shutil.rmtree(dir)

def test_checksum_md5(temp_dir):
    file_path = os.path.join(temp_dir, "test_file.txt")
    with open(file_path, "w") as f:
        f.write("test content")
    expected_md5 = hashlib.md5(b"test content").hexdigest()
    assert checksum(file_path, "MD5") == expected_md5

def test_checksum_sha256(temp_dir):
    file_path = os.path.join(temp_dir, "test_file.txt")
    with open(file_path, "w") as f:
        f.write("test content")
    expected_sha256 = hashlib.sha256(b"test content").hexdigest()
    assert checksum(file_path, "SHA256") == expected_sha256

def test_sync_copies_files(temp_dir):
    source_dir = os.path.join(temp_dir, "source")
    replica_dir = os.path.join(temp_dir, "replica")
    os.makedirs(source_dir)
    os.makedirs(replica_dir)

    file1_path = os.path.join(source_dir, "file1.txt")
    file2_path = os.path.join(source_dir, "file2.txt")
    with open(file1_path, "w") as f:
        f.write("content1")
    with open(file2_path, "w") as f:
        f.write("content2")

    sync_folders(source_dir, replica_dir, "SHA256")

    # Verify files exist in replica
    assert os.path.exists(os.path.join(replica_dir, "file1.txt"))
    assert os.path.exists(os.path.join(replica_dir, "file2.txt"))

    # Verify file content
    with open(os.path.join(replica_dir, "file1.txt"), "r") as f:
        assert f.read() == "content1"
    with open(os.path.join(replica_dir, "file2.txt"), "r") as f:
        assert f.read() == "content2"

def test_sync_updates_modified_files(temp_dir):
    source_dir = os.path.join(temp_dir, "source")
    replica_dir = os.path.join(temp_dir, "replica")
    os.makedirs(source_dir)
    os.makedirs(replica_dir)

    file1_path = os.path.join(source_dir, "file1.txt")
    with open(file1_path, "w") as f:
        f.write("original content")

    sync_folders(source_dir, replica_dir, "SHA256")

    with open(file1_path, "w") as f:
        f.write("updated content")

    sync_folders(source_dir, replica_dir, "SHA256")

    # Verify that the file in replica was updated
    with open(os.path.join(replica_dir, "file1.txt"), "r") as f:
        assert f.read() == "updated content"

def test_sync_removes_deleted_files(temp_dir):
    source_dir = os.path.join(temp_dir, "source")
    replica_dir = os.path.join(temp_dir, "replica")
    os.makedirs(source_dir)
    os.makedirs(replica_dir)

    file1_path = os.path.join(source_dir, "file1.txt")
    with open(file1_path, "w") as f:
        f.write("some content")

    sync_folders(source_dir, replica_dir, "SHA256")

    os.remove(file1_path)

    sync_folders(source_dir, replica_dir, "SHA256")

    # Verify the file was removed from replica
    assert not os.path.exists(os.path.join(replica_dir, "file1.txt"))
