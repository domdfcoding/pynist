#!/usr/bin/env python
#
#  utils.py
"""
General utilities.
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
#

# stdlib
import ntpath
import warnings
from typing import Sequence

# 3rd party
from domdf_python_tools.typing import PathLike
from pyms.Spectrum import MassSpectrum

__all__ = ["pack", "parse_name_chars", "lib_name_from_path"]


def pack(mass_spec: MassSpectrum, top: int = 20) -> str:
	"""
	Convert a pyms.Spectrum.MassSpectrum object into a string.

	Adapted from https://sourceforge.net/projects/mzapi-live/

	:param mass_spec:
	:param top: The number of largest peaks to identify
	"""

	values = list(zip(mass_spec.mass_list, mass_spec.intensity_list))

	values.sort(key=lambda s: s[1], reverse=True)
	norm = values[0][1]

	spectrum = [(a, 999.0 * b / norm) for (a, b) in values[:top]]
	spectrum.sort()

	return '*'.join([f"{a:.2f}\t{b:.2f}" for (a, b) in spectrum]) + '*'


def parse_name_chars(name_char_list: Sequence[int]) -> str:
	"""
	Takes a list of Unicode character codes and converts them to characters,
	taking into account the special codes used by the NIST DLL.

	:param name_char_list:

	:return: The parsed name.
	"""  # noqa: D400

	hit_name = ''
	errors = []  # Buffer the errors to display at the end

	# TODO: can we do away with the -1?
	for dec in name_char_list[:-1]:
		if dec == 0:
			break

		if dec == 224:
			char = 'α'
		elif dec == 225:
			char = 'β'
		elif dec == 231:
			char = 'γ'
		elif dec == 235:
			char = 'δ'
		elif dec == 238:
			char = 'ε'
		elif dec == 227:
			char = 'π'
		elif dec == 229:
			char = 'σ'
		elif dec == 230:
			char = 'μ'
		elif dec == 234:
			char = 'ω'
		elif dec == 241:
			char = '±'
		elif dec == 252:
			char = 'η'
		else:
			try:
				char = chr(dec)
			except ValueError:
				errors.append(dec)
				# print(f"Unable to parse character with code {dec}")
				char = '�'

				# List of problem codes encountered so far:
				# -26, which should be a μ (03BC)

		if char != '\x00':
			hit_name += char

	if errors:
		warnings.warn(f"Unable to parse the following character codes for string {hit_name}: {errors}.")

	return hit_name


def lib_name_from_path(lib_path: PathLike) -> str:
	"""
	Given the path to a mass spectral library, returns the library name (the final path component).
	"""

	return ntpath.split(lib_path)[-1]
