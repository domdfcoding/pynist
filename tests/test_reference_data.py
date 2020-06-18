# stdlib
import json
import pathlib
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

ref_data_dict = {
		"name": "DIPHENYLAMINE",
		"cas": "0-0-0",
		"formula": "C12H11N",
		"contributor": 'MASS SPECTROSCOPY SOC. OF JAPAN (MSSJ)',
		"nist_no": 5698,
		"id": "5319",
		"mw": 169,
		"exact_mass": 169.0,
		"synonyms": [],
		"mass_spec": {
				"intensity_list": [
						13, 6, 8, 37, 23, 71, 15, 7, 25, 16, 47, 45, 7, 10, 9, 9, 10,
						61, 13, 51, 14, 10, 6, 10, 9, 6, 4, 5, 10, 4, 26, 7, 5, 5, 13,
						4, 5, 16, 12, 27, 16, 10, 12, 27, 178, 329, 999, 137, 8,
						],
				"mass_list": [
						18, 28, 38, 39, 50, 51, 52, 62, 63, 64, 65, 66, 71, 72, 74, 75,
						76, 77, 78, 84, 85, 89, 90, 91, 92, 93, 102, 103, 104, 114, 115,
						116, 117, 127, 128, 129, 130, 139, 140, 141, 142, 143, 154, 166,
						167, 168, 169, 170, 171,
						],
				},
		}

ref_data_dict_non_recursive = {
		"name": "DIPHENYLAMINE",
		"cas": "0-0-0",
		"formula": "C12H11N",
		"contributor": 'MASS SPECTROSCOPY SOC. OF JAPAN (MSSJ)',
		"nist_no": 5698,
		"id": "5319",
		"mw": 169,
		"exact_mass": 169.0,
		"synonyms": [],
		"mass_spec": ref_data.mass_spec,
		}

ref_data_json = json.dumps(ref_data_dict)


def test_json_ref_data():
	assert json.dumps(ref_data, cls=PyNISTEncoder) == ref_data_json
	assert ref_data.to_json() == ref_data_json
	assert ReferenceData.from_json(ref_data.to_json()) == ref_data

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
		with pytest.raises(TypeError):
			ReferenceData.from_json(obj)


def test_sdjson_ref_data():
	assert sdjson.dumps(ref_data) == ref_data_json


def test_dict():
	assert dict(ref_data) == ref_data.__dict__() == ref_data_dict_non_recursive
	assert ref_data.__dict__(recursive=True) == ref_data_dict
	assert ReferenceData.from_dict(dict(ref_data)) == ref_data

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
			test_lists,
			]:
		with pytest.raises(TypeError):
			ReferenceData.from_dict(obj)


def test_str():
	assert str(ref_data) == repr(ref_data) == "Reference Data: DIPHENYLAMINE 	(0-0-0)"


def test_eq():
	# TODO: make another search result to test equality to
	assert ref_data == ref_data

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
		assert ref_data != obj

	assert ref_data != hit
	assert ref_data != ref_data.mass_spec


def test_pickle():
	reloaded_ref_data = pickle.loads(pickle.dumps(ref_data))
	assert isinstance(reloaded_ref_data, ReferenceData)
	assert reloaded_ref_data == ref_data


def test_creation():
	ReferenceData("Compound Name", 112233, 123, 456, 7.8, 999)
	ReferenceData("Compound Name", "11-22-33", 12.3, 45.6, 78, 99.9)


def test_from_jcamp():
	# TODO: main bit

	# Errors
	for obj in [123, 12.3, (12, 34), set(), dict(), list()]:
		with pytest.raises(TypeError):
			ReferenceData.from_jcamp(obj)

	with pytest.raises(FileNotFoundError):
		ReferenceData.from_jcamp("non-existant_file.jdx")

	with pytest.raises(FileNotFoundError):
		ReferenceData.from_jcamp(pathlib.Path("non-existant_file.jdx"))


# TODO: from_mona_dict
# TODO: to_msp
