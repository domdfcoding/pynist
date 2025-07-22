#!/usr/bin/env python
#
#  __init__.py
"""
PyMassSpec extension for searching mass spectra using NIST's Mass Spectrum Search Engine.
"""
#
#  This file is part of PyMassSpec NIST Search
#  Python interface to the NIST MS Search DLL
#
#  Copyright (c) 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import os
import pathlib
import platform
import sys

if sys.platform == "win32":
	if sys.version_info < (3, 8):

		python_base_dir = pathlib.Path(__file__).parent.parent.parent.parent
		# assert (python_base_dir / "nistdl64.dll").is_file()
		# assert (python_base_dir / "ctNt66_64.dll").is_file()
		if not str(python_base_dir.absolute()) in os.environ["PATH"].split(':'):
			os.environ["PATH"] += os.pathsep + str(python_base_dir.absolute())
		del python_base_dir

	else:
		_64_bit = platform.architecture()[0] == "64bit"
		os.add_dll_directory(os.path.join(os.path.split(__file__)[0], "x64" if _64_bit else "x86"))

# this package
from pyms_nist_search.reference_data import ReferenceData  # noqa: F401
from pyms_nist_search.search_result import SearchResult  # noqa: F401

# this package
from ._core import *  # noqa: F401

if sys.platform == "win32":
	# this package
	from pyms_nist_search.win_engine import Engine

else:
	# this package
	from pyms_nist_search.docker_engine import Engine  # noqa: F401

name: str = "PyMassSpec NIST Search"
__author__: str = "Dominic Davis-Foster"
__license__: str = "LGPLv3+"
__maintainer_email__: str = "dominic@davis-foster.co.uk"
__version__: str = "0.8.0"

__copyright__: str = "2020 Dominic Davis-Foster"
__email__: str = "dominic@davis-foster.co.uk"
