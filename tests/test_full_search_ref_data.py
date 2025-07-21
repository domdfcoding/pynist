# stdlib
from typing import Optional, Tuple

# 3rd party
from pyms.Spectrum import MassSpectrum

# this package
import pyms_nist_search
from pyms_nist_search import ReferenceData, SearchResult
from pyms_nist_search.utils import lib_name_from_path

# this package
from .engines import FULL_PATH_TO_USER_LIBRARY


def test_full_search(search: pyms_nist_search.Engine, spectra: Tuple[str, Optional[MassSpectrum]]):
	print()

	name, spectrum = spectra
	print(f"Testing {name}")
	hit_list = search.full_search_with_ref_data(spectrum, n_hits=5)

	assert len(hit_list) == 5

	for hit, ref_data in hit_list:
		# TODO: test CAS numbers
		assert isinstance(hit, SearchResult)
		assert isinstance(ref_data, ReferenceData)
		assert isinstance(ref_data.mass_spec, MassSpectrum)

	# if hit_list[0][0].name.lower() == name.lower():
	# 	assert hit_list[0][1].name.lower() == name.lower()
	# else:
	# 	assert name.lower() in hit_list[0][1].synonyms
	assert hit_list[0][0].name.lower() == name.lower()
	assert hit_list[0][1].name.lower() == name.lower()

	assert hit_list[0][1].lib_idx == 0
	assert lib_name_from_path(search.get_lib_paths()[hit_list[0][1].lib_idx]) == "MoNA"


def test_different_n_hits(search: pyms_nist_search.Engine, spectra: Tuple[str, Optional[MassSpectrum]]):
	print()

	spectrum = spectra[1]

	for n_hits in range(1, 21):
		print(f"Testing with {n_hits} hits")
		hit_list = search.full_search_with_ref_data(spectrum, n_hits=n_hits)

		assert len(hit_list) == n_hits
