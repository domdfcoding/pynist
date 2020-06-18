# stdlib
import json
import pickle

# 3rd party
import pytest  # type: ignore
import sdjson
from pyms.Spectrum import MassSpectrum  # type: ignore

# this package
from pyms_nist_search import PyNISTEncoder, ReferenceData, SearchResult

# this package
from .constants import (
		test_dictionary,
		test_float,
		test_int,
		test_list_ints,
		test_list_strs,
		test_lists,
		test_numbers,
		test_sequences,
		test_string,
		test_tuple
		)
from .engines import search
from .spectra import spectra

# Get SearchResult and ReferenceData for Diphenylamine
spectrum = spectra["Diphenylamine"]
hit, ref_data = search.full_search_with_ref_data(spectrum, n_hits=1)[0]

assert isinstance(hit, SearchResult)
assert isinstance(ref_data, ReferenceData)
assert isinstance(ref_data.mass_spec, MassSpectrum)

#
# search_res_json = (
# 			'{"name": "DIPHENYLAMINE", "cas": "---", "match_factor": 917, "reverse_match_factor": 927, "spec_loc": '
# 			'4305039, "hit_prob": 35.08}')

search_res_dict = {
		"name": "DIPHENYLAMINE",
		"cas": "---",
		"match_factor": 916,
		"reverse_match_factor": 926,
		"spec_loc": 1046408,
		"hit_prob": 35.43,
		}

search_res_json = json.dumps(search_res_dict)


def test_json_search_result():
	assert json.dumps(hit, cls=PyNISTEncoder) == search_res_json
	assert hit.to_json() == search_res_json
	assert SearchResult.from_json(hit.to_json()) == hit

	with pytest.raises(json.decoder.JSONDecodeError):
		ReferenceData.from_json(test_string)

	for obj in [
			test_int,
			test_float,
			test_list_ints,
			test_list_strs,
			test_dictionary,
			test_numbers,
			test_tuple,
			test_lists,
			test_sequences,
			]:
		print(obj)
		with pytest.raises(TypeError):
			SearchResult.from_json(obj)


def test_sdjson_search_result():
	assert sdjson.dumps(hit) == search_res_json


def test_dict():
	assert dict(hit) == hit.__dict__() == search_res_dict
	assert SearchResult.from_dict(dict(hit)) == hit
	#
	# with pytest.raises(json.decoder.JSONDecodeError):
	# 	ReferenceData.from_json(test_string)
	#
	for obj in [
			test_string,
			test_int,
			test_float,
			test_list_ints,
			test_list_strs,
			test_dictionary,
			test_numbers,
			test_tuple,
			test_lists,
			test_sequences,
			]:
		with pytest.raises(TypeError):
			SearchResult.from_dict(obj)


def test_str():
	assert str(hit) == repr(hit) == "Search Result: DIPHENYLAMINE 	(916)"


def test_eq():
	# TODO: make another search result to test equality to
	assert hit == hit

	for obj in [
			test_string,
			test_int,
			test_float,
			test_list_ints,
			test_list_strs,
			test_dictionary,
			test_numbers,
			test_tuple,
			test_lists,
			test_sequences,
			]:
		assert hit != obj

	assert hit != ref_data
	assert hit != ref_data.mass_spec


def test_pickle():
	reloaded_hit = pickle.loads(pickle.dumps(hit))
	assert isinstance(reloaded_hit, SearchResult)
	assert reloaded_hit == hit


def test_creation():
	SearchResult("Compound Name", 112233, 123, 456, 7.8, 999)
	SearchResult("Compound Name", "11-22-33", 12.3, 45.6, 78, 99.9)
