#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#  utils.py
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
#  PyMassSpec NIST Search includes the redistributable binaries for NIST MS Search in
#  the x86 and x64 directories. Available from
#  ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip .
#  ctnt66.dll and ctnt66_64.dll copyright 1984-1996 FairCom Corporation.
#  "FairCom" and "c-tree Plus" are trademarks of FairCom Corporation
#  and are registered in the United States and other countries.
#  All Rights Reserved.



# stdlib
import json
import urllib.parse

# 3rd party
from pyms.Spectrum import MassSpectrum

# this package
from .search_result import SearchResult
from .reference_data import ReferenceData


def quote_mass_spec(mass_spec):
	"""
	
	:param mass_spec:
	:type mass_spec: pyms.Spectrum.MassSpectrum
	:return:
	:rtype:
	"""
	
	if not isinstance(mass_spec, MassSpectrum):
		raise ValueError("`mass_spec` must be a `pyms.Spectrum.MassSpectrum` object")
	
	return urllib.parse.quote(json.dumps(dict(mass_spec)))


def unquote_mass_spec(string):
	json_data = urllib.parse.unquote(string)
	data_dict = json.loads(json_data)

	return MassSpectrum.from_dict(data_dict)


class PyNISTEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, (SearchResult, ReferenceData, MassSpectrum)):
			return dict(o)
		else:
			json.JSONEncoder.default(self, o)
