#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  search_result.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020  Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  GunShotMatch is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  GunShotMatch is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# stdlib
import json

# 3rd party
from pyms.Spectrum import MassSpectrum


class ReferenceData:
	def __init__(self, name='', cas='', nist_no=0, id=0, mw=0.0, formula='', contributor='', mass_spec=None, synonyms=None):
		"""
		
		:param name: The name of the compound
		:type name: str
		:param cas: The CAS number of the compound
		:type cas: str
		:param nist_no:
		:type nist_no:
		:param id:
		:type id:
		:param mw:
		:type mw:
		:param formula:
		:type formula:
		:param contributor:
		:type contributor:
		:param mass_spec:
		:type mass_spec:
		:param synonyms:
		:type synonyms:
		"""
		
		self._name = name
		self._formula = formula
		self._contributor = contributor
		
		if cas == "0-00-0":
			cas = "---"
		self._cas = cas
		
		self._nist_no = int(nist_no)
		self._id = int(id)
		
		self._mw = float(mw)
		
		if mass_spec is None:
			self._mass_spec = None
		elif isinstance(mass_spec, dict):
			self._mass_spec = MassSpectrum(**mass_spec)
		else:
			self._mass_spec = copy_mass_spec(mass_spec)
		
		if synonyms is None:
			self._synonyms = []
		else:
			self._synonyms = synonyms[:]
	
	@property
	def name(self):
		return self._name
	
	@property
	def cas(self):
		return self._cas
		
	@property
	def formula(self):
		return self._formula
	
	@property
	def contributor(self):
		return self._contributor
	
	@property
	def nist_no(self):
		return int(self._nist_no)
	
	@property
	def id(self):
		return int(self._id)
	
	@property
	def mw(self):
		return int(self._mw)
	
	@property
	def mass_spec(self):
		return copy_mass_spec(self._mass_spec)
	
	@property
	def synonyms(self):
		return self._synonyms[:]
	
	@classmethod
	def from_pynist(cls, pynist_dict):
		return cls(
				name=parse_name_chars(pynist_dict["name_chars"]),
				cas=cas_int_to_string(pynist_dict["cas"]),
				formula=pynist_dict["formula"],
				contributor=pynist_dict["contributor"],
				nist_no=pynist_dict["nist_no"],
				id=pynist_dict["id"],
				mw=pynist_dict["mw"],
				mass_spec=MassSpectrum(pynist_dict["mass_list"], pynist_dict["intensity_list"]),
				synonyms=[parse_name_chars(synonym) for synonym in pynist_dict["synonyms_chars"]],
				)
	
	def __repr__(self):
		return f"Reference Data: {self.name} \t({self.cas})"
	
	def __str__(self):
		return self.__repr__()
	
	def __dict__(self):
		return dict(
				name=self._name,
				cas=self.cas,
				formula=self.formula,
				contributor=self.contributor,
				nist_no=self.nist_no,
				id=self.id,
				mw=self.mw,
				mass_spec=copy_mass_spec(self.mass_spec),
				synonyms=self.synonyms[:],
				)
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
	
	def __getstate__(self):
		return self.__dict__()
	
	def __setstate__(self, state):
		self.__init__(**state)
	
	@classmethod
	def from_json(cls, json_data):
		peak_dict = json.load(json_data)
		
		return cls.from_dict(peak_dict)
	
	@classmethod
	def from_dict(cls, dictionary):
		return cls(**dictionary)
	
	def to_json(self):
		return json.dumps(dict(self))


def parse_name_chars(name_char_list):
	"""
	Takes a list of Unicode character codes and converts them to characters,
	taking into account the special codes used by the NIST DLL.
	
	:param name_char_list:
	:type name_char_list: list of int
	
	:return:
	:rtype: str
	"""
	
	hit_name = ''
	for dec in name_char_list[:-1]:
		if dec == 224:
			char = "α"
		elif dec == 225:
			char = "β"
		elif dec == 231:
			char = "γ"
		elif dec == 235:
			char = "δ"
		elif dec == 238:
			char = "ε"
		elif dec == 227:
			char = "π"
		elif dec == 229:
			char = "σ"
		elif dec == 230:
			char = "μ"
		elif dec == 234:
			char = "ω"
		elif dec == 241:
			char = "±"
		elif dec == 252:
			char = "η"
		else:
			char = chr(dec)
		
		if char != "\x00":
			hit_name += char
	
	return hit_name


def cas_int_to_string(cas_no):
	"""
	Converts an integer CAS number to a hyphenated string
	
	:param cas_no:
	:type cas_no: int
	
	:return:
	:rtype:
	"""
	
	cas_no = int(cas_no)
	
	check_digit = cas_no % 10
	main_value = (cas_no - check_digit) // 10
	block_2 = main_value % 100
	block_1 = (main_value - block_2) // 100
	
	# TODO: Check check_digit
	
	return f"{block_1}-{block_2}-{check_digit}"


def cas_string_to_int(cas_no):
	"""
	Converts a hyphenated string CAS number to a integer

	:param cas_no:
	:type cas_no: int

	:return:
	:rtype:
	"""
	
	cas_no = str(cas_no)
	
	block_1, block_2, check_digit = cas_no.split("-")
	
	block_1 = int(block_1) * 1000
	block_2 = int(block_2) * 10
	check_digit = int(check_digit) * 1
	
	# TODO: Check check_digit
	
	return block_1 + block_2 + check_digit


def copy_mass_spec(mass_spec):
	""" Returns a copy of the MassSpectrum object given"""
	
	if not isinstance(mass_spec, MassSpectrum):
		raise TypeError("`mass_spec` must be a `pyms.Spectrum.MassSpectrum` object.")
	
	return MassSpectrum(mass_spec.mass_list[:], mass_spec.intensity_list[:])

