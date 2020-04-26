# stdlib
import pathlib

# this package
import pyms_nist_search

repo_root = pathlib.Path(__file__).parent.parent.absolute()


FULL_PATH_TO_MAIN_LIBRARY = str(repo_root.parent / "mainlib")
FULL_PATH_TO_USER_LIBRARY = str(repo_root / "MoNA_GCMS_Library" / "MoNA")
FULL_PATH_TO_WORK_DIR = str(repo_root)

# TODO: tests with mainlib
# search = pyms_nist_search.Engine(
# 		FULL_PATH_TO_MAIN_LIBRARY,
# 		pyms_nist_search.NISTMS_MAIN_LIB,
# 		FULL_PATH_TO_WORK_DIR,
# 		debug=True,
# 		)

search = pyms_nist_search.Engine(
		FULL_PATH_TO_USER_LIBRARY,
		pyms_nist_search.NISTMS_USER_LIB,
		FULL_PATH_TO_WORK_DIR,
		debug=True,
		)
