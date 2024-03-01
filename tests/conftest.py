# stdlib
from typing import Iterator

# 3rd party
import pytest

# this package
import pyms_nist_search

# this package
from .engines import FULL_PATH_TO_USER_LIBRARY, FULL_PATH_TO_WORK_DIR


@pytest.fixture(scope="session")
def search() -> Iterator[pyms_nist_search.Engine]:
	with pyms_nist_search.Engine(
			FULL_PATH_TO_USER_LIBRARY,
			pyms_nist_search.NISTMS_USER_LIB,
			FULL_PATH_TO_WORK_DIR,  # debug=True,
			) as engine:
		yield engine
