import logging
import subprocess

import pytest

from efi_family_app.utils import ExampleReadsApp

@pytest.fixture
def process():
    return subprocess.Popen(
        ["echo", "hello world"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def test_process(process):
    logging.info("Running a test")
    assert 1 == 1
