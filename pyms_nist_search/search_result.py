#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#  search_result.py
"""
Class to store search results from NIST MS Search
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


# this package
from .utils import parse_name_chars
from .base import NISTBase


class SearchResult(NISTBase):
	"""
	Class to store search results from NIST MS Search
	"""
	
	def __init__(
			self, name='', cas='', match_factor=0,
			reverse_match_factor=0, hit_prob=0.0, spec_loc=0):
		"""
		:param name: The name of the compound
		:type name: str
		:param cas: The CAS number of the compound
		:type cas: str
		:param match_factor:
		:type match_factor: int
		:param reverse_match_factor:
		:type reverse_match_factor: int
		:param hit_prob:
		:type hit_prob: float
		:param spec_loc: The location of the reference spectrum in the library.
		:type spec_loc: int
		"""
		
		NISTBase.__init__(self, name, cas)
		
		self._match_factor = int(match_factor)
		self._reverse_match_factor = int(reverse_match_factor)
		
		self._hit_prob = float(hit_prob)
		self._spec_loc = int(spec_loc)
	
	@property
	def match_factor(self):
		"""
		Returns a score (out of 1000) representing the similarity of the searched
		mass spectrum to the search result.
		
		:rtype: int
		"""
		
		return int(self._match_factor)
	
	@property
	def reverse_match_factor(self):
		"""
		Returns a score (out of 1000) representing the similarity of the searched
		mass spectrum to the search result, but ignoring any peaks that are in
		the searched mass spectrum but not in the library spectrum.

		:rtype: int
		"""

		return int(self._reverse_match_factor)
	
	@property
	def hit_prob(self):
		"""
		
		:rtype: float
		"""
		
		return float(self._hit_prob)
	
	@property
	def spec_loc(self):
		"""
		Returns a the location of the reference spectrum in the library.
		This can then be searched using the `get_reference_data` method of the
		search engine to obtain the reference data.
		
		:rtype: int
		"""

		return int(self._spec_loc)
	
	@classmethod
	def from_pynist(cls, pynist_dict):
		"""
		Create a :class:`SearchResult` object from the raw data returned by the C extension.
		
		:type pynist_dict: dict
		
		:rtype: SearchResult
		"""

		return cls(
				name=parse_name_chars(pynist_dict["hit_name_chars"]),
				cas=pynist_dict["cas_no"],
				match_factor=pynist_dict["sim_num"],
				reverse_match_factor=pynist_dict["rev_sim_num"],
				hit_prob=pynist_dict["hit_prob"]/100,
				spec_loc=pynist_dict["spec_loc"],
				)
	
	def __repr__(self):
		return f"Search Result: {self.name} \t({self.match_factor})"
		
	def __dict__(self):
		return dict(
				name=self._name,
				cas=self.cas,
				match_factor=self.match_factor,
				reverse_match_factor=self.reverse_match_factor,
				spec_loc=self.spec_loc,
				hit_prob=self.hit_prob,
				)
