# stdlib
from typing import Optional, Tuple

# 3rd party
import pytest
from pyms.Spectrum import MassSpectrum

# this package
import pyms_nist_search
from pyms_nist_search import SearchResult
from pyms_nist_search.utils import lib_name_from_path


def test_full_search(search: pyms_nist_search.Engine, spectra: Tuple[str, Optional[MassSpectrum]]):
	print()

	name, spectrum = spectra
	print(f"Testing {name}")
	hit_list = search.full_spectrum_search(spectrum, n_hits=5)

	assert len(hit_list) == 5

	for hit in hit_list:
		# TODO: test CAS numbers
		assert isinstance(hit, SearchResult)

	assert hit_list[0].name.lower() == name.lower()
	lib_paths = search.get_lib_paths()
	assert lib_name_from_path(lib_paths[hit_list[0].lib_idx]) == "MoNA"
	# assert hit_list[0].cas == cas


def test_different_n_hits(search: pyms_nist_search.Engine, spectra: Tuple[str, Optional[MassSpectrum]]):
	print()

	name, spectrum = spectra
	if name != "Diphenylamine":
		pytest.skip()

	for n_hits in range(1, 21):
		print(f"Testing with {n_hits} hits")
		hit_list = search.full_spectrum_search(spectrum, n_hits=n_hits)

		assert len(hit_list) == n_hits
