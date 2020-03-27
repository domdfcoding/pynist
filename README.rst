************************
PyMassSpec NIST Search
************************

.. image:: https://travis-ci.com/domdfcoding/pynist.svg?branch=master
	:target: https://travis-ci.com/domdfcoding/pynist
	:alt: Linux Build Status
.. image:: https://ci.appveyor.com/api/projects/status/82cs9prucypd1igb?svg=true
	:target: https://ci.appveyor.com/project/domdfcoding/pyms-nist-search/branch/master
	:alt: Windows Build Status
.. image:: https://readthedocs.org/projects/pymassspec/badge/?version=latest
	:target: https://pymassspec.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/pyms_nist_search.svg
	:target: https://pypi.org/project/pyms_nist_search/
	:alt: PyPI
.. image:: https://img.shields.io/pypi/pyversions/pyms_nist_search.svg
	:target: https://pypi.org/project/pyms_nist_search/
	:alt: PyPI - Python Version
.. image:: https://img.shields.io/pypi/l/pyms-nist-search
	:alt: PyPI - License
	:target: https://www.gnu.org/licenses/lgpl-3.0.en.html



PyMassSpec extension for searching mass spectra using NIST's Spectrum Search Engine

PyMassSpec NIST Search is Free Software licensed under the `GNU Lesser General Public License Version 3 <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_

Usage
########

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
