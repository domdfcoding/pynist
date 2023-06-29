# this package
from pyms_nist_search import SearchResult

# this package
# from .engines import search
from .spectra import spectra


def test_quick_search(search):
	print()

	for name, spectrum in spectra.items():
		print(f"Testing {name}")
		hit_list = search.spectrum_search(spectrum, n_hits=5)

		assert len(hit_list) == 5

		for hit in hit_list:
			# TODO: test CAS numbers
			assert isinstance(hit, SearchResult)

		# Special case for MEK
		if name.lower() == "2-butanone":
			assert hit_list[0].name.lower() in {
					"2-butanone",
					"butanone",
					"ethyl methyl ketone",
					"methyl ethyl ketone",
					}
		else:
			assert hit_list[0].name.lower() == name.lower()
		# assert hit_list[0].cas == cas


def test_different_n_hits(search):
	print()

	spectrum = spectra["Diphenylamine"]

	for n_hits in range(1, 21):
		print(f"Testing with {n_hits} hits")
		hit_list = search.spectrum_search(spectrum, n_hits=n_hits)

		assert len(hit_list) == n_hits
