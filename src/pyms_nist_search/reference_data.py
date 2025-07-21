#!/usr/bin/env python
#
#  reference_data.py
"""
Class to store reference data from NIST MS Search.
"""
#
#  This file is part of PyMassSpec NIST Search
#  Python interface to the NIST MS Search DLL
#
#  Copyright (c) 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import warnings
from typing import Any, Dict, List, Optional, Sequence, Type, Union

# 3rd party
import sdjson
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.iterative import chunks
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from pyms.Spectrum import MassSpectrum, normalize_mass_spec
from pyms.Utils.jcamp import JcampTagWarning, header_info_fields, xydata_tags
from pyms.Utils.Math import is_float

# this package
from pyms_nist_search.base import NISTBase
from pyms_nist_search.mona_tools import mass_spec_from_mona, parse_metadata
from pyms_nist_search.templates import *
from pyms_nist_search.utils import parse_name_chars

__all__ = ("ReferenceData", )


@prettify_docstrings
class ReferenceData(NISTBase):
	"""
	Class to store reference data from NIST MS Search.

	:param name: The name of the compound.
	:param cas: The CAS number of the compound.
	:param nist_no:
	:param id:
	:param mw:
	:param formula: The formula of the compound.
	:param contributor: The contributor to the library.
	:param mass_spec: The reference mass spectrum.
	:param synonyms: List of synonyms for the compound.
	:param exact_mass: Not used.
	:param lib_idx: The (zero-based) index of the library the result was found in (see :meth:`~.WinEngine.get_lib_names()`).

	.. latex:vspace:: 100px
	"""

	_exact_mass: float
	_mass_spec: Optional[MassSpectrum]
	_synonyms: List[str]

	def __init__(
			self,
			name: str = '',
			cas: Union[str, int] = "---",
			nist_no: Union[int, str] = 0,
			id: Union[str, int] = '',  # noqa: A002  # pylint: disable=redefined-builtin
			mw: Union[float, str] = 0.0,
			formula: str = '',
			contributor: str = '',
			mass_spec: Optional[MassSpectrum] = None,
			synonyms: Optional[Sequence[str]] = None,
			exact_mass: Optional[Any] = None,
			lib_idx: int = 0,
			) -> None:

		NISTBase.__init__(self, name, cas)

		self._formula: str = str(formula)
		self._contributor: str = str(contributor)

		self._nist_no: int = int(nist_no)
		self._id: str = str(id)

		self._mw: int = int(mw)

		if not exact_mass:
			self._exact_mass = float(mw)
		else:
			self._exact_mass = float(exact_mass)

		self._lib_idx: int = int(lib_idx)

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
	def formula(self) -> str:
		"""
		The formula of the compound.
		"""

		return self._formula

	@property
	def contributor(self) -> str:
		"""
		The name of the contributor to the library.
		"""

		return self._contributor

	@property
	def nist_no(self) -> int:
		"""
		The NIST number of the compund.
		"""

		return self._nist_no

	@property
	def id(self) -> str:
		"""
		The ID of the compound.
		"""

		return self._id

	@property
	def mw(self) -> int:
		"""
		The molecular weight of the compound.
		"""

		return self._mw

	@property
	def exact_mass(self) -> float:
		"""
		The exact mass of the compound (not used).
		"""

		return self._exact_mass

	@property
	def mass_spec(self) -> Optional[MassSpectrum]:
		"""
		The mass spectrum of the compound.
		"""

		return copy.copy(self._mass_spec)

	@property
	def synonyms(self) -> List[str]:
		"""
		A list of synonyms for the compound.
		"""

		return self._synonyms[:]

	@property
	def lib_idx(self) -> int:
		"""
		The (zero-based) index of the library the result was found in (see :meth:`~.Engine.get_lib_names()`).
		"""

		return int(self._lib_idx)

	@classmethod
	def from_pynist(cls, pynist_dict: Dict[str, Any]) -> "ReferenceData":
		"""
		Create a :class:`ReferenceData` object from the raw data returned by the C extension.

		:param pynist_dict:
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
				lib_idx=pynist_dict["lib_idx"],
				)

	def __repr__(self) -> str:
		return f"Reference Data: {self.name} \t({self.cas})"

	def to_dict(self) -> Dict[str, Any]:
		"""
		Convert the object to a dictionary.

		.. versionadded:: 0.6.0
		"""

		return dict(
				name=self.name,
				cas=self.cas,
				formula=self.formula,
				contributor=self.contributor,
				nist_no=self.nist_no,
				id=self.id,
				mw=self.mw,
				exact_mass=self.exact_mass,
				synonyms=self.synonyms[:],
				mass_spec=self.mass_spec,
				lib_idx=self.lib_idx,
				)

	@property
	def __dict__(self):  # noqa: MAN002
		return self.to_dict()

	@classmethod
	def from_jcamp(cls, file_name: PathLike, ignore_warnings: bool = True) -> "ReferenceData":
		"""
		Create a ReferenceData object from a JCAMP-DX file.

		:param file_name: Path of the file to read.
		:param ignore_warnings: Whether warnings about invalid tags should be shown.

		:authors: Qiao Wang, Andrew Isaac, Vladimir Likic, David Kainer, Dominic Davis-Foster
		"""

		with warnings.catch_warnings():

			if ignore_warnings:
				warnings.simplefilter("ignore", JcampTagWarning)

			file_name = PathPlus(file_name)

			# Commented this line because it also gets printed when the MassSpectrum is created
			# print(f" -> Reading JCAMP file '{file_name}'")
			lines_list = file_name.read_lines()
			last_tag = None

			header_info: Dict[str, Any] = {}  # Dictionary containing header information

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

	def to_json(self) -> str:
		"""
		Convert the object to JSON.
		"""

		return sdjson.dumps(self.to_dict())

	@classmethod
	def from_json(cls: Type["ReferenceData"], json_data: str) -> "ReferenceData":
		"""
		Construct an object from JSON data.

		:param json_data:
		"""

		peak_dict = json.loads(json_data)
		# peak_dict["mass_spec"] = MassSpectrum.from_dict(peak_dict["mass_spec"])
		return cls.from_dict(peak_dict)

	@classmethod
	def from_mona_dict(cls, mona_data: Dict) -> "ReferenceData":
		"""
		Construct an object from Massbank of North America json data
		that has been loaded into a dictionary.

		:param mona_data: dict
		"""  # noqa: D400

		compound: Dict = mona_data["compound"][0]
		names: List = compound["names"]
		name: str = names[0]["name"]
		synonyms: List = [name for name in names[1:]]

		properties_dict = parse_metadata(mona_data)

		# Remove unwanted properties
		del properties_dict["license"]

		mass_spec = mass_spec_from_mona(mona_data["spectrum"])

		return cls(
				name=name,
				mass_spec=mass_spec,
				synonyms=synonyms,
				**properties_dict,
				)

	def to_msp(self) -> str:
		"""
		Returns the ReferenceData object as an MSP file similar to that produced by
		NIST MS Search's export function.
		"""  # noqa: D400

		if not self.mass_spec:
			raise ValueError("No mass spectrum included in the reference data.")

		normalized_ms = normalize_mass_spec(self.mass_spec, max_intensity=999)
		num_peaks = len(self.mass_spec)

		mz_int_pairs = [f"{mz} {intensity}" for mz, intensity in normalized_ms.iter_peaks()]

		spec_block = []

		for row in list(chunks(mz_int_pairs, 5)):
			spec_block.append("; ".join(x for x in row))

		msp_text = msp_template.render(
				ref_data=self,
				num_peaks=num_peaks,
				spec_block='\n'.join(spec_block),
				)

		return msp_text


@sdjson.register_encoder(ReferenceData)
def encode_reference_data(obj: ReferenceData) -> Dict[str, Any]:
	return obj.to_dict()
