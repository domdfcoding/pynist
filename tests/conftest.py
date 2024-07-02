# stdlib
import pathlib
from typing import Iterator

# 3rd party
import pytest
import requests

# this package
import pyms_nist_search
from pyms_nist_search import ReferenceData

# this package
from .engines import FULL_PATH_TO_USER_LIBRARY, FULL_PATH_TO_WORK_DIR


@pytest.fixture(scope="session")
def search() -> Iterator[pyms_nist_search.Engine]:
	with pyms_nist_search.Engine(
			FULL_PATH_TO_USER_LIBRARY,
			pyms_nist_search.NISTMS_USER_LIB,
			FULL_PATH_TO_WORK_DIR,  # debug=True,
			) as engine:
		yield engine


@pytest.fixture(
		scope="session",
		params=[
				"122-39-4",
				"71-43-2",
				"107-10-8",  # "50-37-3",  # LSD, shows up under synonym  # yapf: ignore
				"57-13-6",
				# "77-92-9", citric acid, shows up as diisopropyl malonate
				# "118-96-7", tnt, being detected as n-sec-butyl-2,4-dinitrobenzenamine
				# "67-66-3",  # Chloroform, detected as trichloromethane (synonym)
				# "‎106-24-1",  # Geraniol, being detected as 3,7-dimethyl-2,6-octadien-1-ol(trans)
				# "121-14-2",  # 2,4-DNT	need to fix synonyms
				"507-70-0",  # Borneol
				"78-93-3",  # MEK
				]
		)
def spectra(request):
	# Download required files from NIST Webbook
	nist_data_dir = pathlib.Path("nist_jdx_files")

	if not nist_data_dir.exists():
		nist_data_dir.mkdir(parents=True)

	cas = request.param
	jcamp_file = nist_data_dir / f"{cas}.jdx"

	if not jcamp_file.exists():
		url = f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C{cas.replace('-', '')}&Index=0&Type=Mass"
		r = requests.get(url)
		if r.status != 200:
			# Try once more
			r = requests.get(url)
			r.raise_for_status()
		jcamp_file.write_bytes(r.content)

	# Read ReferenceData from Jcamp File
	ref_data = ReferenceData.from_jcamp(jcamp_file)

	# Fix for borneol
	if ref_data.cas == "507-70-0":
		return "Borneol", ref_data.mass_spec
	else:
		return ref_data.name, ref_data.mass_spec
