#!/usr/bin/env python
#
#  base.py
"""
Base class for other PyMassSpec NIST Search classes.
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
#

# stdlib
import json
from typing import Any, Dict, Iterator, Tuple, Union

# 3rd party
import sdjson
from chemistry_tools.cas import cas_int_to_string, check_cas_number
from domdf_python_tools.doctools import prettify_docstrings
from numpy import int32, int64, signedinteger
from pyms.json import encode_mass_spec, encode_scan  # noqa

# this package
from pyms_nist_search.utils import parse_name_chars

__all__ = ("NISTBase", )


@prettify_docstrings
class NISTBase:
	"""
	Base class for other PyMassSpec NIST Search classes.

	:param name: The name of the compound.
	:param cas: The CAS number of the compound.
	"""

	def __init__(self, name: str = '', cas: Union[str, int] = "---") -> None:

		self._name: str = str(name)

		if isinstance(cas, int):
			if check_cas_number(cas):
				cas = "---"
			else:
				cas = cas_int_to_string(cas)

		if cas == "0-00-0":
			cas = "---"
		self._cas: str = str(cas)

	@property
	def name(self) -> str:
		"""
		The name of the compound.
		"""

		return self._name

	@property
	def cas(self) -> str:
		"""
		The CAS number of the compound.
		"""

		return self._cas

	@classmethod
	def from_json(cls, json_data):  # noqa: MAN001,MAN002
		"""
		Construct an object from json data.

		:param json_data:
		:type json_data: :class:`str`
		"""

		peak_dict = json.loads(json_data)

		return cls.from_dict(peak_dict)

	@classmethod
	def from_dict(cls, dictionary: Dict[str, Any]):  # noqa: MAN002
		"""
		Construct an object from a dictionary.

		:param dictionary:
		"""

		return cls(**dictionary)

	def to_dict(self) -> Dict[str, Any]:
		"""
		Convert the object to a dictionary.

		.. versionadded:: 0.6.0
		"""

		return dict(
				name=self._name,
				cas=self.cas,
				)

	def to_json(self) -> str:
		"""
		Convert the object to json.
		"""

		return sdjson.dumps(self.to_dict())

	@classmethod
	def from_pynist(cls, pynist_dict: Dict[str, Any]):  # noqa: MAN002
		"""
		Create an object from the raw data returned by the C extension.

		:param pynist_dict:
		"""

		return cls(
				name=parse_name_chars(pynist_dict["hit_name_chars"]),
				cas=cas_int_to_string(pynist_dict["cas_no"]),
				)

	@property
	def __dict__(self):  # noqa: MAN002
		return self.to_dict()

	def __getstate__(self) -> Dict[str, Any]:
		return self.to_dict()

	def __setstate__(self, state) -> None:  # noqa: MAN001
		self.__init__(**state)  # type: ignore[misc]

	def __iter__(self) -> Iterator[Tuple[str, Any]]:
		yield from self.to_dict().items()

	def __str__(self) -> str:
		return self.__repr__()

	def __eq__(self, other) -> bool:  # noqa: MAN001
		if isinstance(other, self.__class__):
			return self.to_dict() == other.to_dict()

		return NotImplemented


@sdjson.register_encoder(int64)
@sdjson.register_encoder(int32)
@sdjson.register_encoder(signedinteger)
def serialise_numpy_int64(value: int) -> int:
	return int(value)
