# stdlib
import pathlib

# 3rd party
from pyms_nist_search.utils import lib_name_from_path
import pytest
from pyms.Spectrum import MassSpectrum

# this package
import pyms_nist_search
from pyms_nist_search import SearchResult
from pyms_nist_search.reference_data import ReferenceData

repo_root = pathlib.Path(__file__).parent.parent.absolute()

FULL_PATH_TO_MONA_LIBRARY = str(repo_root / "MoNA_GCMS_Library" / "MoNA")
FULL_PATH_TO_C1_LIBRARY = str(repo_root / "test_multi_library" / "c1")
FULL_PATH_TO_C2_LIBRARY = str(repo_root / "test_multi_library" / "c2")
FULL_PATH_TO_C3_LIBRARY = str(repo_root / "test_multi_library" / "c3")
FULL_PATH_TO_C4_LIBRARY = str(repo_root / "test_multi_library" / "c4")
FULL_PATH_TO_C5_LIBRARY = str(repo_root / "test_multi_library" / "c5")
FULL_PATH_TO_WORK_DIR = str(repo_root)


def test_c1_c2_51():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		spectrum = MassSpectrum([51.0], [27])

		hit_list = engine.full_spectrum_search(spectrum, n_hits=5)
		hit_list_names = [hit.name for hit in hit_list]

		assert len(hit_list) == 2

		for hit in hit_list:
			# TODO: test CAS numbers
			assert isinstance(hit, SearchResult)

		print(hit_list)
		print(hit_list_names)
		assert "1-NITROPYRENE" in hit_list_names
		assert "2,4-DINITROPHENOL" in hit_list_names
		assert "3,4-DICHLOROPHENOL" not in hit_list_names
		assert "2,5-DICHLOROPHENOL" not in hit_list_names
		assert "2,6-DICHLOROPHENOL" not in hit_list_names

		assert hit_list_names == ["1-NITROPYRENE", "2,4-DINITROPHENOL"]
		lib_paths = engine.get_lib_paths()
		assert lib_name_from_path(lib_paths[hit_list[0].lib_idx]) == "c1"
		assert lib_name_from_path(lib_paths[hit_list[1].lib_idx]) == "c2"


def test_all_51():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C4_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		spectrum = MassSpectrum([51.0], [27])

		hit_list = engine.full_spectrum_search(spectrum, n_hits=5)
		hit_list_names = [hit.name for hit in hit_list]

		assert len(hit_list) == 4

		for hit in hit_list:
			# TODO: test CAS numbers
			assert isinstance(hit, SearchResult)

		print(hit_list)
		print(hit_list_names)
		assert "1-NITROPYRENE" in hit_list_names
		assert "2,4-DINITROPHENOL" in hit_list_names
		assert "3,4-DICHLOROPHENOL" in hit_list_names
		assert "2,5-DICHLOROPHENOL" in hit_list_names
		assert "2,6-DICHLOROPHENOL" not in hit_list_names

		assert hit_list_names == ["1-NITROPYRENE", "2,4-DINITROPHENOL", "2,5-DICHLOROPHENOL", "3,4-DICHLOROPHENOL"]

		lib_paths = engine.get_lib_paths()
		assert lib_name_from_path(lib_paths[hit_list[0].lib_idx]) == "c1"
		assert lib_name_from_path(lib_paths[hit_list[1].lib_idx]) == "c2"
		assert lib_name_from_path(lib_paths[hit_list[2].lib_idx]) == "c4"
		assert lib_name_from_path(lib_paths[hit_list[3].lib_idx]) == "c3"


def test_all_53():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C4_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		spectrum = MassSpectrum([53.0], [64])

		hit_list = engine.full_spectrum_search(spectrum, n_hits=5)
		hit_list_names = [hit.name for hit in hit_list]

		assert len(hit_list) == 3

		for hit in hit_list:
			# TODO: test CAS numbers
			assert isinstance(hit, SearchResult)

		print(hit_list)
		print(hit_list_names)
		assert "1-NITROPYRENE" not in hit_list_names
		assert "2,4-DINITROPHENOL" not in hit_list_names
		assert "3,4-DICHLOROPHENOL" in hit_list_names
		assert "2,5-DICHLOROPHENOL" in hit_list_names
		assert "2,6-DICHLOROPHENOL" in hit_list_names

		assert hit_list_names == ["2,5-DICHLOROPHENOL", "3,4-DICHLOROPHENOL", "2,6-DICHLOROPHENOL"]

		lib_paths = engine.get_lib_paths()
		assert lib_name_from_path(lib_paths[hit_list[0].lib_idx]) == "c4"
		assert lib_name_from_path(lib_paths[hit_list[1].lib_idx]) == "c3"
		assert lib_name_from_path(lib_paths[hit_list[2].lib_idx]) == "c5"


