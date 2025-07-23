=======
Usage
=======

You will need to supply your own copy of the NIST Mass Spectral library to use this software.

The main class in this library is the :class:`~pyms_nist_search.win_engine.Engine` class. This class performs the actual searching.
Start by initialising the search engine as follows:

.. code-block:: python

	search = pyms_nist_search.Engine(
			FULL_PATH_TO_MAIN_LIBRARY,
			pyms_nist_search.NISTMS_MAIN_LIB,
			FULL_PATH_TO_WORK_DIR,
			)

Where ``FULL_PATH_TO_MAIN_LIBRARY`` is the path to the location of your mass spectral library,
and ``FULL_PATH_TO_WORK_DIR`` is the path to the working directory to be used by the search engine.

A :class:`pyms.Spectrum.MassSpectrum` object can then be searched as follows:

.. code-block:: python

	search.full_search_with_ref_data(mass_spec)

This will return a list of tuples consisting of :class:`~.SearchResult` and :class:`~.ReferenceData`
objects for the possible identities of the mass spectrum.

A list of just the :class:`~.SearchResult` objects can be obtained with this method:

.. code-block:: python

	hit_list = search.full_search(mass_spec)

For each of these hits, the reference data can be obtained as follows:

.. code-block:: python

	for hit in hit_list:
		ref_data = search.get_reference_data(hit.spec_loc)

Using Multiple Libraries
===========================

``pyms-nist-search`` can also be configured to search multiple libraries simultaneously,
such as the NIST mainlib and some user libraries.
The libraries to search are specified in a list of ``(<lib_path>, <lib_type>)`` tuples,
where ``lib_path`` is the full path to the library on disk and ``lib_type``
is :data:`pyms_nist_search.NISTMS_MAIN_LIB`, :data:`pyms_nist_search.NISTMS_USER_LIB` or :data:`pyms_nist_search.NISTMS_REP_LIB`
as applicable.

.. code-block:: python

	search = pyms_nist_search.Engine(
			[
					(FULL_PATH_TO_MAIN_LIBRARY, pyms_nist_search.NISTMS_MAIN_LIB),
					(FULL_PATH_TO_REPLICATE_LIBRARY, pyms_nist_search.NISTMS_REP_LIB),
					(FULL_PATH_TO_USER_LIBRARY, pyms_nist_search.NISTMS_USER_LIB),
					],
			work_dir=FULL_PATH_TO_WORK_DIR,
			)
