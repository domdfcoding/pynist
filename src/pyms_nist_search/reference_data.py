#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  reference_data.py
"""
Class to store reference data from NIST MS Search
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
import copy
import json
import pathlib
import warnings

# 3rd party
from domdf_python_tools.utils import chunks
from pyms.Spectrum import MassSpectrum, normalize_mass_spec
from pyms.Utils.jcamp import header_info_fields, JcampTagWarning, xydata_tags
from pyms.Utils.Math import is_float

# this package
import pyms_nist_search.templates
from pyms_nist_search.mona_tools import mass_spec_from_mona, parse_metadata
from .base import NISTBase
from .utils import parse_name_chars
from .templates import *


class ReferenceData(NISTBase):
	"""
	Class to store reference data from NIST MS Search
	"""
	
	def __init__(
			self, name='', cas='---', nist_no=0, id='', mw=0.0,
			formula='', contributor='', mass_spec=None, synonyms=None,
			exact_mass=None,
			):
		"""
		:param name: The name of the compound
		:type name: str
		:param cas: The CAS number of the compound
		:type cas: str
		:param nist_no:
		:type nist_no: int or str
		:param id:
		:type id: str
		:param mw:
		:type mw: float or int or str
		:param formula: The formula of the compound
		:type formula: str
		:param contributor: The contributor to the library
		:type contributor: str
		:param mass_spec: The reference mass spectrum
		:type mass_spec: pyms.Spectrum.MassSpectrum
		:param synonyms: List of synonyms for the compound
		:type synonyms: list of str
		"""
		
		NISTBase.__init__(self, name, cas)
		
		self._formula = str(formula)
		self._contributor = str(contributor)
		
		self._nist_no = int(nist_no)
		self._id = str(id)
		
		self._mw = int(mw)

		if not exact_mass:
			self._exact_mass = float(mw)
		else:
			self._exact_mass = float(exact_mass)
		
		if mass_spec is None:
			self._mass_spec = None
		elif isinstance(mass_spec, dict):
			self._mass_spec = MassSpectrum(**mass_spec)
		else:
			self._mass_spec = copy.copy(mass_spec)
		
		if synonyms is None:
			self._synonyms = []
		else:
			self._synonyms = [str(synonym) for synonym in synonyms]
	
	@property
	def formula(self):
		"""
		Returns the formula of the compound.

		:rtype: str
		"""
		
		return self._formula
	
	@property
	def contributor(self):
		"""
		Returns the name of the contributor to the library.

		:rtype: str
		"""
		
		return self._contributor
	
	@property
	def nist_no(self):
		return self._nist_no
	
	@property
	def id(self):
		return self._id
	
	@property
	def mw(self):
		"""
		Returns the molecular weight of the compound
		
		:rtype: int
		"""
		
		return self._mw
	
	@property
	def exact_mass(self):
		"""
		Returns the exact mass of the compound
		
		:rtype: float
		"""
		
		return self._exact_mass
	
	@property
	def mass_spec(self):
		"""
		Returns the mass spectrum of the compound.

		:rtype: pyms.Spectrum.MassSpectrum
		"""
		
		return copy.copy(self._mass_spec)
	
	@property
	def synonyms(self):
		"""
		Returns a list of synonyms for the compound.

		:rtype: list of str
		"""
		
		return self._synonyms[:]
	
	@classmethod
	def from_pynist(cls, pynist_dict):
		"""
		Create a :class:`ReferenceData` object from the raw data returned by the C extension.

		:type pynist_dict: dict

		:rtype: ReferenceData
		"""
		
		return cls(
				name=parse_name_chars(pynist_dict["name_chars"]),
				cas=pynist_dict["cas"],
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
	
	def __dict__(self, recursive=False):
		class_dict = dict(
				name=self.name,
				cas=self.cas,
				formula=self.formula,
				contributor=self.contributor,
				nist_no=self.nist_no,
				id=self.id,
				mw=self.mw,
				exact_mass=self.exact_mass,
				synonyms=self.synonyms[:],
				)
		
		if recursive:
			class_dict["mass_spec"] = dict(self.mass_spec)
		else:
			class_dict["mass_spec"] = copy.copy(self.mass_spec)
		
		return class_dict
	
	@classmethod
	def from_jcamp(cls, file_name, ignore_warnings=True):
		"""
		Create a ReferenceData object from a JCAMP-DX file
	
		:param file_name: Path of the file to read
		:type file_name: str or pathlib.Path
		:param ignore_warnings: Whether warnings about invalid tags should be shown. Default True
		:type ignore_warnings: bool, optional
	
		:return: ReferenceData
		:rtype: :class:`pyms_nist_search.reference_data.ReferenceData`
	
		:authors: Qiao Wang, Andrew Isaac, Vladimir Likic, David Kainer, Dominic Davis-Foster
		"""
		
		with warnings.catch_warnings():
			
			if ignore_warnings:
				warnings.simplefilter("ignore", JcampTagWarning)
			
			if not isinstance(file_name, (str, pathlib.Path)):
				raise TypeError("'file_name' must be a string or a pathlib.Path object")
			
			if not isinstance(file_name, pathlib.Path):
				file_name = pathlib.Path(file_name)
			
			# Commented this line because it also gets printed when the MassSpectrum is created
			# print(f" -> Reading JCAMP file '{file_name}'")
			lines_list = file_name.open('r')
			last_tag = None
			
			header_info = {}  # Dictionary containing header information
			
			for line in lines_list:
				
				if len(line.strip()):
					if line.startswith("##"):
						# key word or information
						fields = line.split('=', 1)
						current_tag = fields[0] = fields[0].lstrip("##").upper()
						last_tag = fields[0]
						fields[1] = fields[1].strip()
						
						if current_tag.upper().startswith("END"):
							break
						
						elif current_tag in xydata_tags:
							continue
						
						elif current_tag in header_info_fields:
							if fields[1].isdigit():
								header_info[current_tag] = int(fields[1])
							elif is_float(fields[1]):
								header_info[current_tag] = float(fields[1])
							else:
								header_info[current_tag] = fields[1]
						else:
							warnings.warn(current_tag, JcampTagWarning)
					
					else:
						if last_tag in header_info:
							header_info[last_tag] += f"{line}"
			
			return cls(
					name=header_info["TITLE"],
					cas=header_info["CAS REGISTRY NO"],
					nist_no=header_info["$NIST MASS SPEC NO"],
					contributor=header_info["ORIGIN"],
					formula=header_info["MOLFORM"],
					mw=header_info["MW"],
					mass_spec=MassSpectrum.from_jcamp(file_name),
					)
	
	def to_json(self):
		"""
		Convert the object to json

		:rtype: str
		"""
		
		return json.dumps(self.__dict__(recursive=True))
	
	@classmethod
	def from_json(cls, json_data):
		"""
		Construct an object from json data.

		:type json_data: str
		"""
		
		peak_dict = json.loads(json_data)
		# peak_dict["mass_spec"] = MassSpectrum.from_dict(peak_dict["mass_spec"])
		return cls.from_dict(peak_dict)
	
	@classmethod
	def from_mona_dict(cls, mona_data: dict):
		"""
		Construct an object from Massbank of North America json data
		that has been loaded into a dictionary.

		:type mona_data: dict
		"""
		
		compound: dict = mona_data["compound"][0]
		names: list = compound["names"]
		name: str = names[0]["name"]
		synonyms: list = [name for name in names[1:]]
		
		properties_dict = parse_metadata(mona_data)
		
		# Remove unwanted properties
		del properties_dict['license']

		mass_spec = mass_spec_from_mona(mona_data["spectrum"])
		
		return cls(
				name=name,
				mass_spec=mass_spec,
				synonyms=synonyms,
				**properties_dict,
				)
	
	def to_msp(self):
		"""
		Returns the ReferenceData object as an MSP file similar to that produced by
		NIST MS Search's export function
		
		:return:
		:rtype:
		"""
		
		normalized_ms = normalize_mass_spec(self.mass_spec, max_intensity=999)
		num_peaks = len(self.mass_spec)

		mz_int_pairs = [f"{mz} {intensity}" for mz, intensity in normalized_ms.iter_peaks()]
		
		spec_block = []
		
		for row in list(chunks(mz_int_pairs, 5)):
			spec_block.append("; ".join(x for x in row))
		
		msp_text = msp_template.render(
				ref_data=self,
				num_peaks=num_peaks,
				spec_block="\n".join(spec_block),
				)
		
		return msp_text
