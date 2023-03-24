import os

import pytest

import data_storage

TEST_DIRECTORY = f"test_directory"
REAL_FILE = f"{TEST_DIRECTORY}/real_file.txt"
FAKE_FILE = f"{TEST_DIRECTORY}/fake_file.txt"


def create_real_file():
    if not os.path.exists(TEST_DIRECTORY):
        os.makedirs(TEST_DIRECTORY)
    with open(REAL_FILE, "w", encoding="utf8") as f:
        f.write("This is a test that will be uploaded")


def cleanup():
    os.remove(REAL_FILE)
    os.rmdir(TEST_DIRECTORY)
    assert data_storage.s3.delete(REAL_FILE)


def test_upload():
    # real upload file
    create_real_file()
    assert data_storage.s3.upload(REAL_FILE)
    files = data_storage.s3.files_in_bucket(TEST_DIRECTORY)
    assert REAL_FILE in files

    # fake upload file
    assert not data_storage.s3.upload(FAKE_FILE)

    cleanup()


def test_download():
    # upload real file
    create_real_file()
    assert data_storage.s3.upload(REAL_FILE)
    files = data_storage.s3.files_in_bucket(TEST_DIRECTORY)
    assert REAL_FILE in files

    # download real file
    os.remove(REAL_FILE)
    assert data_storage.s3.download(REAL_FILE)
    assert os.path.isfile(REAL_FILE)

    # download fake file
    assert not data_storage.s3.download(FAKE_FILE)

    cleanup()


def test_files_in_bucket():

    # no files in bucket
    assert not data_storage.s3.files_in_bucket(TEST_DIRECTORY)

    # upload real file
    create_real_file()
    assert data_storage.s3.upload(REAL_FILE)
    files = data_storage.s3.files_in_bucket(TEST_DIRECTORY)
    assert REAL_FILE in files

    cleanup()
