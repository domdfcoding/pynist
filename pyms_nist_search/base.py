#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#  base.py
"""
Base class for other PyMassSpec NIST Search classes
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
import json

# 3rd party
from chemistry_tools.cas import cas_int_to_string, check_cas_number

# this package
from .utils import parse_name_chars


class NISTBase:
	"""
	Base class for other PyMassSpec NIST Search classes
	"""
	
	def __init__(self, name='', cas='---'):
		"""

		:param name: The name of the compound
		:type name: str
		:param cas: The CAS number of the compound
		:type cas: str
		"""
		
		self._name = name
		
		if isinstance(cas, int):
			if check_cas_number(cas):
				cas = "---"
			else:
				cas = cas_int_to_string(cas)
			
		if cas == "0-00-0":
			cas = "---"
		self._cas = cas
	
	@property
	def name(self):
		"""
		Returns the name of the compound.

		:rtype: str
		"""
		
		return self._name
	
	@property
	def cas(self):
		"""
		Returns the CAS number of the compound.

		:rtype: str
		"""
		
		return self._cas
	
	@classmethod
	def from_json(cls, json_data):
		"""
		Construct an object from json data.
		
		:type json_data: str
		"""
		
		peak_dict = json.load(json_data)
		
		return cls.from_dict(peak_dict)
	
	@classmethod
	def from_dict(cls, dictionary):
		"""
		Construct an object from a dictionary.

		:type dictionary: dict
		"""
		
		return cls(**dictionary)
	
	def to_json(self):
		"""
		Convert the object to json
		
		:rtype: str
		"""
		
		return json.dumps(dict(self))

	@classmethod
	def from_pynist(cls, pynist_dict):
		"""
		Create an object from the raw data returned by the C extension.

		:type pynist_dict: dict
		"""
		
		return cls(
				name=parse_name_chars(pynist_dict["hit_name_chars"]),
				cas=cas_int_to_string(pynist_dict["cas_no"]),
				)
	
	def __dict__(self):
		return dict(
				name=self._name,
				cas=self.cas,
				)

	def __getstate__(self):
		return self.__dict__()
	
	def __setstate__(self, state):
		self.__init__(**state)
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
	
	def __str__(self):
		return self.__repr__()
	
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.__dict__() == other.__dict__()
		
		return NotImplemented
