# stdlib
import pathlib
from typing import Optional, Tuple

# 3rd party
import pytest
from pyms.Spectrum import MassSpectrum

# this package
import pyms_nist_search
from pyms_nist_search import SearchResult

repo_root = pathlib.Path(__file__).parent.parent.absolute()

FULL_PATH_TO_MONA_LIBRARY = str(repo_root / "MoNA_GCMS_Library" / "MoNA")
FULL_PATH_TO_C1_LIBRARY = str(repo_root / "test_multi_library" / "c1")
FULL_PATH_TO_C2_LIBRARY = str(repo_root / "test_multi_library" / "c2")
FULL_PATH_TO_WORK_DIR = str(repo_root)


def test_mona_and_extra_lib():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		spectrum = MassSpectrum([51.0], [27])

		
		hit_list = engine.full_spectrum_search(spectrum, n_hits=5)
		hit_list_names = [hit.name for hit in hit_list]
	
		# assert len(hit_list) == 5

		for hit in hit_list:
			# TODO: test CAS numbers
			assert isinstance(hit, SearchResult)

		assert "1-NITROPYRENE" in hit_list_names


# def test_different_n_hits(search: pyms_nist_search.Engine, spectra: Tuple[str, Optional[MassSpectrum]]):
# 	print()

# 	name, spectrum = spectra
# 	if name != "Diphenylamine":
# 		pytest.skip()

# 	for n_hits in range(1, 21):
# 		print(f"Testing with {n_hits} hits")
# 		hit_list = search.full_spectrum_search(spectrum, n_hits=n_hits)

# 		assert len(hit_list) == n_hits
