#!/usr/bin/env python
#
#  mona_tools.py
"""
Functions for working with MoNA JSON data.

It could probably be its own package.
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
from typing import Any, Dict, Iterable, List, Mapping, Set

# 3rd party
from pyms.Spectrum import MassSpectrum

__all__ = (
		"prep_match_list",
		"other_dbs",
		"mona_skip_compound_props",
		"mona_skip_categories",
		"mona_skip_properties",
		"parse_metadata",
		"mass_spec_from_mona",
		)


def prep_match_list(match_list: Iterable[str]) -> Set[str]:
	"""
	Prepare a list of matches for caseless matching with :meth:`str.casefold`.

	:param match_list:
	"""

	return {x.casefold() for x in match_list}


other_dbs: Set[str] = prep_match_list([
		"SMILES",
		"InChI",
		"InChIKey",
		"kegg",
		"chebi",
		"pubchem cid",
		"chemspider",
		"PubChem",
		"lipidbank",
		"knapsack",
		"lipidmaps",
		"hmdb",
		])

mona_skip_compound_props: Set[str] = prep_match_list([*other_dbs, "compound class"])

mona_skip_categories: Set[str] = prep_match_list([
		"mass spectrometry",
		"focused ion",
		"spectral properties",
		"acquisition properties",
		])

mona_skip_properties: Set[str] = prep_match_list([
		"date",
		"ionization mode",
		"instrument",
		"instrument type",
		"chromatography type",
		"column",
		"guard column",
		"mobile phase",
		"column temperature",
		"flow rate",
		"injection volume",
		"injection",
		"injection temperature",
		"data transformation",
		"chromatogram",
		"retention index",
		"retention index type",
		"detector voltage",
		"derivatization type",
		"derivatization formula",
		"derivatization mass",
		"scan range",
		"ms level",
		"comment",
		"oven temperature",
		"retention time",
		"whole",
		"copyright",
		"transfer line temperature",
		"publication",
		"ion source temperature",
		"ionization energy",
		"scannumber",
		"quantmass",
		"intensity",
		"origin",
		"modelion",
		"modelionheight",
		"modelionarea",
		"integratedheight",
		"integratedarea",
		"comments",
		"sample file",
		"sample type",
		"species",
		"organ",
		"annotation",
		"biological matrix used sample preparation",
		"collision energy",
		"precursor type",
		"carrier gas",
		"recalibrate",
		"column temperature gradient",
		"transferline temperature",
		"sample introduction",
		"derivatization",
		"ionization",
		])


def parse_metadata(mona_data: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Parse metadata for the compound.

	:param mona_data:
	"""

	compound: Dict = mona_data["compound"][0]
	compound_metadata: List = compound["metaData"]
	metadata: List = mona_data["metaData"]
	submitter: Dict = mona_data["submitter"]

	properties_dict: Dict[str, Any] = {
			"formula": '',
			"mw": 0,
			"exact_mass": 0.0,
			"cas": '',
			"contributor": '',
			"license": '',
			}

	if "id" in mona_data:
		properties_dict["id"] = mona_data["id"]
	else:
		properties_dict["id"] = ''

	prop_lookup: Dict[str, str] = {
			"accession": "id",
			"exact mass": "exact_mass",
			"author": "contributor",
			"molecular formula": "formula",
			"total exact mass": "exact_mass",
			"accurate mass": "exact_mass",
			"cas number": "cas",
			"cas": "cas",
			"license": "license",
			}

	def set_prop_value(property_name: str, prop_: Mapping[str, Any]) -> None:
		if not properties_dict[property_name]:
			properties_dict[property_name] = prop_["value"]

	def parse_compound_prop(prop_: Mapping[str, Any]) -> None:
		# Put props in order of priority
		for prop_name in ["molecular formula", "total exact mass", "cas number", "cas"]:
			if prop_["name"].casefold() == prop_name:
				set_prop_value(prop_lookup[prop_name], prop_)
				break
		else:
			print(prop_)

	def parse_property(prop_: Mapping[str, Any]) -> None:
		# Put props in order of priority
		for prop_name in ["accession", "exact mass", "author", "institution", "accurate mass", "license"]:
			if prop_["name"].casefold() == prop_name:
				set_prop_value(prop_lookup[prop_name], prop_)
				break
		else:
			print(prop_)

	for prop in compound_metadata:
		if prop["name"].casefold() in mona_skip_compound_props:
			continue

		elif not prop["computed"]:
			parse_compound_prop(prop)
		# prioritise not computed
		elif prop["computed"]:
			parse_compound_prop(prop)
		else:
			# Unknown property
			print(prop)

	for prop in metadata:
		if "category" in prop and prop["category"].casefold() in mona_skip_categories:
			continue

		elif prop["name"].casefold() in prep_match_list((
				*mona_skip_properties,
				"data format",
				"institution",
				"formula",
				"ion type",
				)):
			# todo: "data format"
			continue

		elif not prop["computed"]:
			# prioritise not computed
			parse_property(prop)
		elif prop["computed"]:
			parse_property(prop)
		else:
			# Unknown property
			print(prop)

	if not properties_dict["contributor"] and "institution" in submitter:
		properties_dict["contributor"] = submitter["institution"]

	if not properties_dict["mw"]:
		properties_dict["mw"] = properties_dict["exact_mass"]

	# ignored following keys
	#  dateCreated
	#  lastUpdated
	#  lastCurated
	#  score
	#  splash
	#  tags
	#  library

	return properties_dict


def mass_spec_from_mona(mona_ms_string: str) -> MassSpectrum:
	"""
	Create a :class:`pyms.Spectrum.MassSpectrum` object from the MoNA JSON representation of the spectrum.

	:param mona_ms_string:
	"""

	pairs = [val.split(':') for val in mona_ms_string.split(' ')]
	return MassSpectrum.from_mz_int_pairs([(float(mz), float(int_)) for mz, int_ in pairs])
