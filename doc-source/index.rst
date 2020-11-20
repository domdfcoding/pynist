========================
PyMassSpec NIST Search
========================

.. start short_desc

**PyMassSpec extension for searching mass spectra using NIST's Mass Spectrum Search Engine**

.. end short_desc

.. image:: https://ci.appveyor.com/api/projects/status/82cs9prucypd1igb?svg=true
	:target: https://ci.appveyor.com/project/domdfcoding/pyms-nist-search/branch/master
	:alt: Windows Build Status

.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |travis| |actions_windows| |coveralls| |codefactor| |pre_commit_ci|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires| |pre_commit|

.. |docs| rtfd-shield::
	:project: pynist
	:alt: Documentation Build Status

.. |docs_check| actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status

.. |travis| actions-shield::
	:workflow: Linux Tests
	:alt: Linux Test Status

.. |actions_windows| actions-shield::
	:workflow: Windows Tests
	:alt: Windows Test Status

.. |requires| requires-io-shield::
	:alt: Requirements Status

.. |coveralls| coveralls-shield::
	:alt: Coverage

.. |codefactor| codefactor-shield::
	:alt: CodeFactor Grade

.. |pypi-version| pypi-shield::
	:project: pyms-nist-search
	:version:
	:alt: PyPI - Package Version

.. |supported-versions| pypi-shield::
	:project: pyms-nist-search
	:py-versions:
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| pypi-shield::
	:project: pyms-nist-search
	:implementations:
	:alt: PyPI - Supported Implementations

.. |wheel| pypi-shield::
	:project: pyms-nist-search
	:wheel:
	:alt: PyPI - Wheel

.. |license| github-shield::
	:license:
	:alt: License

.. |language| github-shield::
	:top-language:
	:alt: GitHub top language

.. |commits-since| github-shield::
	:commits-since: v0.4.14
	:alt: GitHub commits since tagged version

.. |commits-latest| github-shield::
	:last-commit:
	:alt: GitHub last commit

.. |maintained| maintained-shield:: 2020
	:alt: Maintenance

.. |pre_commit| pre-commit-shield::
	:alt: pre-commit

.. |pre_commit_ci| pre-commit-ci-shield::
	:alt: pre-commit.ci status

.. end shields


PyMassSpec extension for searching mass spectra using NIST's Spectrum Search Engine

PyMassSpec NIST Search is Free Software licensed under the `GNU Lesser General Public License Version 3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_

A copy of the MassBank of North America database, in JSON, MSP and NIST Library formats, is included for the purposes of these tests.
This library was created on 22 April 2020 using the "parse_mona_json.py" script and Lib2Nist.
Licensed under the CC BY 4.0 License.
For a list of contributors, see the file `MoNA_GCMS_Library/AUTHORS`
.. TODO: add links.

Installation
--------------

.. begin installation
.. end installation


Usage
--------

You will need to supply your own copy of the NIST Mass Spectral library to use this software.

The main class in this library is the `Engine` class. This class performs the actual searching. Start by initialising the search engine as follows:

.. code-block:: python

	search = pyms_nist_search.Engine(
			FULL_PATH_TO_MAIN_LIBRARY,
			pyms_nist_search.NISTMS_MAIN_LIB,
			FULL_PATH_TO_WORK_DIR,
			)

Where ``FULL_PATH_TO_MAIN_LIBRARY`` is the path to the location of your mass spectral library, and ``FULL_PATH_TO_WORK_DIR`` is the path to the working directory to be used by the search engine.

A `MassSpectrum` object can then be searched as follows:

.. code-block:: python

	search.full_search_with_ref_data(mass_spec)

This will return a list of tuples consisting of `SearchResult` and `ReferenceData` objects for the possible identities of the mass spectrum.

A list of just the `SearchResult` objects can be obtained with this method:

.. code-block:: python

	hit_list = search.full_search(mass_spec)

For each of these hits, the reference data can be obtained as follows:

.. code-block:: python

	for hit in hit_list:
		ref_data = search.get_reference_data(hit.spec_loc)


TODO
-----

1. Write comprehensive tests using pytest


|browse_github|

.. toctree::
    :maxdepth: 3
    :caption: Documentation

    docs
    Source
    Building


.. start links

View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

`Browse the GitHub Repository <https://github.com/domdfcoding/pynist>`__

.. end links
