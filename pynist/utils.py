# stdlib
import json
import urllib.parse

# 3rd party
from pyms.Spectrum import MassSpectrum

# this package
from .search_result import SearchResult
from .reference_data import ReferenceData


def quote_mass_spec(mass_spec):
	"""
	
	:param mass_spec:
	:type mass_spec: pyms.Spectrum.MassSpectrum
	:return:
	:rtype:
	"""
	
	if not isinstance(mass_spec, MassSpectrum):
		raise ValueError("`mass_spec` must be a `pyms.Spectrum.MassSpectrum` object")
	
	return urllib.parse.quote(json.dumps(dict(mass_spec)))


def unquote_mass_spec(string):
	json_data = urllib.parse.unquote(string)
	data_dict = json.loads(json_data)

	return MassSpectrum.from_dict(data_dict)


class PyNISTEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, (SearchResult, ReferenceData, MassSpectrum)):
			return dict(o)
		else:
			json.JSONEncoder.default(self, o)
