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
import base64
import functools
import json
import os
import pathlib
import time
from typing import Callable, List, Optional, Sequence, Tuple, Union

# 3rd party
import docker  # type: ignore[import-untyped]
import docker.errors  # type: ignore[import-untyped]
import requests
import sdjson
from domdf_python_tools.typing import PathLike
from pyms.Spectrum import MassSpectrum

# this package
from pyms_nist_search.reference_data import ReferenceData
from pyms_nist_search.search_result import SearchResult

# this package
from . import _core  # type: ignore[attr-defined]

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
	This can also be performed manually, such as to upgrade to the latest version,
	with the following command:

	.. prompt:: bash

		docker pull domdfcoding/pywine-pyms-nist

	The engine must be uninitialized when no longer required to shut down the underlying docker container.
	This is achieved with the :meth:`uninit() <pyms_nist_search.docker_engine.Engine.uninit>` method.
	Alternatively, this class can be used as a contextmanager to automatically uninitialize the engine
	upon leaving the :keyword:`with` block:

	.. code-block:: python3

		with pyms_nist_search.Engine(
				FULL_PATH_TO_MAIN_LIBRARY,
				pyms_nist_search.NISTMS_MAIN_LIB,
				FULL_PATH_TO_WORK_DIR,
				) as search:
			search.full_spectrum_search(ms, n_hits=5)

	.. versionchanged:: 0.6.0  Added context manager support.

	:param lib_path: The path to the mass spectral library.
	:param lib_type: The type of library. One of ``NISTMS_MAIN_LIB``, ``NISTMS_USER_LIB``, ``NISTMS_REP_LIB``.
	:param work_dir: The path to the working directory.

	.. latex:clearpage::
	"""

	initialised: bool = False

	image_name: str = "domdfcoding/pywine-pyms-nist:latest"
	"""
	The name (and label) of the docker image to use.

	.. versionadded:: 0.8.0
	"""

	def __init__(
			self,
			lib_path: Union[PathLike, Sequence[Tuple[PathLike, int]]],
			lib_type: int = _core.NISTMS_MAIN_LIB,
			work_dir: Optional[PathLike] = None,
			debug: bool = False,
			):

		self.debug: bool = bool(debug)

		parsed_lib_paths, parsed_lib_types = self._parse_lib_paths_and_types(lib_path, lib_type)

		# # Check if the server is already running
		# for container in client.containers.list(all=True, filters={"status": "running"}):
		# 	if container.name == "pyms-nist-server":
		# 		self.docker = container
		# 		break
		# else:
		#

		print("Launching Docker...")

		self._client = docker.from_env()

		self._pull_and_launch(parsed_lib_paths, parsed_lib_types)

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

	def _pull_and_launch(self, lib_paths: List[str], lib_types: List[int]) -> None:
		try:
			self.__launch_container(lib_paths, lib_types)
		except docker.errors.ImageNotFound:
			print("Docker Image not found. Downloading now.")
			self._client.images.pull(self.image_name)
			self.__launch_container(lib_paths, lib_types)

	@staticmethod
	def _parse_lib_paths_and_types(
			lib_path: Union[PathLike, Sequence[Tuple[PathLike, int]]],
			lib_type: int,
			) -> Tuple[List[str], List[int]]:

		if isinstance(lib_path, (str, os.PathLike)):
			if not isinstance(lib_path, pathlib.Path):
				lib_path = pathlib.Path(lib_path)

			if not lib_path.is_dir():
				raise FileNotFoundError(f"Library not found at the given path: {lib_path}")

			if lib_type not in {_core.NISTMS_MAIN_LIB, _core.NISTMS_USER_LIB, _core.NISTMS_REP_LIB}:
				raise ValueError("`lib_type` must be one of NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB.")

			return [str(lib_path)], [lib_type]

		else:
			assert lib_type is _core.NISTMS_MAIN_LIB
			lib_paths = []
			lib_types = []
			libraries: Sequence[Tuple[PathLike, int]] = lib_path
			for library in libraries:
				lib_path = library[0]

				if not isinstance(lib_path, pathlib.Path):
					lib_path = pathlib.Path(lib_path)

				if not lib_path.is_dir():
					raise FileNotFoundError(f"Library not found at the given path: {lib_path}")

				lib_paths.append(str(lib_path))
				lib_type = library[1]
				if lib_type not in {_core.NISTMS_MAIN_LIB, _core.NISTMS_USER_LIB, _core.NISTMS_REP_LIB}:
					raise ValueError("`lib_type` must be one of NISTMS_MAIN_LIB, NISTMS_USER_LIB, NISTMS_REP_LIB.")
				lib_types.append(lib_type)

			return lib_paths, lib_types

	def __launch_container(self, lib_paths: List[str], lib_types: List[int]) -> None:
		volumes = {}
		lib_names = []

		for library in lib_paths:
			lib_name = os.path.split(library)[-1]
			lib_names.append(f"Z:\\{lib_name}")
			volumes[library] = {"bind": f"/{lib_name}", "mode": "ro"}

		configdata = {
				"lib_paths": lib_names,
				"lib_types": [lt for lt in lib_types],
				}

		config_b64 = base64.b64encode(json.dumps(configdata).encode("UTF-8")).decode("UTF-8")

		self.docker = self._client.containers.run(
				self.image_name,
				ports={5001: 5001},
				detach=True,
				name="pyms-nist-server",
				# remove=True,
				# stdout=False,
				# stderr=False,
				stdin_open=False,
				volumes=volumes,
				# environment=[f"LIBPATHS={lib_paths_packed!r}", f"LIBTYPES={lib_types.decode('UTF-8')!r}", f"NUM_LIBS={num_libs}"],
				environment=[f"CONFIG={config_b64}"]
				)

	def __enter__(self) -> "Engine":
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.uninit()

	def uninit(self) -> None:
		"""
		Uninitialize the Search Engine.

		.. latex:clearpage::
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

	@staticmethod
	def cas_search(cas: str) -> List[SearchResult]:
		"""
		Search for a compound by CAS number.

		.. note:: This function does not appear to work with user libraries converted using LIB2NIST.

		:param cas:

		:return: List of results for CAS number (usually just one result).
		"""

		retry_count = 0

		# Keep trying until it works
		while retry_count < 240:
			try:
				res = requests.post(f"http://localhost:5001/search/cas/{cas}")
				res.raise_for_status()
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

		:return: List of tuples containing possible identities
			for the mass spectrum, and the reference data.

		.. latex:clearpage::
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

	@require_init
	def get_lib_paths(self) -> List[str]:
		"""
		Returns the list of library names currently in use.
		"""

		retry_count = 0

		# Keep trying until it works
		while retry_count < 240:
			try:
				res = requests.get(f"http://localhost:5001/info/lib_paths")
				res.raise_for_status()
				assert isinstance(res.json(), list)
				return res.json()
			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1

		raise TimeoutError("Unable to communicate with the search server.")

	@require_init
	def get_active_libs(self) -> List[int]:
		"""
		Returns the active librararies, as their (zero-based) indices in the output of :meth:~.WinEngine.get_lib_names()`.
		"""

		retry_count = 0

		# Keep trying until it works
		while retry_count < 240:
			try:
				res = requests.get(f"http://localhost:5001/info/active_libs")
				res.raise_for_status()
				assert isinstance(res.json(), list)
				return res.json()
			except requests.exceptions.ConnectionError:
				time.sleep(0.5)
				retry_count += 1

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
