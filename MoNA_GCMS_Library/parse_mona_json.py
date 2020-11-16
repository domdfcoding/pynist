#!/usr/bin/env python
#
#  parse_mona_json.py
"""
Script to parse MoNA JSON data into ReferenceData objects and then convert them into a single MSP file.
That file can then be converted into a NIST User Library using the Lib2Nist program from
https://chemdata.nist.gov/mass-spc/ms-search/Library_conversion_tool.html
"""
#
#  This file is part of PyMassSpec NIST Search
#  Python interface to the NIST MS Search DLL
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  PyMassSpec NIST Search is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation; either version 3 of
#  the License, or (at your option) any later version.
#
#  PyMassSpec NIST Search is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import json
import pathlib
import shutil

# 3rd party
import importlib_resources

# this package
import MoNA_GCMS_Library
from pyms_nist_search import ReferenceData

# import urllib.request


def load_mona_json():
	mona_library_dir = pathlib.Path(__file__).parent
	library_json_file = mona_library_dir / "MoNA-export-GC-MS_Spectra.json"
	library_zip_file = mona_library_dir / "MoNA-export-GC-MS_Spectra-json.zip"

	# if not library_json_file.is_file() and not library_zip_file.is_file():
	# 	urllib.request.urlretrieve(
	# 			'https://mona.fiehnlab.ucdavis.edu/rest/downloads/retrieve/33c87724-3595-4d7e-9bc0-35d1011c7482/',
	# 			str(library_zip_file))

	if not library_json_file.is_file():
		shutil.unpack_archive(str(library_zip_file), str(mona_library_dir), format="zip")
	return json.loads(importlib_resources.read_text(MoNA_GCMS_Library, "MoNA-export-GC-MS_Spectra.json"))


def create_mona_msp():
	# Create ReferenceData and write to file
	with open(pathlib.Path(MoNA_GCMS_Library.__file__).parent / "MoNA.msp", "w") as fp:
		for comp in load_mona_json():
			ref_data = ReferenceData.from_mona_dict(comp)
			msp = ref_data.to_msp()
			# print(msp)
			fp.write(msp)


def main():
	create_mona_msp()


if __name__ == '__main__':
	main()
