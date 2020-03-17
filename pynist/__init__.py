from . import _core
from ._core import *
abc = "abc"

from .search_result import SearchResult
from .reference_data import ReferenceData

def pack(spectrum, top=20):
	"""
	Convert the spectrum data into a string.
	:param spectrum:
	:type spectrum:
	:param top:
	:type top:
	:return:
	:rtype:
	"""
	spectrum.sort(key=lambda s: s[1], reverse=True)
	norm = spectrum[0][1]
	
	spectrum = [(a, 999.0 * b / norm) for (a, b) in spectrum[:top]]
	spectrum.sort()
	return "*".join(["%.2f\t%.2f" % (a, b) for (a, b) in spectrum]) + "*"


def full_spectrum_search(mass_spec):
	values = list(zip(mass_spec.mass_list, mass_spec.intensity_list))
	
	hit_list = _core.full_spectrum_search(pack(values, len(values)))

	parsed_hit_list = []
	
	for hit in hit_list:
		parsed_hit_list.append(SearchResult.from_pynist(hit))
		
	return parsed_hit_list


def get_spectrum_by_loc(spec_loc):
	reference_data = _core.get_spectrum_by_loc(spec_loc)
	
	return ReferenceData.from_pynist(reference_data)

# TODO: Search by Name. See page 13 of the documentation.
#  Would also like to search by CAS number but DLL doesn't seem to support that
