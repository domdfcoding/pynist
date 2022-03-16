#!/usr/bin/env python

# stdlib
import pathlib
import shutil
import sys

# 3rd party
from setuptools import Extension, setup

sys.path.append('.')

common_kwargs = dict(
		description="PyMassSpec extension for searching mass spectra using NIST's Mass Spectrum Search Engine.",
		packages=["pyms_nist_search"],
		package_dir={"pyms_nist_search": "src/pyms_nist_search"},
		# package_data={modname: ["pyms_nist_search/templates/*"]},
		)

docker_only_reqs = [
		"docker>=4.2.0",
		"requests>=2.22.0",
		]

build_macros = [
		("INTERNALBUILD", "1"),
		("WIN32", "1"),
		("MSTXTDATA", "1"),
		]


extras_require = {}

repo_root = pathlib.Path(__file__).parent
install_requires = (repo_root / "requirements.txt").read_text(encoding="UTF-8").split('\n')

##############################


if sys.platform == "win32":

	if sys.maxsize > 2 ** 32:
		x = 64
		bit = 64
		ctree = "ctNt66_64"
	# libraries = ["src/pyms_nist_search/x64/nistdl64']
	# data_files = [('', ['src/pyms_nist_search/x64/nistdl64.dll', 'src/pyms_nist_search/x64/ctNt66_64.dll'])]
	else:
		x = 86
		bit = 32
		ctree = "ctNt66"
	# libraries = ['src/pyms_nist_search/x86/nistdl32']
	# data_files = [('', ['src/pyms_nist_search/x86/nistdl32.dll', 'src/pyms_nist_search/x86/ctNt66.dll'])]
	libraries = [f'src/pyms_nist_search/x{x}/nistdl{bit}']
	data_files = [('', [f'src/pyms_nist_search/x{x}/nistdl{bit}.dll', f'src/pyms_nist_search/x{x}/{ctree}.dll'])]

	extension = Extension(
			name='pyms_nist_search._core',
			define_macros=build_macros,
			libraries=libraries,
			sources=['src/pyms_nist_search/pyms_nist_search.c'],
			include_dirs=["src/pyms_nist_search"],
			language="c",
			)

	setup(
			**common_kwargs,
			install_requires=[req for req in install_requires if req not in docker_only_reqs],
			ext_modules=[extension],
			data_files=data_files
			)

else:
	# On platforms other than windows, build the minimal C extension that just contains the variables,
	# as well as the Python files that are required for cross compatibility.

	min_extension = Extension(
			name='pyms_nist_search._core',
			define_macros=build_macros,
			sources=['src/pyms_nist_search/pyms_nist_search_min.c'],
			include_dirs=["src/pyms_nist_search"],
			)

	setup(
			**common_kwargs,
			install_requires=install_requires,
			ext_modules=[min_extension],
			)


shutil.rmtree("pyms_nist_search.egg-info", ignore_errors=True)
