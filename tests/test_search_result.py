# stdlib
import json
import pickle

# 3rd party
import pytest
import sdjson
from pyms.Spectrum import MassSpectrum  # type: ignore

# this package
from pyms_nist_search import ReferenceData, SearchResult

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
# from .engines import search
from .spectra import spectra


@pytest.fixture()
def reference_data(search):

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

	return {
			"search_res_json": search_res_json,
			"search_res_dict": search_res_dict,
			"hit": hit,
			"ref_data": ref_data,
			}


def test_json_search_result(reference_data):
	assert sdjson.dumps(reference_data["hit"]) == reference_data["search_res_json"]
	assert reference_data["hit"].to_json() == reference_data["search_res_json"]
	assert SearchResult.from_json(reference_data["hit"].to_json()) == reference_data["hit"]

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


def test_sdjson_search_result(reference_data):
	assert sdjson.dumps(reference_data["hit"]) == reference_data["search_res_json"]


def test_dict(reference_data):
	assert dict(reference_data["hit"]) == reference_data["hit"].to_dict() == reference_data["search_res_dict"]
	assert SearchResult.from_dict(dict(reference_data["hit"])) == reference_data["hit"]
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
			SearchResult.from_dict(obj)  # type: ignore


def test_str(reference_data):
	assert str(reference_data["hit"]) == repr(reference_data["hit"]) == "Search Result: DIPHENYLAMINE \t(916)"


def test_eq(reference_data):
	# TODO: make another search result to test equality to
	assert reference_data["hit"] == reference_data["hit"]

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
		assert reference_data["hit"] != obj

	assert reference_data["hit"] != reference_data["ref_data"]
	assert reference_data["hit"] != reference_data["ref_data"].mass_spec


def test_pickle(reference_data):
	reloaded_hit = pickle.loads(pickle.dumps(reference_data["hit"]))  # nosec: B301
	assert isinstance(reloaded_hit, SearchResult)
	assert reloaded_hit == reference_data["hit"]


def test_creation():
	SearchResult("Compound Name", 112233, 123, 456, 7.8, 999)
	SearchResult("Compound Name", "11-22-33", 12.3, 45.6, 78, 99.9)
