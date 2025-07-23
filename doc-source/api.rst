==============
API Reference
==============

.. automodule:: pyms_nist_search
	:no-members:


:mod:`~pyms_nist_search`
----------------------------------

This module exposes many constants used by ``pyms-nist-search``.
The most notable are detailed below.

.. py:data:: NISTMS_MAIN_LIB

	Indicates the NIST/EPA/NIH main library.

.. py:data:: NISTMS_REP_LIB

	Indicates the NIST/EPA/NIH replicate spectra library.

.. py:data:: NISTMS_USER_LIB

	Indicates a user-created library or simular.

.. py:data:: NISTMS_MAX_LIBS

	The maximum number of libraries that may be searched.

.. latex:clearpage::

:mod:`~pyms_nist_search.base`
----------------------------------

.. automodule:: pyms_nist_search.base
	:no-members:

.. autoclass:: pyms_nist_search.base.NISTBase

.. latex:clearpage::

:mod:`~pyms_nist_search.docker_engine`
---------------------------------------

.. automodule:: pyms_nist_search.docker_engine


.. latex:clearpage::

:mod:`~pyms_nist_search.reference_data`
---------------------------------------

.. automodule:: pyms_nist_search.reference_data
	:no-members:

.. autoclass:: pyms_nist_search.reference_data.ReferenceData


:mod:`~pyms_nist_search.search_result`
---------------------------------------

.. automodule:: pyms_nist_search.search_result
	:no-members:

.. autoclass:: pyms_nist_search.search_result.SearchResult
	:exclude-members: __repr__


.. latex:vspace:: 40px

:mod:`~pyms_nist_search.utils`
-----------------------------------

.. automodule:: pyms_nist_search.utils


.. latex:clearpage::

:mod:`~pyms_nist_search.win_engine`
-----------------------------------

.. automodule:: pyms_nist_search.win_engine
	:no-members:

.. autoclass:: pyms_nist_search.win_engine.Engine
