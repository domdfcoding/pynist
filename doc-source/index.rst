========================
PyMassSpec NIST Search
========================

.. start short_desc

.. documentation-summary::
	:meta:

.. end short_desc

.. only:: html

	.. image:: https://img.shields.io/appveyor/build/domdfcoding/pyms-nist-search/master?logo=appveyor
		:target: https://ci.appveyor.com/project/domdfcoding/pyms-nist-search/branch/master
		:alt: AppVeyor Windows Build Status

.. start shields

.. only:: html

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

	.. |docs| rtfd-shield::
		:project: pynist
		:alt: Documentation Build Status

	.. |docs_check| actions-shield::
		:workflow: Docs Check
		:alt: Docs Check Status

	.. |actions_linux| actions-shield::
		:workflow: Linux
		:alt: Linux Test Status

	.. |actions_windows| actions-shield::
		:workflow: Windows
		:alt: Windows Test Status

	.. |actions_flake8| actions-shield::
		:workflow: Flake8
		:alt: Flake8 Status

	.. |actions_mypy| actions-shield::
		:workflow: mypy
		:alt: mypy status

	.. |requires| image:: https://dependency-dash.repo-helper.uk/github/domdfcoding/pynist/badge.svg
		:target: https://dependency-dash.repo-helper.uk/github/domdfcoding/pynist/
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
		:commits-since: v0.6.2.post2
		:alt: GitHub commits since tagged version

	.. |commits-latest| github-shield::
		:last-commit:
		:alt: GitHub last commit

	.. |maintained| maintained-shield:: 2023
		:alt: Maintenance

	.. |pypi-downloads| pypi-shield::
		:project: pyms-nist-search
		:downloads: month
		:alt: PyPI - Downloads

.. end shields


PyMassSpec extension for searching mass spectra using NIST's Spectrum Search Engine

PyMassSpec NIST Search is Free Software licensed under the
`GNU Lesser General Public License Version 3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_.

A copy of the MassBank of North America database, in JSON, MSP and NIST Library formats,
is included for the purposes of these tests.
This library was created on 22 April 2020 using the "parse_mona_json.py" script and Lib2Nist.
Licensed under the CC BY 4.0 License. For a list of contributors, see the file ``MoNA_GCMS_Library/AUTHORS``.

.. TODO: add links.

Installation
--------------

.. start installation

.. installation:: pyms-nist-search
	:pypi:
	:github:

.. end installation

Contents
------------

.. html-section::

.. toctree::
	:hidden:

	Home<self>


.. toctree::
	:maxdepth: 3

	usage
	api
	contributing
	license
	Source

.. sidebar-links::
	:caption: Links
	:github:
	:pypi: pyms-nist-search


.. start links

.. only:: html

	View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

	:github:repo:`Browse the GitHub Repository <domdfcoding/pynist>`

.. end links
