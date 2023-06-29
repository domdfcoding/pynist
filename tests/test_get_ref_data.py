# 3rd party
from pyms.Spectrum import MassSpectrum  # type: ignore

# this package
from pyms_nist_search import ReferenceData, SearchResult

# this package
# from .engines import search
from .spectra import spectra


def test_get_ref_data(search):
	print()

	# To avoid duplicates for speed
	tested_locs = set()

	# perform a full search first to get some spec_loc values as they may change
	for name, spectrum in spectra.items():
		hit_list = search.full_spectrum_search(spectrum, n_hits=20)

		for hit in hit_list:
			assert isinstance(hit, SearchResult)
			assert isinstance(hit.spec_loc, int)
			if hit.spec_loc not in tested_locs:
				print(f"Testing spec_loc {hit.spec_loc}")

				ref_data = search.get_reference_data(hit.spec_loc)

				assert isinstance(ref_data, ReferenceData)
				assert isinstance(ref_data.mass_spec, MassSpectrum)

				tested_locs.add(hit.spec_loc)

		assert search.get_reference_data(hit_list[0].spec_loc).name.lower() == name.lower()
		# assert search.get_reference_data(hit_list[0].spec_loc).cas == cas
		print(search.get_reference_data(hit_list[0].spec_loc))
		print(dict(search.get_reference_data(hit_list[0].spec_loc)))
