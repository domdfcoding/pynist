#!/usr/bin/env python
#
#  search_result.py
"""
Class to store search results from NIST MS Search.
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
from typing import Any, Dict, Union

# 3rd party
from domdf_python_tools.doctools import prettify_docstrings
from sdjson import register_encoder

# this package
from pyms_nist_search.base import NISTBase
from pyms_nist_search.utils import parse_name_chars

__all__ = ["SearchResult"]


@prettify_docstrings
class SearchResult(NISTBase):
	"""
	Class to store search results from NIST MS Search.

	:param name: The name of the compound
	:param cas: The CAS number of the compound
	:param match_factor:
	:param reverse_match_factor:
	:param hit_prob:
	:param spec_loc: The location of the reference spectrum in the library.
	:param lib_idx: The (zero-based) index of the library the result was found in (see :meth:`~.WinEngine.get_lib_names()`).

	.. latex:vspace:: 20px
	"""

	def __init__(
			self,
			name: str = '',
			cas: Union[str, int] = "---",
			match_factor: float = 0,
			reverse_match_factor: float = 0,
			hit_prob: float = 0.0,
			spec_loc: float = 0,
			lib_idx: int = 0,
			) -> None:
		NISTBase.__init__(self, name, cas)

		self._match_factor: int = int(match_factor)
		self._reverse_match_factor: int = int(reverse_match_factor)

		self._hit_prob: float = float(hit_prob)
		self._spec_loc: int = int(spec_loc)
		self._lib_idx: int = int(lib_idx)

	@property
	def match_factor(self) -> int:
		"""
		Returns a score (out of 1000) representing the similarity of the searched
		mass spectrum to the search result.
		"""  # noqa: D400

		return int(self._match_factor)

	@property
	def reverse_match_factor(self) -> int:
		"""
		A score (out of 1000) representing the similarity of the searched
		mass spectrum to the search result, but ignoring any peaks that are in
		the searched mass spectrum but not in the library spectrum.
		"""  # noqa: D400

		return int(self._reverse_match_factor)

	@property
	def hit_prob(self) -> float:
		"""
		Returns the probability of the hit being the compound responsible for the mass spectrum.
		"""

		return float(self._hit_prob)

	@property
	def spec_loc(self) -> int:
		"""
		The location of the reference spectrum in the library.

		This can then be searched using the :meth:`~pynist.win_engine.Engine.get_reference_data` method of the
		search engine to obtain the reference data.
		"""

		return int(self._spec_loc)

	@property
	def lib_idx(self) -> int:
		"""
		The (zero-based) index of the library the result was found in (see :meth:`~.WinEngine.get_lib_names()`).
		"""

		return int(self._lib_idx)

	@classmethod
	def from_pynist(cls, pynist_dict: Dict[str, Any]) -> "SearchResult":
		"""
		Create a :class:`~.SearchResult` object from the raw data returned by the C extension.

		:param pynist_dict:
		"""

		return cls(
				name=parse_name_chars(pynist_dict["hit_name_chars"]),
				cas=pynist_dict["cas_no"],
				match_factor=pynist_dict["sim_num"],
				reverse_match_factor=pynist_dict["rev_sim_num"],
				hit_prob=pynist_dict["hit_prob"] / 100,
				spec_loc=pynist_dict["spec_loc"],
				lib_idx=pynist_dict["lib_idx"],
				)

	def __repr__(self) -> str:
		return f"Search Result: {self.name} \t({self.match_factor})"

	def to_dict(self) -> Dict[str, Any]:
		"""
		Convert the object to a dictionary.

		.. versionadded:: 0.6.0
		"""

		return dict(
				name=self._name,
				cas=self.cas,
				match_factor=self.match_factor,
				reverse_match_factor=self.reverse_match_factor,
				spec_loc=self.spec_loc,
				hit_prob=self.hit_prob,
				lib_idx=self.lib_idx,
				)

	@property
	def __dict__(self):  # noqa: MAN002
		return self.to_dict()


@register_encoder(SearchResult)
def encode_search_result(obj: SearchResult) -> Dict[str, Any]:
	return obj.to_dict()
