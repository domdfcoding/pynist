#!/usr/bin/env python
#
#  docker_engine.py
"""
Search engine for Linux and other platforms supporting Docker.
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
import atexit
import functools
import json
import pathlib
import time
from typing import Callable, List, Optional, Tuple

# 3rd party
import docker  # type: ignore
import docker.errors  # type: ignore
import requests
import sdjson
from domdf_python_tools.typing import PathLike
from pyms.Spectrum import MassSpectrum  # type: ignore

# this package
from pyms_nist_search.reference_data import ReferenceData
from pyms_nist_search.search_result import SearchResult

# this package
from ._core import NISTMS_MAIN_LIB, NISTMS_REP_LIB, NISTMS_USER_LIB  # type: ignore

client = docker.from_env()

__all__ = [
		"require_init",
		"Engine",
		"hit_list_from_json",
		"hit_list_with_ref_data_from_json",
		]


def require_init(func: Callable) -> Callable:
	"""
	Decorator to ensure that functions do not run after the class has been uninitialised.

	:param func: The function or method to wrap.
	"""

	@functools.wraps(func)
	def wrapper(cls, *args, **kwargs) -> Callable:
		if not cls.initialised:
			raise RuntimeError(
					"""The Search Engine has been uninitialised!
Please create a new instance of the Search Engine and try again."""
					)

		return func(cls, *args, **kwargs)

	return wrapper


class Engine:
	"""
	Search engine for Linux and other platforms supporting Docker.

	The first time the engine is initialized it will download the latest
	version of the docker image automatically.

	This can also be done manually, such as to upgrade to the latest version,
	with the following command:

	.. prompt:: bash

		docker pull domdfcoding/pywine-pyms-nist

	"""

	initialised: bool

	def __init__(
			self,
			lib_path: PathLike,
			lib_type: int = NISTMS_MAIN_LIB,
			work_dir: Optional[PathLike] = None,
			debug: bool = False,
			):
		"""
		:param lib_path: The path to the mass spectral library.
		:param lib_type: The type of library. One of NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB.
		:param work_dir: The path to the working directory.
		"""

		if not isinstance(lib_path, pathlib.Path):
			lib_path = pathlib.Path(lib_path)

		if not lib_path.is_dir():
			raise FileNotFoundError(f"Library not found at the given path: {lib_path}")

		if lib_type not in {NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB}:
			raise ValueError("`lib_type` must be one of NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB.")

		# # Check if the server is already running
		# for container in client.containers.list(all=True, filters={"status": "running"}):
		# 	if container.name == "pyms-nist-server":
		# 		self.docker = container
		# 		break
		# else:
		#

		self.debug: bool = bool(debug)

		print("Launching Docker...")

		try:
			self.__launch_container(lib_path, lib_type)
		except docker.errors.ImageNotFound:
			print("Docker Image not found. Downloading now.")
			client.images.pull("domdfcoding/pywine-pyms-nist")
			self.__launch_container(lib_path, lib_type)

		atexit.register(self.uninit)

		retry_count = 0

		# Wait for server to come online
		while retry_count < 240:
			try:
				if requests.get("http://localhost:5001/").text == "ready":
					self.initialised = True
					return

			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1

		raise TimeoutError("Unable to communicate with the search server.")

	def __launch_container(self, lib_path, lib_type):
		self.docker = client.containers.run(
				"domdfcoding/pywine-pyms-nist",
				ports={5001: 5001},
				detach=True,
				name="pyms-nist-server",
				# remove=True,
				# stdout=False,
				# stderr=False,
				stdin_open=False,
				volumes={lib_path: {"bind": "/mainlib", "mode": "ro"}},
				environment=[f"LIBTYPE={lib_type}"],
				)

	def uninit(self) -> None:
		"""
		Uninitialize the Search Engine.
		"""

		if self.initialised:

			print("Shutting down docker server")

			if self.debug:
				print("Server log follows:")
				print(self.docker.logs(timestamps=True).decode("utf-8"))

			try:
				self.docker.stop()
				self.docker.remove()
			except docker.errors.NotFound:
				print("Unable to shut down the docker server")

			self.initialised = False

	@require_init
	def spectrum_search(self, mass_spec: MassSpectrum, n_hits: int = 5) -> List[SearchResult]:
		"""
		Perform a Quick Spectrum Search of the mass spectral library.

		:param mass_spec: The mass spectrum to search against the library.
		:param n_hits: The number of hits to return.

		:return: List of possible identities for the mass spectrum.
		"""

		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")

		retry_count = 0

		# Keep trying until it works
		while retry_count < 240:
			try:
				res = requests.post(
						f"http://localhost:5001/search/quick/?n_hits={n_hits}",
						json=sdjson.dumps(mass_spec),
						)
				print(res.text)
				return hit_list_from_json(res.text)

			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1

		raise TimeoutError("Unable to communicate with the search server.")

	@require_init
	def full_spectrum_search(
			self,
			mass_spec: MassSpectrum,
			n_hits: int = 5,
			) -> List[SearchResult]:
		"""
		Perform a Full Spectrum Search of the mass spectral library.

		:param mass_spec: The mass spectrum to search against the library.
		:param n_hits: The number of hits to return.

		:return: List of possible identities for the mass spectrum.
		"""

		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")

		retry_count = 0

		# Keep trying until it works
		while retry_count < 240:
			try:
				res = requests.post(
						f"http://localhost:5001/search/spectrum/?n_hits={n_hits}", json=sdjson.dumps(mass_spec)
						)
				return hit_list_from_json(res.text)

			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1

		raise TimeoutError("Unable to communicate with the search server.")

	@require_init
	def full_search_with_ref_data(
			self,
			mass_spec: MassSpectrum,
			n_hits: int = 5,
			) -> List[Tuple[SearchResult, ReferenceData]]:
		"""
		Perform a Full Spectrum Search of the mass spectral library, including reference data.

		:param mass_spec: The mass spectrum to search against the library.
		:param n_hits: The number of hits to return.

		:return: List of tuples consisting of the possible identities
			for the mass spectrum and the reference data from the library.
		"""

		if not isinstance(mass_spec, MassSpectrum):
			raise TypeError("`mass_spec` must be a pyms.Spectrum.MassSpectrum object.")

		retry_count = 0

		# Keep trying until it works
		while retry_count < 240:
			try:
				res = requests.post(
						f"http://localhost:5001/search/spectrum_with_ref_data/?n_hits={n_hits}",
						json=sdjson.dumps(mass_spec)
						)
				return hit_list_with_ref_data_from_json(res.text)
			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1

		raise TimeoutError("Unable to communicate with the search server.")

	@require_init
	def get_reference_data(self, spec_loc: int) -> ReferenceData:
		"""
		Get reference data from the library for the compound at the given location.

		:param spec_loc:
		"""

		retry_count = 0

		# Keep trying until it works
		while retry_count < 240:
			try:
				res = requests.post(f"http://localhost:5001/search/loc/{spec_loc}")
				return ReferenceData(**json.loads(res.text))

			except requests.exceptions.ConnectionError:
				time.sleep(0.5)

		raise TimeoutError("Unable to communicate with the search server.")


def hit_list_from_json(json_data: str) -> List[SearchResult]:
	"""
	Parse json data into a list of SearchResult objects.

	:param json_data: str
	"""

	raw_output = json.loads(json_data)

	hit_list = []

	for hit in raw_output:
		hit_list.append(SearchResult(**hit))

	return hit_list


def hit_list_with_ref_data_from_json(json_data: str) -> List[Tuple[SearchResult, ReferenceData]]:
	"""
	Parse json data into a list of (SearchResult, ReferenceData) tuples.

	:param json_data: str
	"""

	raw_output = json.loads(json_data)

	hit_list = []

	for hit, ref_data in raw_output:
		hit_list.append((SearchResult(**hit), ReferenceData(**ref_data)))

	return hit_list
