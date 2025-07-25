# stdlib
import pathlib
from typing import Optional, Tuple

# 3rd party
import pytest
import requests
from pyms.Spectrum import MassSpectrum

# this package
from pyms_nist_search import ReferenceData


@pytest.fixture(
		scope="session",
		params=[
				"122-39-4",
				"71-43-2",
				"107-10-8",
				"57-13-6",
				"507-70-0",
				"78-93-3",
				],
		)
def spectra(request) -> Tuple[str, Optional[MassSpectrum]]:
	# Download required files from NIST Webbook
	nist_data_dir = pathlib.Path("nist_jdx_files")

	if not nist_data_dir.exists():
		nist_data_dir.mkdir(parents=True)

	cas = request.param
	jcamp_file = nist_data_dir / f"{cas}.jdx"

	if not jcamp_file.exists():
		url = f"https://web.archive.org/web/20201215130403/https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C{cas.replace('-', '')}&Index=0&Type=Mass"
		r = requests.get(url)
		if r.status_code != 200:
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
