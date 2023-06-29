# 3rd party
from pyms.Spectrum import MassSpectrum  # type: ignore

# this package
from pyms_nist_search import ReferenceData, SearchResult

# this package
# from .engines import search
from .spectra import spectra


def test_full_search(search):
	print()

	for name, spectrum in spectra.items():
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


def test_different_n_hits(search):
	print()

	spectrum = spectra["Diphenylamine"]

	for n_hits in range(1, 21):
		print(f"Testing with {n_hits} hits")
		hit_list = search.full_search_with_ref_data(spectrum, n_hits=n_hits)

		assert len(hit_list) == n_hits