def test_full_search_with_ref_data():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C4_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		spectrum = MassSpectrum([53.0], [64])

		hits = engine.full_search_with_ref_data(spectrum, n_hits=5)

		assert len(hits) == 3

		for hit in hits:
			# TODO: test CAS numbers
			assert isinstance(hit[0], SearchResult)
			assert isinstance(hit[1], ReferenceData)

		assert hit[0].name == "2,6-DICHLOROPHENOL"

		assert hit[1].name == "2,6-DICHLOROPHENOL"
		# assert hit[1].cas == "95-77-2"  # Not supported by lib2nist it seems

		ref_data_dict = hit[1].to_dict()
		assert hit[1].name == "2,6-DICHLOROPHENOL"
		# CAS not supported by LIB2NIST
		assert hit[1].formula == "C6H4Cl2O"
		assert hit[1].nist_no == 5
		assert hit[1].id == '1'
		assert hit[1].lib_idx == 4
		engine.get_lib_paths()[hit[1].lib_idx] == FULL_PATH_TO_C5_LIBRARY
		assert isinstance(hit[1].mass_spec, MassSpectrum)


@pytest.mark.xfail()
def test_c1_c2_cas():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		hit_list = engine.cas_search("51-28-5")

		assert len(hit_list) == 1
		assert isinstance(hit_list[0], SearchResult)

		assert hit_list[0].name == "2,4-DINITROPHENOL"


@pytest.mark.xfail()
def test_all_cas_c4():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C4_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		hit_list = engine.cas_search("583-78-8")

		assert len(hit_list) == 1

		assert isinstance(hit_list[0], SearchResult)
		assert hit_list[0].name == "2,5-DICHLOROPHENOL"


@pytest.mark.xfail()
def test_all_cas_c2():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C4_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		hit_list = engine.cas_search("51-28-5")

		assert len(hit_list) == 1

		assert isinstance(hit_list[0], SearchResult)
		assert hit_list[0].name == "2,4-DINITROPHENOL"


# TODO: spectrum_search, get_reference_data

# def test_different_n_hits(search: pyms_nist_search.Engine, spectra: Tuple[str, Optional[MassSpectrum]]):
# 	print()

# 	name, spectrum = spectra
# 	if name != "Diphenylamine":
# 		pytest.skip()

# 	for n_hits in range(1, 21):
# 		print(f"Testing with {n_hits} hits")
# 		hit_list = search.full_spectrum_search(spectrum, n_hits=n_hits)

# 		assert len(hit_list) == n_hits


@pytest.mark.xfail()
def test_cas_single_library():
	# Make sure it works with these "fake" libraries

	with pyms_nist_search.Engine(
			[(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB)],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		print()

		hit_list = engine.cas_search("51-28-5")

		assert len(hit_list) == 1
		assert isinstance(hit_list[0], SearchResult)

		assert hit_list[0].name == "2,4-DINITROPHENOL"


def test_get_active_libs():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C4_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		active_libs = engine.get_active_libs()
		assert active_libs[0] == 1
		assert active_libs[1] == 2
		assert active_libs[2] == 3
		assert active_libs[3] == 4
		assert active_libs[4] == 5

		for pos in active_libs[5:]:
			assert pos == 0


def test_get_lib_paths():
	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C4_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C2_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		lib_paths = engine.get_lib_paths()
		assert len(lib_paths) == 5
		assert lib_name_from_path(lib_paths[0]) == "c5"
		assert lib_name_from_path(lib_paths[1]) == "c4"
		assert lib_name_from_path(lib_paths[2]) == "c3"
		assert lib_name_from_path(lib_paths[3]) == "c2"
		assert lib_name_from_path(lib_paths[4]) == "c1"

	with pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_C1_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C3_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					(FULL_PATH_TO_C5_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			) as engine:

		lib_paths = engine.get_lib_paths()
		assert len(lib_paths) == 3
		assert lib_name_from_path(lib_paths[0]) == "c1"
		assert lib_name_from_path(lib_paths[1]) == "c3"
		assert lib_name_from_path(lib_paths[2]) == "c5"
