#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#  utils.py
"""
General utilities
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


def pack(mass_spec, top=20):
	"""
	Convert a pyms.Spectrum.MassSpectrum object into a string.

	Adapted from https://sourceforge.net/projects/mzapi-live/

	:type mass_spec: pyms.Spectrum.MassSpectrum
	:param top: The number of largest peaks to identify
	:type top: int
	
	:rtype: str
	"""
	
	values = list(zip(mass_spec.mass_list, mass_spec.intensity_list))
	
	values.sort(key=lambda s: s[1], reverse=True)
	norm = values[0][1]
	
	spectrum = [(a, 999.0 * b / norm) for (a, b) in values[:top]]
	spectrum.sort()
	return "*".join(["%.2f\t%.2f" % (a, b) for (a, b) in spectrum]) + "*"


def parse_name_chars(name_char_list):
	"""
	Takes a list of Unicode character codes and converts them to characters,
	taking into account the special codes used by the NIST DLL.

	:type name_char_list: list of int

	:return: The parsed name
	:rtype: str
	"""
	
	hit_name = ''
	
	for dec in name_char_list[:-1]:
		if dec == 0:
			break
		
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

