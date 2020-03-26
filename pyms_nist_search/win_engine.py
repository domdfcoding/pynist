#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pynist_search_server.py
"""
Search engine for Windows systems
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
#  PyMassSpec NIST Search includes the redistributable binaries for NIST MS Search in
#  the x86 and x64 directories. Available from
#  ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip .
#  ctnt66.dll and ctnt66_64.dll copyright 1984-1996 FairCom Corporation.
#  "FairCom" and "c-tree Plus" are trademarks of FairCom Corporation
#  and are registered in the United States and other countries.
#  All Rights Reserved.


# stdlib
import atexit
import os
import os.path

# 3rd party
from pyms.Spectrum import MassSpectrum

# this package
from . import _core
from ._core import *
from .reference_data import ReferenceData
from .search_result import SearchResult
from .utils import pack


class Engine:
	"""
	Search engine for Windows systems
	"""
	
	def __init__(self, lib_path, lib_type, work_dir=None, debug=False):
		"""
		TODO: Search by Name. See page 13 of the documentation.
		 Would also like to search by CAS number but DLL doesn't seem to support that

		:param lib_path: The path to the mass spectral library
		:type lib_path: str or pathlib.Path
		:param lib_type: The type of library. One of NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB
		:type lib_type: int
		:param work_dir: The path to the working directory
		:type work_dir: str or pathlib.Path
		"""
		
		if work_dir is None:
			work_dir = os.getcwd()
		
		if not os.path.exists(lib_path):
			raise FileNotFoundError(f"Library not found at the given path: {lib_path}")
		
		# Create work_dir if it doesn't exist
		if not os.path.exists(work_dir):
			os.mkdir(work_dir)
		
		self.debug = debug
		
		_core._init_api(str(lib_path), lib_type, str(work_dir))
		
		atexit.register(self.uninit)
	
	def uninit(self):
		"""
		Uninitialize the Search Engine
		"""
		
		pass
	
	def spectrum_search(self, mass_spec, n_hits=5):
		"""
		Perform a Quick Spectrum Search of the mass spectral library

		:param mass_spec: The mass spectrum to search against the library
		:type mass_spec: pyms.Spectrum.MassSpectrum
		:param n_hits: The number of hits to return
		:type n_hits: int

		:return: List of possible identities for the mass spectrum
		:rtype: list of SearchResult
		"""
		
		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")
		
		hit_list = _core._spectrum_search(pack(mass_spec, len(mass_spec)))[:n_hits]
		
		parsed_hit_list = []
		
		for hit in hit_list:
			parsed_hit_list.append(SearchResult.from_pynist(hit))
		
		return parsed_hit_list
	
	def full_spectrum_search(self, mass_spec, n_hits=5):
		"""
		Perform a Full Spectrum Search of the mass spectral library
		
		:param mass_spec: The mass spectrum to search against the library
		:type mass_spec: pyms.Spectrum.MassSpectrum
		:param n_hits: The number of hits to return
		:type n_hits: int
		
		:return: List of possible identities for the mass spectrum
		:rtype: list of SearchResult
		"""
		
		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")
		
		hit_list = _core._full_spectrum_search(pack(mass_spec, len(mass_spec)))[:n_hits]
		
		parsed_hit_list = []
		
		for hit in hit_list:
			parsed_hit_list.append(SearchResult.from_pynist(hit))
		
		return parsed_hit_list
	
	def full_search_with_ref_data(self, mass_spec, n_hits=5):
		"""
		Perform a Full Spectrum Search of the mass spectral library, including reference data.

		:param mass_spec: The mass spectrum to search against the library
		:type mass_spec: pyms.Spectrum.MassSpectrum
		:param n_hits: The number of hits to return
		:type n_hits: int

		:return: List of tuples consisting of the possible identities for the mass spectrum and the reference data from the library
		:rtype: list of (SearchResult, ReferenceData) tuples
		"""
		
		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")
		
		hit_list = self.full_spectrum_search(mass_spec)[:n_hits]
		output_buffer = []
		
		for idx, hit in enumerate(hit_list):
			ref_data = self.get_reference_data(hit.spec_loc)
			output_buffer.append((hit, ref_data))
		
		return output_buffer
	
	def get_reference_data(self, spec_loc):
		"""
		Get reference data from the library for the compound at the given location.

		:type spec_loc: int

		:rtype: ReferenceData
		"""
		
		reference_data = _core._get_reference_data(spec_loc)
		
		return ReferenceData.from_pynist(reference_data)
