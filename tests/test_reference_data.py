# stdlib
import json
import pathlib
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

	intensity_list = [  # yapf: disable  # noqa: E122
		13, 6, 8, 37, 23, 71, 15, 7, 25, 16, 47, 45, 7, 10, 9, 9, 10,
		61, 13, 51, 14, 10, 6, 10, 9, 6, 4, 5, 10, 4, 26, 7, 5, 5, 13,
		4, 5, 16, 12, 27, 16, 10, 12, 27, 178, 329, 999, 137, 8,
		]

	mass_list = [  # yapf: disable  # noqa: E122
		18, 28, 38, 39, 50, 51, 52, 62, 63, 64, 65, 66, 71, 72, 74, 75,
		76, 77, 78, 84, 85, 89, 90, 91, 92, 93, 102, 103, 104, 114, 115,
		116, 117, 127, 128, 129, 130, 139, 140, 141, 142, 143, 154, 166,
		167, 168, 169, 170, 171,
		]

	ref_data_dict = {
			"name": "DIPHENYLAMINE",
			"cas": "0-0-0",
			"formula": "C12H11N",
			"contributor": "MASS SPECTROSCOPY SOC. OF JAPAN (MSSJ)",
			"nist_no": 5698,
			"id": "5319",
			"mw": 169,
			"exact_mass": 169.0,
			"synonyms": [],
			"mass_spec": {
					"intensity_list": intensity_list,
					"mass_list": mass_list,
					},
			}

	ref_data_dict_non_recursive = {
			"name": "DIPHENYLAMINE",
			"cas": "0-0-0",
			"formula": "C12H11N",
			"contributor": "MASS SPECTROSCOPY SOC. OF JAPAN (MSSJ)",
			"nist_no": 5698,
			"id": "5319",
			"mw": 169,
			"exact_mass": 169.0,
			"synonyms": [],
			"mass_spec": ref_data.mass_spec,
			}

	ref_data_json = json.dumps(ref_data_dict)

	return {
			"ref_data_dict_non_recursive": ref_data_dict_non_recursive,
			"ref_data_json": ref_data_json,
			"hit": hit,
			"ref_data": ref_data,
			"ref_data_dict": ref_data_dict,
			}


def test_json_ref_data(reference_data):
	assert sdjson.dumps(reference_data["ref_data"]) == reference_data["ref_data_json"]
	assert reference_data["ref_data"].to_json() == reference_data["ref_data_json"]
	assert ReferenceData.from_json(reference_data["ref_data"].to_json()) == reference_data["ref_data"]

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
			ReferenceData.from_json(obj)  # type: ignore


def test_sdjson_ref_data(reference_data):
	assert sdjson.dumps(reference_data["ref_data"]) == reference_data["ref_data_json"]


def test_dict(reference_data):
	assert dict(reference_data["ref_data"]
				) == reference_data["ref_data"].to_dict() == reference_data["ref_data_dict_non_recursive"]
	assert sdjson.loads(sdjson.dumps(reference_data["ref_data"])) == reference_data["ref_data_dict"]
	assert ReferenceData.from_dict(dict(reference_data["ref_data"])) == reference_data["ref_data"]

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
			ReferenceData.from_dict(obj)  # type: ignore


def test_str(reference_data):
	assert str(reference_data["ref_data"]
				) == repr(reference_data["ref_data"]) == "Reference Data: DIPHENYLAMINE \t(0-0-0)"


def test_eq(reference_data):
	# TODO: make another search result to test equality to
	assert reference_data["ref_data"] == reference_data["ref_data"]

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
		assert reference_data["ref_data"] != obj

	assert reference_data["ref_data"] != reference_data["hit"]
	assert reference_data["ref_data"] != reference_data["ref_data"].mass_spec


def test_pickle(reference_data):
	reloaded_ref_data = pickle.loads(pickle.dumps(reference_data["ref_data"]))  # nosec: B301
	assert isinstance(reloaded_ref_data, ReferenceData)
	assert reloaded_ref_data == reference_data["ref_data"]


def test_creation():
	ReferenceData(
			name="Compound Name",
			cas=112233,
			nist_no=123,
			id=456,
			mw=7.8,
			)


def test_from_jcamp():
	# TODO: main bit

	# Errors
	for obj in [123, 12.3, (12, 34), set(), dict(), list()]:
		with pytest.raises(TypeError):
			ReferenceData.from_jcamp(obj)  # type: ignore

	with pytest.raises(FileNotFoundError):
		ReferenceData.from_jcamp("non-existant_file.jdx")

	with pytest.raises(FileNotFoundError):
		ReferenceData.from_jcamp(pathlib.Path("non-existant_file.jdx"))


# TODO: from_mona_dict
# TODO: to_msp
