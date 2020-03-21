#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#  search_result.py
#
#  This file is part of PyNIST
#  Python interface to the NIST MS Search DLL
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  PyNIST is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation; either version 3 of
#  the License, or (at your option) any later version.
#
#  PyNIST is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  PyNIST includes the redistributable binaries for NIST MS Search in
#  the x86 and x64 directories. Available from
#  ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip .
#  ctnt66.dll and ctnt66_64.dll copyright 1984-1996 FairCom Corporation.
#  "FairCom" and "c-tree Plus" are trademarks of FairCom Corporation
#  and are registered in the United States and other countries.
#  All Rights Reserved.



import json


class SearchResult:
	def __init__(self, name='', cas='', match_factor=0, reverse_match_factor=0, hit_prob=0.0, spec_loc=0):
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
		
		self._name = name
		
		if cas == "0-00-0":
			cas = "---"
		self._cas = cas
		
		self._match_factor = int(match_factor)
		self._reverse_match_factor = int(reverse_match_factor)
		
		self._hit_prob = float(hit_prob)
		self._spec_loc = int(spec_loc)
	
	@property
	def name(self):
		return self._name
	
	@property
	def cas(self):
		return self._cas
		
	@property
	def match_factor(self):
		return int(self._match_factor)
	
	@property
	def reverse_match_factor(self):
		return int(self._reverse_match_factor)
	
	@property
	def hit_prob(self):
		return float(self._hit_prob)
	
	@property
	def spec_loc(self):
		return int(self._spec_loc)
	
	@classmethod
	def from_pynist(cls, pynist_dict):
		return cls(
				match_factor=pynist_dict["sim_num"],
				reverse_match_factor=pynist_dict["rev_sim_num"],
				hit_prob=pynist_dict["hit_prob"]/100,
				cas=cas_int_to_string(pynist_dict["cas_no"]),
				name=parse_name_chars(pynist_dict["hit_name_chars"]),
				spec_loc=pynist_dict["spec_loc"],
				)
	
	def __repr__(self):
		return f"Search Result: {self.name} \t({self.match_factor})"
	
	def __str__(self):
		return self.__repr__()
	
	def __dict__(self):
		return dict(
				name=self._name,
				cas=self.cas,
				match_factor=self.match_factor,
				reverse_match_factor=self.reverse_match_factor,
				spec_loc=self.spec_loc,
				hit_prob=self.hit_prob,
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

