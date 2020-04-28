#!/usr/bin/env python
"""Setup script"""

import pathlib
import sys

from setuptools import Extension, find_packages, setup

print(pathlib.Path.cwd())

copyright = """
2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
"""

VERSION = "0.4.13"

modname = "pyms_nist_search"

short_desc = "PyMassSpec extension for searching mass spectra using NIST's Mass Spectrum Search Engine"

author = "Dominic Davis-Foster"
author_email = "dominic@davis-foster.co.uk"
github_username = "domdfcoding"

classifiers = [
		"Development Status :: 4 - Beta",
		# "Development Status :: 5 - Production/Stable",
		# "Development Status :: 6 - Mature",
		# "Development Status :: 7 - Inactive",

		"Operating System :: Microsoft :: Windows",
		"Operating System :: Microsoft :: Windows :: Windows 10",
		"Operating System :: Microsoft :: Windows :: Windows 7",
		"Operating System :: Microsoft :: Windows :: Windows 8.1",

		"Operating System :: POSIX :: Linux",
		# "Operating System :: OS Independent",

		"Intended Audience :: Developers",
		"Intended Audience :: Science/Research",

		"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",

		"Programming Language :: C",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: Implementation :: CPython",

		# "Topic :: Database :: Front-Ends",
		"Topic :: Scientific/Engineering :: Chemistry",
		"Topic :: Software Development :: Libraries :: Python Modules",
		]


common_kwargs = dict(
		author=author,
		author_email=author_email,
		classifiers=classifiers,
		description=short_desc,
		license='LGPLv3',
		name=modname,
		version=VERSION,
		packages=["pyms_nist_search"],
		package_dir={'pyms_nist_search': 'src/pyms_nist_search'},
		python_requires=">=3.6",
		package_data={modname: ['pyms_nist_search/templates/*']},
		include_package_data=True,
		url=f"https://github.com/{github_username}/{modname}",
		)

if pathlib.Path.cwd().name == "doc-source":
	print(pathlib.Path.cwd().parent / "README.rst")
	install_requires = (pathlib.Path.cwd().parent / "requirements.txt").read_text().split("\n")
	common_kwargs["long_description"] = (pathlib.Path.cwd().parent / "README.rst").read_text() + '\n'
else:
	print(pathlib.Path("README.rst"))
	install_requires = pathlib.Path("requirements.txt").read_text().split("\n")
	common_kwargs["long_description"] = pathlib.Path("README.rst").read_text() + '\n'

docker_only_reqs = [
		"docker>=4.2.0",
		"requests>=2.22.0",
		]

build_macros = [
		('INTERNALBUILD', '1'),
		('WIN32', '1'),
		('MSTXTDATA', '1'),
		]

##############################

if __name__ == '__main__':
	
	if sys.platform == "win32":
		
		if sys.maxsize > 2 ** 32:
			x = 64
			bit = 64
			ctree = "ctNt66_64"
			# libraries = ['src/pyms_nist_search/x64/nistdl64']
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
