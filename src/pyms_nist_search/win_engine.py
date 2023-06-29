#!/usr/bin/env python
#
#  pynist_search_server.py
"""
Search engine for Windows systems.
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
import atexit
import pathlib
from typing import List, Optional, Tuple

# 3rd party
from domdf_python_tools.typing import PathLike
from pyms.Spectrum import MassSpectrum  # type: ignore

# this package
# from ._core import *  # type: ignore
from pyms_nist_search.reference_data import ReferenceData
from pyms_nist_search.search_result import SearchResult
from pyms_nist_search.utils import pack

# this package
from . import _core

__all__ = ("Engine", )


class Engine:
	"""
	Search engine for Windows systems.

	.. TODO::

		Search by Name. See page 13 of the documentation.
		Would also like to search by CAS number but DLL doesn't seem to support that.

	:param lib_path: The path to the mass spectral library.
	:param lib_type: The type of library. One of ``NISTMS_MAIN_LIB``, ``NISTMS_USER_LIB``, ``NISTMS_REP_LIB``.
	:param work_dir: The path to the working directory.

	.. latex:vspace:: 50px
	"""

	def __init__(
			self,
			lib_path: PathLike,
			lib_type: int = _core.NISTMS_MAIN_LIB,
			work_dir: Optional[PathLike] = None,
			debug: bool = False,
			):
		if not isinstance(lib_path, pathlib.Path):
			lib_path = pathlib.Path(lib_path)

		if work_dir is None:
			work_dir = pathlib.Path.cwd()
		elif not isinstance(work_dir, pathlib.Path):
			work_dir = pathlib.Path(work_dir)

		# Create work_dir if it doesn't exist
		if not work_dir.is_dir():
			work_dir.mkdir()

		if not lib_path.is_dir():
			raise FileNotFoundError(f"Library not found at the given path: {lib_path}")

		if lib_type not in {_core.NISTMS_MAIN_LIB, _core.NISTMS_USER_LIB, _core.NISTMS_REP_LIB}:
			raise ValueError("`lib_type` must be one of NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB.")

		self.debug = debug

		_core._init_api(str(lib_path), lib_type, str(work_dir))

		atexit.register(self.uninit)

	def uninit(self) -> None:
		"""
		Uninitialize the Search Engine.
		"""

	@staticmethod
	def spectrum_search(mass_spec: MassSpectrum, n_hits: int = 5) -> List[SearchResult]:
		"""
		Perform a Quick Spectrum Search of the mass spectral library.

		:param mass_spec: The mass spectrum to search against the library.
		:param n_hits: The number of hits to return.

		:return: List of possible identities for the mass spectrum.
		"""

		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")

		hit_list = _core._spectrum_search(pack(mass_spec, len(mass_spec)))[:n_hits]

		return [SearchResult.from_pynist(hit) for hit in hit_list]

	@staticmethod
	def full_spectrum_search(mass_spec: MassSpectrum, n_hits: int = 5) -> List[SearchResult]:
		"""
		Perform a Full Spectrum Search of the mass spectral library.

		:param mass_spec: The mass spectrum to search against the library.
		:param n_hits: The number of hits to return.

		:return: List of possible identities for the mass spectrum.
		"""

		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")

		hit_list = _core._full_spectrum_search(pack(mass_spec, len(mass_spec)))[:n_hits]

		return [SearchResult.from_pynist(hit) for hit in hit_list]

	def full_search_with_ref_data(
			self,
			mass_spec: MassSpectrum,
			n_hits: int = 5,
			) -> List[Tuple[SearchResult, ReferenceData]]:
		"""
		Perform a Full Spectrum Search of the mass spectral library, including reference data.

		:param mass_spec: The mass spectrum to search against the library.
		:param n_hits: The number of hits to return.

		:return: List of tuples containing possible identities
			for the mass spectrum, and the reference data
		"""

		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")

		hit_list = self.full_spectrum_search(mass_spec, n_hits)

		output_buffer = []

		for idx, hit in enumerate(hit_list):
			ref_data = self.get_reference_data(hit.spec_loc)
			output_buffer.append((hit, ref_data))

		return output_buffer

	@staticmethod
	def get_reference_data(spec_loc: int) -> ReferenceData:
		"""
		Get reference data from the library for the compound at the given location.

		:param spec_loc:
		"""

		reference_data = _core._get_reference_data(spec_loc)

		return ReferenceData.from_pynist(reference_data)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.uninit()
