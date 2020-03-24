#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pynist_search_server.py
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
import os

# this package
from . import _core
from ._core import *
from .reference_data import ReferenceData
from .search_result import SearchResult
from .utils import pack


class Engine:
	def __init__(self, lib_path, lib_type, work_dir=None):
		"""

		TODO: Search by Name. See page 13 of the documentation.
		 Would also like to search by CAS number but DLL doesn't seem to support that

		:param lib_path:
		:type lib_path:
		:param lib_type:
		:type lib_type:
		:param work_dir:
		:type work_dir:
		"""
		
		if work_dir is None:
			work_dir = os.getcwd()
		
		# TODO: check library and work dir exist
		
		_core._init_api(lib_path, lib_type, work_dir)
	
	def uninit(self):
		"""
		Uninitialize the Search Engine
		"""
		
		pass
	
	def spectrum_search(self):
		# TODO
		pass
	
	def full_spectrum_search(self, mass_spec):
		# TODO: type check
		
		values = list(zip(mass_spec.mass_list, mass_spec.intensity_list))
		hit_list = _core._full_spectrum_search(pack(values, len(values)))
		
		parsed_hit_list = []
		
		for hit in hit_list:
			parsed_hit_list.append(SearchResult.from_pynist(hit))
		
		return parsed_hit_list
	
	def full_search_with_ref_data(self, mass_spec):
		# TODO: type check
		
		hit_list = self.full_spectrum_search(mass_spec)
		output_buffer = []
		
		for idx, hit in enumerate(hit_list):
			ref_data = self.get_reference_data(hit.spec_loc)
			output_buffer.append((hit, ref_data))
		
		return output_buffer
	
	def get_reference_data(self, spec_loc):
		reference_data = _core._get_reference_data(spec_loc)
		
		return ReferenceData.from_pynist(reference_data)
