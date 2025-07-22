========================
PyMassSpec NIST Search
========================

.. start short_desc

**PyMassSpec extension for searching mass spectra using NIST's Mass Spectrum Search Engine.**

.. end short_desc

.. image:: https://img.shields.io/appveyor/build/domdfcoding/pyms-nist-search/master?logo=appveyor
	:target: https://ci.appveyor.com/project/domdfcoding/pyms-nist-search/branch/master
	:alt: AppVeyor Windows Build Status

.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |actions_linux| |actions_windows| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/pynist/latest?logo=read-the-docs
	:target: https://pynist.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/domdfcoding/pynist/workflows/Docs%20Check/badge.svg
	:target: https://github.com/domdfcoding/pynist/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/domdfcoding/pynist/workflows/Linux/badge.svg
	:target: https://github.com/domdfcoding/pynist/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/domdfcoding/pynist/workflows/Windows/badge.svg
	:target: https://github.com/domdfcoding/pynist/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_flake8| image:: https://github.com/domdfcoding/pynist/workflows/Flake8/badge.svg
	:target: https://github.com/domdfcoding/pynist/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/domdfcoding/pynist/workflows/mypy/badge.svg
	:target: https://github.com/domdfcoding/pynist/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://dependency-dash.repo-helper.uk/github/domdfcoding/pynist/badge.svg
	:target: https://dependency-dash.repo-helper.uk/github/domdfcoding/pynist/
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/domdfcoding/pynist/master?logo=coveralls
	:target: https://coveralls.io/github/domdfcoding/pynist?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/pynist?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/pynist
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/pyms-nist-search
	:target: https://pypi.org/project/pyms-nist-search/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/pyms-nist-search?logo=python&logoColor=white
	:target: https://pypi.org/project/pyms-nist-search/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/pyms-nist-search
	:target: https://pypi.org/project/pyms-nist-search/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/pyms-nist-search
	:target: https://pypi.org/project/pyms-nist-search/
	:alt: PyPI - Wheel

.. |license| image:: https://img.shields.io/github/license/domdfcoding/pynist
	:target: https://github.com/domdfcoding/pynist/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/pynist
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/pynist/v0.8.0
	:target: https://github.com/domdfcoding/pynist/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/pynist
	:target: https://github.com/domdfcoding/pynist/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2025
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/pyms-nist-search
	:target: https://pypi.org/project/pyms-nist-search/
	:alt: PyPI - Downloads

.. end shields


PyMassSpec extension for searching mass spectra using NIST's Spectrum Search Engine

PyMassSpec NIST Search is Free Software licensed under the `GNU Lesser General Public License Version 3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_

A copy of the MassBank of North America database, in JSON, MSP and NIST Library formats, is included for the purposes of these tests.
This library was created on 22 April 2020 using the "parse_mona_json.py" script and Lib2Nist.
Licensed under the CC BY 4.0 License.
For a list of contributors, see the file ``MoNA_GCMS_Library/AUTHORS``

.. TODO: add links.

Installation
--------------

.. begin installation
.. end installation


Usage
--------

You will need to supply your own copy of the NIST Mass Spectral library to use this software.

The main class in this library is the ``Engine`` class. This class performs the actual searching. Start by initialising the search engine as follows:

.. code-block:: python

	search = pyms_nist_search.Engine(
			FULL_PATH_TO_MAIN_LIBRARY,
			pyms_nist_search.NISTMS_MAIN_LIB,
			FULL_PATH_TO_WORK_DIR,
			)

Where ``FULL_PATH_TO_MAIN_LIBRARY`` is the path to the location of your mass spectral library, and ``FULL_PATH_TO_WORK_DIR`` is the path to the working directory to be used by the search engine.

A ``MassSpectrum`` object can then be searched as follows:

.. code-block:: python

	search.full_search_with_ref_data(mass_spec)

This will return a list of tuples consisting of ``SearchResult`` and ``ReferenceData`` objects for the possible identities of the mass spectrum.

A list of just the ``SearchResult`` objects can be obtained with this method:

.. code-block:: python

	hit_list = search.full_search(mass_spec)

For each of these hits, the reference data can be obtained as follows:

.. code-block:: python

	for hit in hit_list:
		ref_data = search.get_reference_data(hit.spec_loc)


TODO
-----

1. Write comprehensive tests using pytest
