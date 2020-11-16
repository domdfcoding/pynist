#!/usr/bin/env python
#
#  parse_mona_contributors.py
"""
Script to both parse MoNA JSON data into a single MSP file and compile a contributors to
the MoNA library, in a more efficient manner than doing them separately.
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
import pathlib

# this package
import MoNA_GCMS_Library
from pyms_nist_search import ReferenceData
from pyms_nist_search.mona_tools import mass_spec_from_mona, parse_metadata


def main():
	contributors = MoNA_GCMS_Library.parse_mona_contributors.ContributorList()

	# Create ReferenceData and write to file
	with open(pathlib.Path(MoNA_GCMS_Library.__file__).parent / "MoNA.msp", "w") as msp_fp:

		for comp in MoNA_GCMS_Library.parse_mona_json.load_mona_json():

			compound: dict = comp["compound"][0]
			names: list = compound["names"]
			name: str = names[0]["name"]
			synonyms: list = [name for name in names[1:]]

			mass_spec = mass_spec_from_mona(comp["spectrum"])

			properties_dict = parse_metadata(comp)

			# Contributors
			contributor = contributors.add_contributor(properties_dict["contributor"])
			contributor.add_contribution(**properties_dict)

			# MSP
			del properties_dict["license"]

			ref_data = ReferenceData(
					name=name,
					mass_spec=mass_spec,
					synonyms=synonyms,
					**properties_dict,
					)

			msp = ref_data.to_msp()
			print(msp)
			msp_fp.write(msp)

	contributors.write_authors_file()


if __name__ == "__main__":
	main()
