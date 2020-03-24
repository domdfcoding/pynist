#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
#  cas.py
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


# TODO: Use chemistry_tools>=0.2.1 in place of this


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
	
	if check_cas_number(cas_no):
		raise ValueError(
				f"Invalid CAS Number. Check digit mismatch: expected {check_digit}, computed {check_cas_number(cas_no) + check_digit}.")
	
	main_value = (cas_no - check_digit) // 10
	block_2 = main_value % 100
	block_1 = (main_value - block_2) // 100
	
	return f"{block_1}-{block_2}-{check_digit}"


def check_cas_number(cas_no):
	"""
	Checks the CAS number to ensure the check digit is valid
	with respect to the rest of the number.
	
	If the CAS number is valid 0 is returned. If there is a problem the difference
	between the computed check digit and that given as part of the CAS number
	is returned.
	"""
	
	cas_no = int(cas_no)
	
	check_digit = cas_no % 10
	main_value = (cas_no - check_digit) // 10
	block_2 = main_value % 100
	block_1 = (main_value - block_2) // 100
	
	last_digit = block_2 % 10
	
	check_total = last_digit + (((block_2 - last_digit) // 10) * 2)
	
	for position, digit in enumerate(str(block_1)[::-1]):
		check_total += int(digit) * (position + 3)
	
	if check_digit == check_total % 10:
		return 0
	else:
		return (check_total % 10) - check_digit


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
	
	check_digit = int(check_digit)

	block_1 = int(block_1) * 1000
	block_2 = int(block_2) * 10
	
	cas_no = block_1 + block_2 + check_digit
	
	if check_cas_number(cas_no):
		raise ValueError(
				f"Invalid CAS Number. Check digit mismatch: expected {check_digit}, computed {check_cas_number(cas_no) + check_digit}.")
	
	return cas_no

