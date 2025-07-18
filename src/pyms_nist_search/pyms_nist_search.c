/*
pyms-nist-search.c

This file is part of PyMassSpec NIST Search
Python interface to the NIST MS Search DLL

Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>

PyMassSpec NIST Search is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation; either version 3 of
the License, or (at your option) any later version.

PyMassSpec NIST Search is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.

PyMassSpec NIST Search includes the redistributable binaries for NIST MS Search in
the x86 and x64 directories. Available from
ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip .
ctnt66.dll and ctnt66_64.dll copyright 1984-1996 FairCom Corporation.
"FairCom" and "c-tree Plus" are trademarks of FairCom Corporation
and are registered in the United States and other countries.
All Rights Reserved.

This file is a modified version of the CALLDLL.C files from
  ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip and
  https://sourceforge.net/projects/mzapi-live/

*/

#define PY_SSIZE_T_CLEAN
#include <Python.h>

/*
  To recompile, the following constant should be externally defined:

  INTERNALBUILD

  or in the compiler command line:

  /D "INTERNALBUILD"
*/

/* Linking */

#ifdef NISTMS_6BYTE_RECLOC
/*  NISTMS_RECLOC is 6-byte-long */
/*  This version can handle ms libraries that have user.dbu not greater than 2,147,483,647 bytes */
/*  link to nistdl32_2gb.lib */
/*  (NIST.pyd was built with this option) */
#else
/*  NISTMS_RECLOC is 4-byte-long; in fact, it is a 32-bit long int */
/*  This version can handle ms libraries that have user.dbu not greater than 268,435,455 bytes */
/*  link to nistdl32.lib */
#endif

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <ctype.h>
#include <memory.h>
#include <io.h>

#include "NISTMS.H"
#include "NISTERR.H"

#define MAX_NAME_LEN 120 /*  longest string returned for a name in hit list */

#ifdef WIN32
	#define MAX_FINAL_HITS 6000 /*  largest number of spectra in final hit list */ /*  This value MUST be >= 120 */
#else
	#define MAX_FINAL_HITS 1000 /*  largest number of spectra in final hit list */
/*  This value MUST be >= 120 */
#endif

/* Take a slice from an array of chars (`str`) between `start` and `end` and put it in `buffer` */
void slice_str(const unsigned char *str, unsigned char *buffer, size_t start, size_t end) {
	size_t j = 0;
	for (size_t i = start; i <= end; ++i) {
		buffer[j++] = str[i];
	}
	buffer[j] = 0;
}

/************************************/
/*  Define signatures for functions */
/************************************/
void NISTMS_C_EXPORT nistms_search(NISTMS_SEARCH_TYPE srch_type, NISTMS_IO *io);

static PyObject *spec_search(PyObject *self, PyObject *args);
static PyObject *spectrum_search(NISTMS_IO *pio, int search_type, char *spectrum);

static PyObject *full_spec_search(PyObject *self, PyObject *args);
static PyObject *full_spectrum_search(NISTMS_IO *pio, char *spectrum);

static PyObject *get_reference_data(PyObject *self, PyObject *args);

// static PyObject *get_lib_paths(PyObject *self, PyObject *args);
static PyObject *get_active_libs(PyObject *self, PyObject *args);

/* loads a single spectrum from a string */
static int parse_spectrum(NISTMS_MASS_SPECTRUM *ms, NISTMS_AUX_DATA *aux_data, char *spectrum);

/* initialization */
// static int  initialize_libs(NISTMS_IO *io);

static void get_spectrum(NISTMS_IO *io, NISTMS_RECLOC *fpos);
static void get_spectrum_int_or_accurate_mz(NISTMS_IO *pio, NISTMS_RECLOC *fpos, int bAccurate_mz);

static int do_init_api(NISTMS_IO *pio, char *lib_paths, char *lib_types, unsigned int num_libs, char *work_dir);
static PyObject *init_api(PyObject *self, PyObject *args);

/******************************/
/* allocated for results      */
/******************************/

/* replace MAX_FINAL_HITS with MAX_NOPRESRCH_HITS or MAX_LIB_SRCH_HITS for spectrum search */
char LibNamesBuffer[(unsigned)MAX_FINAL_HITS * MAX_NAME_LEN];

NISTMS_CONSTRAINTS constraints;

int g_bDisplayMsgLine; /* flag for the callback function */

static unsigned char g_synonyms[NISTMS_MAXSYNONYMLEN]; /*  optional */

static char g_contributor[NISTMS_MAXCONTRIBLEN];

char StringIn[80]; /* for input string  */

char active_libs[NISTMS_MAX_LIBS + 1]; /*  length = maximum number of libraries + 1 */

/* for initiation */
char lib_paths[256];
char work_dir_path[256];
char lib_types[NISTMS_MAX_LIBS + 1];
int num_libs = 0;

NISTMS_IO io;

// #define FULL_PATH_TO_MAIN_LIBRARY 'Path Goes Here'	// main
// #define FULL_PATH_TO_WORK_DIR 'Path Goes Here'

/******************************************************************
This function is the shell of a callback routine that the DLL
periodically calls while performing a library search.  It receives
progress information or can tell the program to abort (if, for
instance, the user has pressed a CANCEL button.  If an appropriate
Windows call is introduced here, it will allow task switching.
******************************************************************/
void NISTMS_CALLBACK CallBack(IQ *p) {

	extern int g_bDisplayMsgLine;
	switch (p->WhatToDo) {
		case WRITE_MSGLINE_:
			/* show progess using string in p->String; */
			if (g_bDisplayMsgLine)
				printf("%s\r", p->String);
			break;
		case TEST_CANCEL_:
			/* set p->ReturnValue=1 to abort processing */
			break;
	}
	return;
}

/*
Takes Python objects as input and prepares them for passing to spectrum_search
*/
static PyObject *spec_search(PyObject *self, PyObject *args) {
	int counter;
	char *test;
	char *my_test;
	int test_len;
	PyObject *py_hit_list;

	int ok = PyArg_ParseTuple(args, "s", &test);
	my_test = (char *)malloc(strlen(test) * sizeof('a'));
	strcpy(my_test, test);
	test_len = strlen(my_test);

	for (counter = 0; counter < test_len; counter += 1) {
		if (my_test[counter] == '*') {
			my_test[counter] = '\000';
		}
	}

	py_hit_list = spectrum_search(&io, NISTMS_NO_PRE_SRCH, my_test);
	free(my_test);
	return py_hit_list;
}

static PyObject *spectrum_search(NISTMS_IO *pio, int search_type, char *spectrum) {

	static NISTMS_CONSTRAINTS constraints;
	static NISTMS_MASS_SPECTRUM userms; /*  contains unknown spectrum */
	static NISTMS_AUX_DATA aux;
	static NISTMS_HIT_LIST hit_list;   /*  returns hits */
	static NISTMS_SRCH_CONTROLS cntls; /*  specifies search type */

	//	int search_type = NISTMS_SCREEN_SRCH;
	//
	//	#define MAX_SCREEN_LOCS NISTMS_MAX_FPOS /* 6000 = largest number of tentative hits from the
	//											   screen search (pre-search) */
	//
	//	#define MAX_HITS_RETURNED MAX_LIB_SRCH_HITS

	/*
	The following seven buffers are attached to the NISTMS_HIT_LIST structure
	to hold retrieved hit locations, similarity values and optional hit
	descriptions

	fpos_array is the central buffer.  It is used as follows:
	1) to receive locations of spectra passing the screen (pre-search)
	2) to send possible hit locations for spectral comparison
	3) to receive an ordered hit list
	*/

	static NISTMS_RECLOC fpos_array[MAX_NOPRESRCH_HITS];

	/*     REQUIRED for library search */
	static int sim_num[MAX_NOPRESRCH_HITS];

	/*     REQUIRED for reverse (impure) search, OPTIONAL for forward search */
	static int rev_sim_num[MAX_NOPRESRCH_HITS];

	/*     OPTIONAL for forward (pure compound) 'Q', 'I', or 'P' search,  */
	/*     Not meaningful for reverse (impure), 'S', 'H' or 'L' searches  */
	static int hit_prob[MAX_NOPRESRCH_HITS];

	//	/*     Meaningful only for Peptide search */
	static float pep_scores[NUM_ADD_SPEC_MATCHFACT][MAX_NOPRESRCH_HITS];

	/*     OPTIONAL; for (possibly truncated) name retrieval for hit list presentation */
	static unsigned char *lib_names = LibNamesBuffer;
	//	static NISTMS_RECLOC *stru_pos[MAX_HITS_RETURNED];

	//	/*     OPTIONAL; for CAS reg. nos. retrieval for hit list presentation */
	//	static long *casnos[MAX_HITS_RETURNED];

	int i;
	//	int best_score = 0 ;

	/* OPTIONAL; for finding hits satisfying constraints */
	memset((void *)&cntls, '\0', sizeof(cntls));

	memset((void *)&hit_list, '\0', sizeof(hit_list));
	memset(pep_scores, 0, sizeof(pep_scores));

	if (0 >= parse_spectrum(&userms, &aux, spectrum)) {
		if (userms.num_exact_mz < -1) {
			PyErr_Format(PyExc_RuntimeError,
						 "Only %d peaks were read: not enough room to read all peaks. Terminating.\n",
						 -(1 + userms.num_exact_mz));
			return NULL;
		} else {
			PyErr_Format(PyExc_RuntimeError, "Could not read the spectrum. Terminating.\n");
			return NULL;
		}
		Py_RETURN_NONE; // cannot read the spectrum
	}

	/* new feature: ignore precursor ion(s)
	   within +/- cntls.precursor_ion_tolerance interval around precursor m/z from:

	  for the searched spectrum:
	  ----------------------------
	  1. ms/ms search && cntls.user_mw                    => cntls.user_mw*100
	  2. peptide search && cntls.precursor_ion_100mz      => cntls.precursor_ion_100mz
	  3. peptide format search spectrum has precursor m/z => pio->userms->precursor_ion_100mz
	  4. NOT peptide search && user spec. mw > 0          => pio->aux_data->mw*100
	  5. zero if none of the above
	  Note: precursor m/z is extracted from the NIST_MSMS
			library spectrum synonyms since 2007-04-04

	  for the library spectrum:
	  ----------------------------
	  1. spectrum has precursor m/z                       => precursor m/z
		 (including nist_msms library)
	  2. not peptide search and spectrum has mw           => mw*100

	  Also are ignored peaks in each library spectrum coinsiding with the search spectrum precursor
	  and peaks in the search spectrum counsiding with the library spectrum precursor.

	 */

	cntls.search_mode = 'Q'; // Quick Search
	cntls.user_mw = 0;		 // Used by 'L', 'H', 'M' only
	cntls.impure = 0;

	cntls.min_mass = 1;
	cntls.max_mass = 2000;

	cntls.min_abund = 1; // ignored by ms/ms search

	cntls.search_mode |= SEARCH_MODE_FLAG_IGNORE_PRECURSOR; // comment out to de-activate

	// for selecting spectra to be compared according to their Precursor m/z
	// and half-width of the ignoring precursor m/z interval (SEARCH_MODE_FLAG_IGNORE_PRECURSOR)
	// (for integer m/z the rounding of the half-width is to the nearest 100)
	cntls.precursor_ion_tolerance = 160; // 1.6 m/z units
	// cntls.precursor_ion_tolerance = 10;  // 1.6 m/z units
	// for spectra comparison
	cntls.product_ions_tolerance = 80; // 0.8 m/z units

	// Peptide Presearch Option
	// The value assigned in the next statement has the followin meaning:
	// zero => search in the active libs all spectra that have Precursor m/z
	//   (corresponds to Presearch=Off in the NIST MS Search Prorgam)
	// 100*(Precursor m/z) => compare only spectra
	//   within +/- cntls.nPrecursorTolerance interval
	//   (corresponds to Presearch=Default in the NIST MS Search Prorgam)
	cntls.precursor_ion_100mz = userms.precursor_ion_100mz; /* Presearch=Default */
															/* 0 => Presearch = OFF */

	//--- Display indicators ----
	cntls.pep_bTF_qry = 0;
	cntls.pep_bE_Omssa = 1;
	cntls.pep_bTF_lib = 0;
	cntls.pep_nCysteineModification = 0; /* unused */
	cntls.pep_cThreshold = 0;			 /* 0=>the highest threshold, 1=>Mediium, 2=>the lowest */
	//--- Weight indicators ----
	cntls.pep_bOmssa = 1;		  /* Use OMSSA score for weighting = No */
	cntls.pep_bNumReplicates = 0; /* Use number of Replicates = No */
	cntls.pep_bQ_TOF = 0;

	/*  attach allocated buffers to input/output structure */
	pio->userms = &userms; /*  input mass spectrum */
	pio->cntls = &cntls;   /*  type of search */

	/* prepare hit list to receive spectrum pointers */
	pio->hit_list = &hit_list;			   /* hit list */
	pio->hit_list->spec_locs = fpos_array; /* spectrum pointers */
	pio->hit_list->max_spec_locs = MAX_NOPRESRCH_HITS;
	pio->hit_list->max_hits_desired = MAX_NOPRESRCH_HITS;

	/* prepare hit list to receive spectrum compare results */
	pio->hit_list->sim_num = sim_num;
	pio->hit_list->rev_sim_num = rev_sim_num;
	pio->hit_list->hit_prob = hit_prob;
	for (i = 0; i < NUM_ADD_SPEC_MATCHFACT; i++) {
		hit_list.pep_Mf[i] = pep_scores[i];
		// actually, only
		// !!cntls.pep_bTF_qry+!!cntls.pep_bE_Omssa+!!cntls.pep_bTF_lib+!!cntls.bRevImpure
		// elements are needed (number of non-zeroes)
	}

	hit_list.lib_names = lib_names;
	hit_list.lib_names_len = sizeof(LibNamesBuffer);
	hit_list.max_one_lib_name_len = MAX_NAME_LEN;
	hit_list.stru_pos = NULL; /* no structures available in Peptide libraries */
	hit_list.casnos = NULL;	  /* no CAS r.n. available in Peptide libraries */

	pio->constraints = NULL; /*  no constraints */

	/* if these were uncommented, hits would be subject to various peptide-specific constraints*/
	// io.constraints = &constraints;
	// clear_constraints(io.constraints);              // disable all constraints
	// set_pep_constraints(io.constraints); // add peptide-specific constraints
	// printf("%d is the search_type\n",search_type) ;

	nistms_search(search_type, pio);

	switch (pio->error_code) {
		case 0:
			break;
		default:
			PyErr_Format(PyExc_RuntimeError, "Spectrum search returned error code %d\n", pio->error_code);
			return NULL;
	};

	PyObject *py_hit_list = PyList_New(0);

	if (pio->hit_list->num_hits_found) {
		int best_score = pio->hit_list->sim_num[0];

		// printf("%d\n", best_score);
		// printf("%d\n", pio->hit_list->num_hits_found);

		int name_len = pio->hit_list->max_one_lib_name_len;
		unsigned char *raw_hit_names = pio->hit_list->lib_names;

		for (int i = 0; i < pio->hit_list->num_hits_found; i++) {
			PyObject *d = PyDict_New();

			// printf("%d, ", i);

			PyObject *py_sim_num = PyLong_FromLong(pio->hit_list->sim_num[i]);
			PyDict_SetItemString(d, "sim_num", py_sim_num);
			// printf("%d, ", pio->hit_list->sim_num[i]);

			PyObject *py_rev_sim_num = PyLong_FromLong(pio->hit_list->rev_sim_num[i]);
			PyDict_SetItemString(d, "rev_sim_num", py_rev_sim_num);
			// printf("%d, ", pio->hit_list->rev_sim_num[i]);

			PyObject *py_hit_prob = PyLong_FromLong(pio->hit_list->hit_prob[i]);
			PyDict_SetItemString(d, "hit_prob", py_hit_prob);
			// printf("%d, ", pio->hit_list->hit_prob[i]);

			// PyObject *py_in_library_prob = PyLong_FromLong(pio->hit_list->in_library_prob[i]);
			// PyDict_SetItemString(d, "in_library_prob", py_in_library_prob);
			// printf("%d, ", pio->hit_list->in_library_prob[i]);

			int start_byte = i * name_len;
			int end_byte = start_byte + name_len;
			unsigned char buffer[MAX_NAME_LEN]; // Should be much larger than needed
												//			slice_str(raw_hit_names, buffer, start_byte, end_byte);

			PyObject *py_hit_name_char_list = PyList_New(0);

			// Fix for Wine crash
			for (size_t i = start_byte; i <= end_byte; ++i) {
				PyList_Append(py_hit_name_char_list, PyLong_FromLong(raw_hit_names[i]));
			}

			// for (int i = 0; i <= MAX_NAME_LEN; i++) {
			// 	PyList_Append(py_hit_name_char_list, PyLong_FromLong(buffer[i]));
			// }

			PyDict_SetItemString(d, "hit_name_chars", py_hit_name_char_list);

			// PyObject *py_hit_name = PyUnicode_FromFormat("%s", buffer);
			// PyDict_SetItemString(d, "hit_name", py_hit_name);

			// printf("%ld, ", pio->hit_list->stru_pos[i]);

			// printf("%ld, ", pio->hit_list->spec_locs[i]);

			PyObject *py_spec_loc = PyLong_FromLong(pio->hit_list->spec_locs[i]);
			PyDict_SetItemString(d, "spec_loc", py_spec_loc);

			PyObject *py_lib_idx = PyLong_FromLong(NISTMS_LIB_NUM(hit_list.spec_locs[i]));
			PyDict_SetItemString(d, "lib_idx", py_lib_idx);

			if (pio->hit_list->casnos) {
				PyDict_SetItemString(d, "cas_no", PyLong_FromLong(pio->hit_list->casnos[i]));
			} else {
				PyDict_SetItemString(d, "cas_no", PyLong_FromLong(0));
			}

			// printf("\n");

			PyList_Append(py_hit_list, d);
		}
	}

	return (py_hit_list);
}

/****************************************************************************
Retieve identification information for spectra whose
spectra locations were previously retrieved in a NISTMS_HIT_LIST structure.
*****************************************************************************/
static void build_hitlist(NISTMS_IO *pio) {
	/*  Buffers for rapidly showing names and structures a hit list */
	char *lib_names = LibNamesBuffer; /*  static Global buffer for compilation convenience */
	static NISTMS_RECLOC stru_pos[MAX_FINAL_HITS];
	static long int casnos[MAX_FINAL_HITS];

	pio->constraints = NULL;
	pio->hit_list->lib_names = lib_names;
	pio->hit_list->lib_names_len = sizeof(LibNamesBuffer);
	pio->hit_list->max_one_lib_name_len = MAX_NAME_LEN;

	/* ensure returned data can fit in allocated space*/
	pio->hit_list->max_hits_desired = min(pio->hit_list->max_hits_desired, MAX_FINAL_HITS);
	if (pio->hit_list->max_hits_desired > 0) {
		/* set buffers for rapidly showing structures and CAS reg. nos. in a hit list */
		pio->hit_list->stru_pos = stru_pos;
		pio->hit_list->casnos = casnos;
	} else {
		/* no buffers for struct. pos.: save time */
		pio->hit_list->stru_pos = NULL;
		pio->hit_list->casnos = NULL;
	}

	/* this returns identification information for spectra in the hit list field */
	/* spec_locs[] that satisfy any specified constraints */
	nistms_search(NISTMS_BUILD_HITLIST_SRCH, pio);
}

static PyObject *nist_cas_search(NISTMS_IO *pio, char query[]) {

	static NISTMS_HIT_LIST hit_list;
	#define MAX_NUM_OF_OFFSETS MAX_FINAL_HITS /*  must be no more than current system limit of NISTMS_MAX_FPOS=6000 */

	static NISTMS_RECLOC fpos_array[MAX_NUM_OF_OFFSETS];
	int num_hits_found = 0;

	pio->string_in = query;

	memset((void *)&hit_list, '\0', sizeof(hit_list));
	hit_list.spec_locs = fpos_array;
	hit_list.max_spec_locs = MAX_NUM_OF_OFFSETS;
	pio->hit_list = &hit_list;

	nistms_search(NISTMS_CASNO_SRCH, pio);

	if (pio->error_code) {
		PyErr_Format(PyExc_RuntimeError, "Spectrum search returned error code %d\n", pio->error_code);
		return NULL;
	}

	if (pio->hit_list->num_hits_found) {
		/*  get compound identification information for compounds retrieved above */
		pio->hit_list->max_hits_desired = pio->hit_list->num_hits_found;
		build_hitlist(pio);

		num_hits_found = pio->hit_list->num_hits_found;
	} else {
		num_hits_found = -1; // no more spectra in sequential search
	}

	PyObject *py_hit_list = PyList_New(0);

	if (pio->hit_list->num_hits_found) {

		int name_len = pio->hit_list->max_one_lib_name_len;
		unsigned char *raw_hit_names = pio->hit_list->lib_names;

		for (int i = 0; i < pio->hit_list->num_hits_found; i++) {
			PyObject *d = PyDict_New();

			PyDict_SetItemString(d, "sim_num", PyLong_FromLong(0));
			PyDict_SetItemString(d, "rev_sim_num", PyLong_FromLong(0));
			PyDict_SetItemString(d, "hit_prob", PyLong_FromLong(0));

			int start_byte = i * name_len;
			int end_byte = start_byte + name_len;
			unsigned char buffer[MAX_NAME_LEN]; // Should be much larger than needed

			PyObject *py_hit_name_char_list = PyList_New(0);

			// Fix for Wine crash
			for (size_t i = start_byte; i <= end_byte; ++i) {
				PyList_Append(py_hit_name_char_list, PyLong_FromLong(raw_hit_names[i]));
			}

			PyDict_SetItemString(d, "hit_name_chars", py_hit_name_char_list);

			PyObject *py_spec_loc = PyLong_FromLong(pio->hit_list->spec_locs[i]);
			PyDict_SetItemString(d, "spec_loc", py_spec_loc);

			if (pio->hit_list->casnos) {
				PyDict_SetItemString(d, "cas_no", PyLong_FromLong(pio->hit_list->casnos[i]));
			} else {
				PyDict_SetItemString(d, "cas_no", PyLong_FromLong(0));
			}

			PyList_Append(py_hit_list, d);
		}
	}

	return (py_hit_list);
}

/*
Takes Python objects as input and prepares them for passing to nist_cas_search
*/
static PyObject *cas_search(PyObject *self, PyObject *args) {
	char *query;

	if (!PyArg_ParseTuple(args, "s", &query))
		return NULL;

	return nist_cas_search(&io, query);
}

/*
Takes Python objects as input and prepares them for passing to full_spectrum_search
*/
static PyObject *full_spec_search(PyObject *self, PyObject *args) {
	int counter;
	char *test;
	char *my_test;
	int test_len;
	PyObject *py_hit_list;

	int ok = PyArg_ParseTuple(args, "s", &test);
	my_test = (char *)malloc(strlen(test) * sizeof('a'));
	strcpy(my_test, test);
	test_len = strlen(my_test);

	for (counter = 0; counter < test_len; counter += 1) {
		if (my_test[counter] == '*') {
			my_test[counter] = '\000';
		}
	}

	py_hit_list = full_spectrum_search(&io, my_test);
	free(my_test);
	return py_hit_list;
}

// /*
// Returns the current list of libraries (delimited by NISTMS_PATH_SEPARATOR)
// */
// static PyObject *get_lib_paths(PyObject *self, PyObject *Py_UNUSED(args)) {
// 	PyObject *py_lib_names = PyUnicode_FromString(lib_paths);
// 	return py_lib_names;
// }

/*
Returns the currently active libraries (in search order)
*/
static PyObject *get_active_libs(PyObject *self, PyObject *Py_UNUSED(args)) {
	PyObject *py_active_libs = PyList_New(0);

	for (int pos = 0; pos < NISTMS_MAX_LIBS; pos++) {
		PyList_Append(py_active_libs, PyLong_FromLong(active_libs[pos]));
	}

	return py_active_libs;
}

// TODO: allow active libs to be changed without reinit

/****************************************************************************

   This function illustrates a full-featured library search.

* New (since July 2008): "fast presearch" is initiated if cntls.search_mode |=
SRCH_CONTROLS.SEARCH_MODE_FLAG_FAST_PRESEARCH
* New (since July 2008): MS/MS search (type='E') with presearch may be executed the same way as the Identity (type='I')
search

   These searches are always conducted in two stages:
	 1) screen search (pre-search) to find a set of possible hits
	 2) comparison of user spectrum to each library spectrum identified in the
		screen search.  The screen search stores locations of possible
		hits in buffer fpos_array.  These are transmitted to the comparison
		search ranked hits (the hit list) and returned in the same array
		with similarity values in sim_num[], rev_sim_num[] and hit_prob[].

	Search mode
	Four types of library searches are available (see Documentation for details)
   For compound IDENTIFICATION
	 1) 'Q'uick: 98% retrieval efficiency
	 2) 'I'dentity: 99+% retrieval effieiency, about 3x slower than 'Q'uick
   For finding SIMILAR compounds
	 3) 'S'imilarity: uses only conventional peaks, input MW not needed
	 4) 'L'oss: uses only "neutral loss" peaks, REQUIRES input MW
	 5) 'H'ybrid: wses both normal and neutral loss peaks, REQUIRES input MW


   INPUT:
	 1) Libraries to be searched (io->active_libs)
	 2) "Unknown" mass spectrum (in NISTMS_USER_SPECTRUM structure)
	 3) Type of search to be done (in NISTMS_SRCH_CONTROLS structure)
	 4) Allocated space for retrieved spectra locations
	 5) Allocated space for spectral similarity values
	 6) Optional: Allocated space for chemical names of hits
		(in NIST_HIT_LIST structure)
	 7) Optional: Allocated space for locations of chemical structures
		(in NIST_HIT_LIST structure)

   OUTPUT: 1-4 in NISTMS_HIT_LIST buffers allocated by calling program
	 1) Spectrum locations,
	 2) Similarity values,
		 a) sim_val - forward comparison match factors
		 b) rev_sim_val - reverse comparison match factors (assumes
			 unmatched unknown peaks are from impurities)
		 c) hit_prob - probability (x 100) that a hit is correct presuming
			 that the matching compound is in the library
	 3) Chemical names (optional),
	 4) Chemical structure locations (optional):
	 5) Relative probability (x 100) that a correct compound was found
		 A positive value signifies that the correct hit has been
		 found, negative values suggest that it has not.
		 Value/100 represents an increase in confidence that a correct
		 hit has been found (or not found).  See paper in JASMS, 1994.

*****************************************************************************/

static PyObject *full_spectrum_search(NISTMS_IO *pio, char *spectrum) {

	static NISTMS_CONSTRAINTS constraints;
	static NISTMS_MASS_SPECTRUM userms; /*  contains unknown spectrum */
	static NISTMS_AUX_DATA aux;
	static NISTMS_HIT_LIST hit_list;   /*  returns hits */
	static NISTMS_SRCH_CONTROLS cntls; /*  specifies search type */

	int search_type = NISTMS_SCREEN_SRCH;

	#define MAX_SCREEN_LOCS                                                                                                \
	NISTMS_MAX_FPOS /* 6000 = largest number of tentative hits from the                                                \
					   screen search (pre-search) */

	#define MAX_HITS_RETURNED MAX_LIB_SRCH_HITS

	/*
		The following seven buffers are attached to the NISTMS_HIT_LIST structure
		to hold retrieved hit locations, similarity values and optional hit
		descriptions

		fpos_array is the central buffer.  It is used as follows:
		1) to receive locations of spectra passing the screen (pre-search)
		2) to send possible hit locations for spectral comparison
		3) to receive an ordered hit list

		Note: in case search_type=NISTMS_NO_PRE_SRCH,
			  MAX_HITS_RETURNED may be increased to MAX_NOPRESRCH_HITS
	*/

	static NISTMS_RECLOC fpos_array[MAX_SCREEN_LOCS];

	/*     REQUIRED for library search */
	/*     In case of ms/ms search, this contains Score */
	static int sim_num[MAX_HITS_RETURNED];

	/*     REQUIRED for reverse (impure) search, OPTIONAL for forward search */
	/*     In case of any ms/ms search, this contains dot-product */
	static int rev_sim_num[MAX_HITS_RETURNED];

	/*     OPTIONAL for forward (pure compound) 'Q', 'I', 'P', or 'E' search mode,  */
	/*     Not meaningful for reverse (impure), 'S', 'H' or 'L' search modes  */
	static int hit_prob[MAX_HITS_RETURNED];

	//	/*     Meaningful only for Peptide search */
	//	static float pep_scores[NUM_ADD_SPEC_MATCHFACT][MAX_NOPRESRCH_HITS];

	/*     OPTIONAL; for (possibly truncated) name retrieval for hit list presentation */
	static unsigned char *lib_names = LibNamesBuffer;
	static NISTMS_RECLOC *stru_pos[MAX_HITS_RETURNED];

	/*     OPTIONAL; for CAS reg. nos. retrieval for hit list presentation */
	long *casnos[MAX_HITS_RETURNED];

	int i;
	int best_score = 0;

	/*     OPTIONAL; for finding hits satisfying constraints  */
	memset((void *)&cntls, '\0', sizeof(cntls));

	memset((void *)&hit_list, '\0', sizeof(hit_list));
	// memset(pep_scores, 0, sizeof(pep_scores));

	if (0 >= parse_spectrum(&userms, &aux, spectrum)) {
		if (userms.num_exact_mz < -1) {
			PyErr_Format(PyExc_RuntimeError,
						 "Only %d peaks were read: not enough room to read all peaks. Terminating.\n",
						 -(1 + userms.num_exact_mz));
			return NULL;
		} else {
			PyErr_Format(PyExc_RuntimeError, "Could not read the spectrum. Terminating.\n");
			return NULL;
		}
		Py_RETURN_NONE; // cannot read the spectrum
	}

	/*****************************************************************************
	 *  search_mode = (ASCII code of a letter) | (search mode flags)
	 *  letters:
	 *    Q  Quick Identity Search
	 *    I  Normal Identity Search
	 *    P  I+penalize rare compounrs
	 *    S  Similarity Search
	 *    L  Loss Similarity Search      (requires user_mw)
	 *    H  Hybrid Similarity Search    (requires user_mw)
	 *    M  search for MS/MS spectrum in EI libraries  (requires user_mw)
	 *    E  MS/MS Identity Search
	 *
	 *  search mode flags
	 *   SEARCH_MODE_FLAG_IGNORE_PRECURSOR      // ms/ms
	 *   SEARCH_MODE_FLAG_FAST_PRESEARCH        // any presearch in two-stage search
	 *   -- v.2.1.5.1 -- NIST 11 --
	 *   SEARCH_MODE_FLAG_ALT_PEAK_MATCHING     // ms/ms
	 *   SEARCH_MODE_FLAG_GENERIC_MSMS          // ms/ms: Peptide search=OFF
	 *   SEARCH_MODE_FLAG_REJECT_OTHER          // ms/ms
	 *   SEARCH_MODE_FLAG_PRECUR_MZ_TOL_PPM     // ms/ms
	 *   SEARCH_MODE_FLAG_PROD_PEAK_TOL_PPM     // ms/ms
	 *   -- masks --
	 *   SEARCH_MODE_FLAG_MASK
	 *   SEARCH_MODE_CHAR_MASK
	 ******************************************************************************/

	cntls.search_mode = 'I';
	cntls.user_mw = 1; // Used by 'L', 'H' or 'M' only  // This got replaced by 0 later on
	cntls.impure = 0;

	// cntls.min_mass =-1 =>lower mass limit=max(min_mass(libms),min_mass(userms)), default in MS Search
	// in MS Search built before 03/04/2013, in 'E' mode, cntls.min_mass is treated as
	// cntls.min_mass = fabs(cntls.min_mass) >= 0
	// cntls.max_mass  = -1 is treated as 1; 0 is treated as max. allowed m/z~4000

	// Min Mass:  -1 => auto: max out of min m/z in library and search spectrum, implemented in MS Search build Mar 04,
	// 2013 or later Max Mass:  -1=> auto: max out of max m/z in library and search spectrum; up to 4000, implemented in
	// MS Search build Mar 04, 2013 or later

	if ((cntls.search_mode & SEARCH_MODE_CHAR_MASK) == 'E') {
		cntls.min_mass = 0; // same as 1;
		cntls.max_mass = 0; // max. mass; same as -1=>no upper mass limit
	} else {
		cntls.min_mass = -1; // 0 is the same as 1;
		cntls.max_mass = -1; //-1=>no upper mass limit
	}

	//	cntls.min_mass  =  1;
	//	cntls.max_mass  =  -1;

	cntls.min_abund = 1; // ignored by ms/ms search  // This got replaced by 0 (auto: min possible) later on

	/*  attach allocated buffers to input/output structure */
	pio->userms = &userms; /*  input mass spectrum */
	pio->cntls = &cntls;   /*  type of search */

	/* prepare hit list to receive spectrum pointers */
	pio->hit_list = &hit_list;			   /* hit list */
	pio->hit_list->spec_locs = fpos_array; /* spectrum pointers */
	pio->hit_list->max_spec_locs = search_type == NISTMS_SCREEN_SRCH ? MAX_SCREEN_LOCS : MAX_NOPRESRCH_HITS;

	/*  Screen ("pre-search") retrieves set of tentative hits */
	nistms_search(search_type, pio);
	switch (pio->error_code) {
		case 0:
			break;

		case WRN_TOO_MANY_HITS:
			/* pre-search cannot return more than 6000 hits */
			/* This warning may occur if the spectrum has only few peaks. */
		case ERR_MAX_SPEC_LOCS_TOO_SMALL:
			/* To lose less hits increase pio->hit_list->spec_locs length*/
			printf(
				"Warning: Too many hits after pre-search. Only %d will be compared.\n",
				pio->hit_list->num_hits_found
				);
			break;
		default:
			printf("Screen search returned error code %d\n", pio->error_code);
	};

	if (search_type == NISTMS_SCREEN_SRCH) {
		/*
		Now prepare for comparing spectra referred to in
		io->hit_list->spec_locs with your spectrum
		Each array must be able to contain io->hit_list->max_hits_desired hits >= 100
		*/

		pio->hit_list->max_hits_desired = MAX_HITS_RETURNED;
		pio->hit_list->sim_num = sim_num;
		pio->hit_list->rev_sim_num = rev_sim_num;
		pio->hit_list->hit_prob = hit_prob;

		/*
		Returning of names and structure pointers is optional:
		hit_list.lib_names == NULL or hit_list.stru_loc == NULL
		associated data will simply not be returned.  This information
		may be obtained later in individual retrievals of spectra
		*/

		hit_list.lib_names = lib_names;
		hit_list.lib_names_len = sizeof(LibNamesBuffer);
		hit_list.max_one_lib_name_len = MAX_NAME_LEN;
		hit_list.stru_pos = stru_pos;
		hit_list.casnos = casnos;

		pio->constraints = NULL; /*  no constraints */

		/* if these were uncommented, hits would be subjected to various constraints*/

		// pio.constraints = &constraints;
		// clear_constraints(pio.constraints);
		// #ifdef PEPTIDE_VERSION
		// 	set_pep_constraints( pio.constraints );
		// #endif
		// 	set_constraints( pio.constraints );
		//    pio.constraints.other_dbs=65;

		/*  compare complete user and library spectra found by pre-search */
		nistms_search(NISTMS_COMPARE_SPECTRA_SRCH, pio);
	}

	PyObject *py_hit_list = PyList_New(0);

	if (pio->hit_list->num_hits_found) {
		int best_score = pio->hit_list->sim_num[0];

		// printf("%d\n", best_score);
		// printf("%d\n", pio->hit_list->num_hits_found);

		int name_len = pio->hit_list->max_one_lib_name_len;
		unsigned char *raw_hit_names = pio->hit_list->lib_names;

		for (int i = 0; i < pio->hit_list->num_hits_found; i++) {
			PyObject *d = PyDict_New();

			printf("%d, ", i);

			PyObject *py_sim_num = PyLong_FromLong(hit_list.sim_num[i]);
			PyDict_SetItemString(d, "sim_num", py_sim_num);
			printf("%d, ", pio->hit_list->sim_num[i]);

			PyObject *py_rev_sim_num = PyLong_FromLong(hit_list.rev_sim_num[i]);
			PyDict_SetItemString(d, "rev_sim_num", py_rev_sim_num);
			printf("%d, ", pio->hit_list->rev_sim_num[i]);

			PyObject *py_hit_prob = PyLong_FromLong(hit_list.hit_prob[i]);
			PyDict_SetItemString(d, "hit_prob", py_hit_prob);
			printf("%d, ", pio->hit_list->hit_prob[i]);

			// PyObject *py_in_library_prob = PyLong_FromLong(hit_list.in_library_prob[i]);
			// PyDict_SetItemString(d, "in_library_prob", py_in_library_prob);
			// printf("%d, ", pio->hit_list->in_library_prob[i]);

			int start_byte = i * name_len;
			int end_byte = start_byte + name_len;
			unsigned char buffer[MAX_NAME_LEN]; // Should be much larger than needed
			// slice_str(raw_hit_names, buffer, start_byte, end_byte);

			PyObject *py_hit_name_char_list = PyList_New(0);

			// Fix for Wine crash
			for (size_t i = start_byte; i <= end_byte; ++i) {
				PyList_Append(py_hit_name_char_list, PyLong_FromLong(raw_hit_names[i]));
			}

			// for (int i = 0; i <= MAX_NAME_LEN; i++) {
			// 	PyList_Append(py_hit_name_char_list, PyLong_FromLong(buffer[i]));
			// }

			PyDict_SetItemString(d, "hit_name_chars", py_hit_name_char_list);

			// PyObject *py_hit_name = PyUnicode_FromFormat("%s", buffer);
			// PyDict_SetItemString(d, "hit_name", py_hit_name);

			// printf("%ld, ", pio->hit_list->stru_pos[i]);

			PyObject *py_spec_loc = PyLong_FromLong(hit_list.spec_locs[i]);
			PyDict_SetItemString(d, "spec_loc", py_spec_loc);
			// printf("%ld, ", pio->hit_list->spec_locs[i]);

			PyObject *py_lib_idx = PyLong_FromLong(NISTMS_LIB_NUM(hit_list.spec_locs[i]));
			PyDict_SetItemString(d, "lib_idx", py_lib_idx);

			PyObject *py_cas_no = PyLong_FromLong(hit_list.casnos[i]);
			PyDict_SetItemString(d, "cas_no", py_cas_no);
			// printf("%ld, ", pio->hit_list->casnos[i]);

			// printf("\n");

			PyList_Append(py_hit_list, d);
		}
	}

	return (py_hit_list);
}

/*
Finds and returns the information about the spectrum at the given location in the library
*/
static PyObject *get_reference_data(PyObject *self, PyObject *args) {
	NISTMS_RECLOC input_spec_loc;
	PyObject *record = PyDict_New();
	PyObject *py_mass_list = PyList_New(0);
	PyObject *py_intensity_list = PyList_New(0);
	// PyObject *py_synonym_list = PyList_New(0);
	PyObject *py_synonyms_char_list = PyList_New(0);

	int ok = PyArg_ParseTuple(args, "l", &input_spec_loc);
	// printf("Parsed Args\n");
	// printf("input_spec_locs = %ld", input_spec_loc);

	get_spectrum(&io, input_spec_loc);

	// printf("Search Complete\n");

	PyObject *py_lib_idx = PyLong_FromLong(NISTMS_LIB_NUM(input_spec_loc));
	PyDict_SetItemString(record, "lib_idx", py_lib_idx);

	// printf("Name: %s\n", io.aux_data->name);
	PyObject *py_name = PyUnicode_FromFormat("%s", io.aux_data->name);
	PyDict_SetItemString(record, "name", py_name);

	PyObject *py_name_char_list = PyList_New(0);

	for (int i = 0; i <= MAX_NAME_LEN; i++) {
		// printf("%d ", io.aux_data->name[i]);
		PyList_Append(py_name_char_list, PyLong_FromLong(io.aux_data->name[i]));
	}

	PyDict_SetItemString(record, "name_chars", py_name_char_list);

	// printf("CAS: %ld\n", io.aux_data->casno);
	PyObject *py_cas = PyLong_FromLong(io.aux_data->casno);
	PyDict_SetItemString(record, "cas", py_cas);

	// printf("NIST Num: %ld\n", io.aux_data->specno);
	PyObject *py_nist_no = PyLong_FromLong(io.aux_data->specno);
	PyDict_SetItemString(record, "nist_no", py_nist_no);

	// printf("ID: %ld\n", io.aux_data->ident);
	PyObject *py_id = PyLong_FromLong(io.aux_data->ident);
	PyDict_SetItemString(record, "id", py_id);

	// printf("MW: %d\n", io.aux_data->mw);
	PyObject *py_mw = PyLong_FromLong(io.aux_data->mw);
	PyDict_SetItemString(record, "mw", py_mw);

	// printf("Exact Mass: %f##\n", io.aux_data->exact_mw);

	// printf("Formula: %s\n", io.aux_data->formula);
	PyObject *py_formula = PyUnicode_FromString(io.aux_data->formula);
	PyDict_SetItemString(record, "formula", py_formula);

	// printf("Contributor: %s\n", io.aux_data->contributor);
	PyObject *py_contributor = PyUnicode_FromString(io.aux_data->contributor);
	PyDict_SetItemString(record, "contributor", py_contributor);

	// printf("MS Num Peaks: %d\n", io.libms->num_peaks);
	for (int i = 0; i < io.libms->num_peaks; i++) {
		// printf("\tmz, Intensity: %d %d\n", io.libms->mass[i], io.libms->abund[i]);
		// printf("%d\n", PyLong_FromLong(io.libms->mass[i]));
		PyList_Append(py_mass_list, PyLong_FromLong(io.libms->mass[i]));
		PyList_Append(py_intensity_list, PyLong_FromLong(io.libms->abund[i]));
		// printf("%d, %d\n", i, io.libms->num_peaks);
	}

	PyDict_SetItemString(record, "mass_list", py_mass_list);
	PyDict_SetItemString(record, "intensity_list", py_intensity_list);

	// Get synonyms in a list
	int start_byte = 0;
	unsigned char buffer[MAX_NAME_LEN]; // Should be much larger than needed

	for (int i = 0; i <= io.aux_data->synonyms_len; i++) {
		if (io.aux_data->synonyms[i] == 0) {
			if (i - start_byte > 0) {
				// slice_str(io.aux_data->synonyms, buffer, start_byte, i);
				// printf("%s#\n", buffer);
				// printf("%s\n", PyUnicode_FromString(buffer));
				// PyList_Append(py_synonym_list, PyUnicode_FromFormat("%s", buffer));

				PyObject *py_synonym_char_list = PyList_New(0);

				// for (int i = 0; i <= MAX_NAME_LEN; i++) {
				// 	PyList_Append(py_synonym_char_list, PyLong_FromLong(buffer[i]));
				// }

				// Fix for Wine crash
				for (size_t j = start_byte; j <= i; ++j) {
					PyList_Append(py_synonym_char_list, PyLong_FromLong(io.aux_data->synonyms[j]));
				}

				PyList_Append(py_synonyms_char_list, py_synonym_char_list);
			}

			start_byte = i + 1;
			char buffer[MAX_NAME_LEN];
		}
	}

	// PyDict_SetItemString(record, "synonyms", py_synonym_list);
	PyDict_SetItemString(record, "synonyms_chars", py_synonyms_char_list);

	return record;
}

/* loads a single spectrum from a string */
static int parse_spectrum(NISTMS_MASS_SPECTRUM *ms, NISTMS_AUX_DATA *aux_data, char *szPeaks) {

	unsigned char szName[] = "unknown";
	int bIncludeExactMZ = 0;

	/* tab-separated pairs (m/z, abundance) separated by NULL bytes; m/z in ASCENDING order */
	/***************************************************/
	/* Important: Abundances MUST be normalized to 999 */
	/**************************************************/

	int i;
	char *p, *q, *pPeakBuf;
	double dMz, dAbund, dMaxAbund = 0.0;
	unsigned int rounded_mz, rounded_ab;

	/* Name */
	memcpy(aux_data->name, szName, sizeof(szName));

	/* Mass Spectrum */

	/* Copy the mz-Abund exact data */
	if (ms->buf_exact_mz && ms->exact_mz && ms->exact_mz_len > 0 && sizeof(szPeaks) <= ms->buf_exact_mz_len) {
		memcpy(ms->buf_exact_mz, szPeaks, sizeof(szPeaks));
		pPeakBuf = ms->buf_exact_mz;
		bIncludeExactMZ = 1;
	} else {
		pPeakBuf = szPeaks;
		bIncludeExactMZ = 0;
	}

	/* count peaks, find max. abundance, store pointers to peaks */
	for (i = 0, p = pPeakBuf; *p; p++, i++) {
		/* p points to the peak text data; store it */
		if (bIncludeExactMZ) {
			if (i < ms->exact_mz_len) {
				ms->exact_mz[i] = p;
			} else {
				return -1; /* not enough room */
			}
		}

		/* read one peak */
		dMz = strtod(p, &q);
		p = q + 1;
		dAbund = strtod(p, &q);
		p = q + strlen(q);
		if (dMaxAbund < dAbund) {
			dMaxAbund = dAbund;
		}
	}

	if (bIncludeExactMZ) {
		ms->num_exact_mz = i; /* store number of exact m/z peaks */
	}

	/* store integral peaks */
	for (i = 0, p = pPeakBuf; *p; p++) {
		/* read one peak */
		dMz = strtod(p, &q);
		p = q + 1;
		dAbund = strtod(p, &q);
		p = q + strlen(q);
		/* rounding */
		rounded_mz = (unsigned int)floor(dMz + 0.5);
		rounded_ab = (unsigned int)floor(0.1 + (999.0 * dAbund / dMaxAbund));
		/* assuming m/z in ascending order */
		if (i && rounded_mz == ms->mass[i - 1]) {
			/* same integral m/z: choose greater abundance */
			if (ms->abund[i - 1] < rounded_ab)
				ms->abund[i - 1] = rounded_ab;
		} else if (i < NISTMS_MAXPEAKS) {
			/* add next integral peak */
			ms->mass[i] = rounded_mz;
			ms->abund[i] = rounded_ab;
			i++;
		} else {
			break; /* Too many peaks; in this simple example we ignore the rest. */
			/* Actually, the smallest peaks are to be ignored, not the last ones */
			/* If many peaks have same small abundance then first peaks */
			/* to be ignored are the peaks with smallest m/z. */
		}
	}
	ms->num_peaks = i; /* store the number of integral m/z peaks; ms->num_peaks <= ms->num_exact_mz */

	return ms->num_peaks; /* number of integral m/z peaks */
}

// static int initialize_libs(NISTMS_IO *pio) {
//	num_libs     = 0;
//	lib_paths[0] = 0;
//
//	strcpy(lib_paths,  FULL_PATH_TO_MAIN_LIBRARY);
//
//	printf("%s", lib_paths);
//
//	lib_types[num_libs++] = NISTMS_MAIN_LIB;
//
//	lib_types[num_libs] = '\0';
//
//	/*  order number of NISTMS_MAIN_LIB in active_lib[] will be 1 */
//	/*  order number of NISTMS_USER_LIB in active_lib[] will be 2 */
//	/*  order number of NISTMS_REP_LIB  in active_lib[] will be 3 */
//	/*  order number of another NISTMS_USER_LIB in active_lib[] will be 4 */
//
//	/*  attach initialization information to NISTMS_IO structure */
//	pio->num_libs = (unsigned int)num_libs;
//	pio->lib_paths = lib_paths;
//	pio->lib_types = lib_types;
//
//	strcpy(work_dir_path, FULL_PATH_TO_WORK_DIR);
//	pio->work_dir_path=work_dir_path;
//
//	/* attach callback function pointer */
//	pio->callback = CallBack;
//
//	nistms_search(NISTMS_INIT_SRCH, pio);
//
//	/* no need for paths and callback until next NISTMS_INIT_SRCH */
//	pio->work_dir_path=NULL;
//	pio->lib_paths    =NULL;
//	pio->callback     =NULL;
//
//
//	/* make sure struct. parts of user libraries are properly indexed */
//	if ( !pio->error_code ) {
//		active_libs[0] = 1; //2; /* user library */
//		active_libs[1] = 0; //4; /* another user library */
//		active_libs[2] = 0;
//		pio->active_libs = active_libs;
//		nistms_search(NISTMS_INDEX_USER_STRU, pio);
//	} else {
//		printf("%d code here...",pio->error_code) ;
//	}
//
//	return(pio->error_code);
// }
//

/**********************************************************************
 Function for retrieving all data associated with a spectrum, including:
   1) peaks, including accurate m/z peaks if available
   2) various identification and other textual information
   3) synonyms (optional),
   4) chemical structure (optional) and
   5) any replicate spectra locations (optional)
   6) NIST Pepdide library-specific references (optional)

 INPUT:
	1) Spectrum offset location (pio->input_spec_loc)
	2) Allocated buffers for any information to be returned
	   (for optional data, NULL signals that the data should not be returned)

 OUTPUT:
	1) Library mass spectrum (in NISTMS_MASS_SPECTURM structure)
	2) Compound identification text (in NISTMS_AUX_DATA structure)
	3) Alternate chemical names (in synonyms field of NISTMS_AUX_DATA)
	4) Chemical structure (in STDATA field of NISTMS_AUX_DATA)
	5) Replicate spectra locations (rep_locs[] in NISTMS_AUX_DATA)

  If optional data is not needed, retrieval will be faster if the
  corresponding fields are NULL.
***************************************************************************/
static void get_spectrum(NISTMS_IO *pio, NISTMS_RECLOC *fpos) { get_spectrum_int_or_accurate_mz(pio, fpos, 1); }
/*****************************************************************/
static void get_spectrum_int_or_accurate_mz(NISTMS_IO *pio, NISTMS_RECLOC *fpos, int bAccurate_mz) {
	static NISTMS_MASS_SPECTRUM ms; /*  required */
	static NISTMS_AUX_DATA aux;		/*  optionsl */
	static NISTMS_STDATA stdata;	/*  optional */
	// #define MAX_NUM_REPLICATES  10              /*  larger than ever needed */
	static NISTMS_RECLOC rep_locs[NISTMS_MAXREPLICATES]; /*  optional */

	#if (defined(ALLOW_MSMS_VERSION))
	/* larger peptide-specific 'peaks text info' sizes may be needed */
	#define MZ_PEAK_NUM NISTMS_DFLT_MAX_PEAK_TXTDATA_NUM
	#define MZ_TEXT_SIZE NISTMS_DFLT_MAX_PEAK_TXTDATA_LEN
	static char szMzText[MZ_TEXT_SIZE];			   /* buffer to hold 'peaks text info' */
	static char *pMzPtr[MZ_PEAK_NUM];			   /* pointers to peaks */
	#define REFERENCES_LEN NISTMS_MAXREFERENCESLEN /* may be greater */
	static char szReferences[REFERENCES_LEN];
	#endif

	memset(&ms, '\0', sizeof(ms));
	memset(&aux, '\0', sizeof(aux));

	#if (defined(ALLOW_MSMS_VERSION))
		if (bAccurate_mz) {
			// additional members for accurate m/z in mass spectral peaks
			ms.exact_mz = pMzPtr;				/* pointers to peaks */
			ms.exact_mz_len = MZ_PEAK_NUM;		/* max. number of peaks */
			ms.num_exact_mz = 0;				/* current number of peaks */
			ms.buf_exact_mz = szMzText;			/* buffer to hold 'peaks text info' */
			ms.buf_exact_mz_len = MZ_TEXT_SIZE; /* buffer size */
		}
	#endif

	printf("Gathering Data for spectrum at location %ld\n", fpos);
	pio->input_spec_loc = fpos; /* most significant 4 bits=lib number, the rest=file offset */

	pio->libms = &ms;
	pio->aux_data = &aux;

	/*  get chemical structures when io->stdata != NULL */
	memset(&stdata, '\0', sizeof(stdata));
	pio->stdata = &stdata;

	if (pio->aux_data) {
		/*  get synonyms when io->aux_data->synonyms != NULL */
		memset(g_synonyms, '\0', sizeof(g_synonyms));
		pio->aux_data->synonyms = g_synonyms;
		pio->aux_data->synonyms_len = sizeof(g_synonyms);

		/*  get any replicates in replicate library if io->aux_data->rep_locs != NULL */
		pio->aux_data->num_rep_locs = NISTMS_MAXREPLICATES;
		pio->aux_data->rep_locs = rep_locs;

			// get contributor for NIST library or comment for user library
			memset(g_contributor, '\0', sizeof(g_contributor));
			pio->aux_data->contributor = g_contributor;
			pio->aux_data->contributor_len = sizeof(g_contributor);
	#if (defined(ALLOW_MSMS_VERSION))
			if (bAccurate_mz) {
				/* peptide library spectrum origin references */
				/* tab-delimited refernce fields:
				   Dataset, Contributor, Number of Files, Source, Reference, Title, Authors.
				   Each reference is zero-terminated; the last reference has an additional zero termination
				   The reference's zero termination byte may be located after any field.
				 */
				pio->aux_data->references     = szReferences;
				pio->aux_data->references_len = REFERENCES_LEN;
				pio->aux_data->num_references = 0; /* will be filled with the number of references */
			}
	#endif
		}
		/*  this will fill io with data */
		nistms_search(NISTMS_GET_SPECTRUM_SRCH, pio);

		/* show_spectrum(io);*/

	//    printf("Name: %s\n", pio->aux_data->name);
	//    printf("CAS: %ld\n", pio->aux_data->casno);
	//    printf("NIST Num: %ld\n", pio->aux_data->specno);
	//    printf("ID: %ld##\n", pio->aux_data->ident);
	//    printf("MW: %d##\n", pio->aux_data->mw);
	//    printf("Exact Mass: %d##\n", pio->aux_data->exact_mw);
	//    printf("Formula: %s##\n", pio->aux_data->formula);
	//    printf("Contributor: %s##\n", pio->aux_data->contributor);
	//
	//	printf("MS Num Peaks: %d##\n", pio->libms->num_peaks);
	//
	//	for (int i=0; i < pio->libms->num_peaks; i++) {
	//		printf("\tmz, Intensity: %d %d\n", pio->libms->mass[i], pio->libms->abund[i]);
	//	}

	return;
#if (defined(ALLOW_MSMS_VERSION))
	#undef MZ_PEAK_NUM
	#undef MZ_TEXT_SIZE
	#undef REFERENCES_LEN
#endif
}
/**************************************************************************/

static int do_init_api(NISTMS_IO *pio, char *lib_paths, char *lib_types, unsigned int num_libs, char *work_dir) {
	// num_libs = 0;
	// lib_paths[0] = 0;

	// strcpy(lib_paths, lib_path);

	printf("Using the following %d libraries:\n", num_libs);
	for (int i = 0; i <= 255; i++) {
		if (lib_paths[i] == 0)
			break;
		else if (lib_paths[i] == 13) { // \r
			printf("; ");
		} else {
			printf("%c", lib_paths[i]);
		}
	}
	printf("\n");

	// lib_types[num_libs++] = lib_type;

	// lib_types[num_libs] = '\0';

	/*  order number of NISTMS_MAIN_LIB in active_lib[] will be 1 */
	/*  order number of NISTMS_USER_LIB in active_lib[] will be 2 */
	/*  order number of NISTMS_REP_LIB  in active_lib[] will be 3 */
	/*  order number of another NISTMS_USER_LIB in active_lib[] will be 4 */

	/*  attach initialization information to NISTMS_IO structure */
	pio->num_libs = (unsigned int)num_libs;
	pio->lib_paths = lib_paths;
	pio->lib_types = lib_types;

	strcpy(work_dir_path, work_dir);
	pio->work_dir_path = work_dir_path;

	/* attach callback function pointer */
	pio->callback = CallBack;

	nistms_search(NISTMS_INIT_SRCH, pio);

	/* no need for paths and callback until next NISTMS_INIT_SRCH */
	pio->work_dir_path = NULL;
	pio->lib_paths = NULL;
	pio->callback = NULL;

	// TODO: handle more than one (user) library
	/* make sure struct. parts of user libraries are properly indexed */
	if (!pio->error_code) {
		active_libs[0] = 1; // 2; /* user library */
		active_libs[1] = 0; // 4; /* another user library */
		active_libs[2] = 0;
		pio->active_libs = active_libs;
		nistms_search(NISTMS_INDEX_USER_STRU, pio);
	}
//	else {
//
//		printf("%d code here...",pio->error_code) ;
//	}

	return (pio->error_code);
}

static PyObject *init_api(PyObject *self, PyObject *args) {
	char *lib_paths;
	Py_ssize_t lib_paths_size;
	char *lib_types;
	Py_ssize_t lib_types_size;
	unsigned int num_libs;
	char *work_dir;

	int ok = PyArg_ParseTuple(args, "s#s#is", &lib_paths, &lib_paths_size, &lib_types, &lib_types_size, &num_libs, &work_dir);
	int err_code = do_init_api(&io, lib_paths, lib_types, num_libs, work_dir);

	if (err_code) {
		PyErr_Format(PyExc_ValueError,
                 "Unable to initialize NIST DLL\nEnsure you are passing valid paths for the library and working directory.\nError code: %d.",
                 err_code
                 );

		return NULL;
	}

	// Reset active_libs
	for (int pos = 0; pos < NISTMS_MAX_LIBS; pos++) {
		active_libs[pos] = 0;
	}

	// Enable the provided libraries in order given
	for (int lib_idx = 0; lib_idx < num_libs; lib_idx++) {
		active_libs[lib_idx] = lib_idx + 1;
	}

	/*  select libraries to search; some searches apply to multiple libraries, */
	/*  while other search only the first active library or do not need        */
	/*  the list of active libraries at all.                                   */
	io.active_libs = active_libs;

	io.string_in = StringIn;

	Py_RETURN_NONE;
}

static PyMethodDef Methods[] = { { "_spectrum_search", spec_search, METH_VARARGS,
								   "Searches the library with search type 'NISTMS_NO_PRE_SRCH'" },
								 { "_full_spectrum_search", full_spec_search, METH_VARARGS, "" },
								 { "_get_reference_data", get_reference_data, METH_VARARGS, "" },
								 { "_init_api", init_api, METH_VARARGS, "" },
								 { "_cas_search", cas_search, METH_VARARGS, "" },
								 // {"_get_lib_paths", get_lib_paths, METH_VARARGS, ""},
								 { "_get_active_libs", get_active_libs, METH_VARARGS, "" },
								 { NULL, NULL } };

static struct PyModuleDef _core = { PyModuleDef_HEAD_INIT, "_core",
									"Python interface for the NIST Spectral Search library", -1, Methods };

PyMODINIT_FUNC PyInit__core(void) {
	/*************************************************************************
	One-time initialization of the NIST DLL
	This sets up database buffers and library locations.
	*************************************************************************/

	io.string_in = "2.1.1";
	nistms_search(NISTMS_SET_VERSION, &io);
	if (io.error_code) {
		PyErr_Format(PyExc_ImportError, "This NIST DLL version is below 2.1.1\n");
		return NULL;
	}

//	if (initialize_libs(&io)) {
//		printf( "Initiation error %d. Press Enter to terminate.\n", io.error_code );
//	}
//	/*  refers to NISTMS_MAIN_LIB, see above */
//	active_libs[0] = 1; // Main NIST Library or Peptide lib 1 (yeast)
//
//	/*  select libraries to search; some searches apply to multiple libraries, */
//	/*  while other search only the first active library or do not need        */
//	/*  the list of active libraries at all.                                   */
//	io.active_libs = active_libs;
//
//	io.string_in = StringIn;

	PyObject *py_module = PyModule_Create(&_core);

	PyObject_SetAttrString(py_module, "COUNT_REF_PEAKS", Py_BuildValue("i", COUNT_REF_PEAKS));
	PyObject_SetAttrString(py_module, "EXACTMW_CONS", Py_BuildValue("i", EXACTMW_CONS));
	PyObject_SetAttrString(py_module, "INSTR_TYPE_CONS", Py_BuildValue("i", INSTR_TYPE_CONS));
	PyObject_SetAttrString(py_module, "PROD_PEAK_TOL_IN_PPM", Py_BuildValue("i", PROD_PEAK_TOL_IN_PPM));
	PyObject_SetAttrString(py_module, "PRECUR_MZ_TOL_IN_PPM", Py_BuildValue("i", PRECUR_MZ_TOL_IN_PPM));
	PyObject_SetAttrString(py_module, "INTERNALBUILD", Py_BuildValue("i", INTERNALBUILD));
	PyObject_SetAttrString(py_module, "MSTXTDATA", Py_BuildValue("i", MSTXTDATA));
	PyObject_SetAttrString(py_module, "NO_VALUE", Py_BuildValue("i", NO_VALUE));
	PyObject_SetAttrString(py_module, "NISTMS_MAXCONTRIBLEN", Py_BuildValue("i", NISTMS_MAXCONTRIBLEN));
	PyObject_SetAttrString(py_module, "NISTMS_PATH_SEPARATOR", Py_BuildValue("s", NISTMS_PATH_SEPARATOR));
	PyObject_SetAttrString(py_module, "NUM_ADD_SPEC_MATCHFACT", Py_BuildValue("i", NUM_ADD_SPEC_MATCHFACT));
	PyObject_SetAttrString(py_module, "COLHDRLEN", Py_BuildValue("i", COLHDRLEN));
	PyObject_SetAttrString(py_module, "NISTMS_MAXSYNONYMLEN", Py_BuildValue("i", NISTMS_MAXSYNONYMLEN));
	PyObject_SetAttrString(py_module, "NISTMS_MAXREFERENCESLEN", Py_BuildValue("i", NISTMS_MAXREFERENCESLEN));
	PyObject_SetAttrString(py_module, "NISTMS_MAIN_LIB", Py_BuildValue("i", NISTMS_MAIN_LIB));
	PyObject_SetAttrString(py_module, "NISTMS_USER_LIB", Py_BuildValue("i", NISTMS_USER_LIB));
	PyObject_SetAttrString(py_module, "NISTMS_REP_LIB", Py_BuildValue("i", NISTMS_REP_LIB));
	PyObject_SetAttrString(py_module, "NISTMS_NOT_A_LIBRARY", Py_BuildValue("i", NISTMS_NOT_A_LIBRARY));
	PyObject_SetAttrString(py_module, "NISTMS_MAX_FPOS", Py_BuildValue("i", NISTMS_MAX_FPOS));
	PyObject_SetAttrString(py_module, "NISTMS_MAX_LIBS", Py_BuildValue("i", NISTMS_MAX_LIBS));
	PyObject_SetAttrString(py_module, "MAX_NOPRESRCH_HITS", Py_BuildValue("i", MAX_NOPRESRCH_HITS));
	PyObject_SetAttrString(py_module, "MAX_LIB_SRCH_HITS", Py_BuildValue("i", MAX_LIB_SRCH_HITS));
	PyObject_SetAttrString(py_module, "NISTMS_MAXBONDS", Py_BuildValue("i", NISTMS_MAXBONDS));
	PyObject_SetAttrString(py_module, "NISTMS_MAXCIRCS", Py_BuildValue("i", NISTMS_MAXCIRCS));
	PyObject_SetAttrString(py_module, "NISTMS_MAXSTRINGS", Py_BuildValue("i", NISTMS_MAXSTRINGS));
	PyObject_SetAttrString(py_module, "NISTMS_MAXSTRINGLEN", Py_BuildValue("i", NISTMS_MAXSTRINGLEN));
	PyObject_SetAttrString(py_module, "NISTMS_MAXREPLICATES", Py_BuildValue("i", NISTMS_MAXREPLICATES));
	PyObject_SetAttrString(py_module, "NISTMS_MAXANYPEAKS", Py_BuildValue("i", NISTMS_MAXANYPEAKS));
	PyObject_SetAttrString(py_module, "NISTMS_MAXPEAKS", Py_BuildValue("i", NISTMS_MAXPEAKS));
	PyObject_SetAttrString(py_module, "NISTMS_DFLT_MAX_PEAK_TXTDATA_NUM",
						   Py_BuildValue("i", NISTMS_DFLT_MAX_PEAK_TXTDATA_NUM));
	PyObject_SetAttrString(py_module, "NISTMS_DFLT_MAX_PEAK_TXTDATA_LEN",
						   Py_BuildValue("i", NISTMS_DFLT_MAX_PEAK_TXTDATA_LEN));
	PyObject_SetAttrString(py_module, "NISTMS_MAXNAMELEN", Py_BuildValue("i", NISTMS_MAXNAMELEN));
	PyObject_SetAttrString(py_module, "NISTMS_MAXFORMLEN", Py_BuildValue("i", NISTMS_MAXFORMLEN));
	PyObject_SetAttrString(py_module, "NISTMS_EXACT", Py_BuildValue("i", NISTMS_EXACT));
	PyObject_SetAttrString(py_module, "NISTMS_ELS_IN_LIST", Py_BuildValue("i", NISTMS_ELS_IN_LIST));
	PyObject_SetAttrString(py_module, "NISTMS_REL_PEAKS", Py_BuildValue("i", NISTMS_REL_PEAKS));
	PyObject_SetAttrString(py_module, "NISTMS_ABS_PEAKS", Py_BuildValue("i", NISTMS_ABS_PEAKS));
	PyObject_SetAttrString(py_module, "NISTMS_NUM_CONSTR_EL", Py_BuildValue("i", NISTMS_NUM_CONSTR_EL));
	PyObject_SetAttrString(py_module, "NISTMS_LEN_CONSTR_EL", Py_BuildValue("i", NISTMS_LEN_CONSTR_EL));
	PyObject_SetAttrString(py_module, "NISTMS_NUM_CONSTR_PK", Py_BuildValue("i", NISTMS_NUM_CONSTR_PK));
	PyObject_SetAttrString(py_module, "NISTMS_NAMEFRAG_LEN", Py_BuildValue("i", NISTMS_NAMEFRAG_LEN));
	PyObject_SetAttrString(py_module, "NISTMS_COMMNT_TAG_LEN", Py_BuildValue("i", NISTMS_COMMNT_TAG_LEN));
	PyObject_SetAttrString(py_module, "NISTMS_PEPNAME_FRAG_LEN", Py_BuildValue("i", NISTMS_PEPNAME_FRAG_LEN));
	PyObject_SetAttrString(py_module, "WARNING_NUM", Py_BuildValue("i", WARNING_NUM));
	PyObject_SetAttrString(py_module, "MAX_WARN_STR", Py_BuildValue("i", MAX_WARN_STR));
	// PyObject_SetAttrString(py_module, "INTERP_DEF", Py_BuildValue("i", INTERP_DEF));
	PyObject_SetAttrString(py_module, "NUM_SUBS", Py_BuildValue("i", NUM_SUBS));
	PyObject_SetAttrString(py_module, "NUM_MW_ESTIMATES", Py_BuildValue("i", NUM_MW_ESTIMATES));
	PyObject_SetAttrString(py_module, "NISTMS_MAX_USER_STRUCT_FILES", Py_BuildValue("i", NISTMS_MAX_USER_STRUCT_FILES));
	PyObject_SetAttrString(py_module, "NISTMS_F32_VALUE_ONE", Py_BuildValue("i", NISTMS_F32_VALUE_ONE));
	PyObject_SetAttrString(py_module, "NISTMS_F32_VALUE_075", Py_BuildValue("i", NISTMS_F32_VALUE_075));
	PyObject_SetAttrString(py_module, "NISTMS_PREC_MZ_ONE", Py_BuildValue("i", NISTMS_PREC_MZ_ONE));
	PyObject_SetAttrString(py_module, "NISTMS_FAKE_PREC_MZ", Py_BuildValue("i", NISTMS_FAKE_PREC_MZ));

	enum tagNISTMS_PEAK_TYPE peak_type;
	peak_type = NISTMS_ANY_PEAK;
	PyObject_SetAttrString(py_module, "NISTMS_ANY_PEAK", Py_BuildValue("i", peak_type));
	peak_type = NISTMS_LOSS_PEAK;
	PyObject_SetAttrString(py_module, "NISTMS_LOSS_PEAK", Py_BuildValue("i", peak_type));
	peak_type = NISTMS_MAXMASS_PEAK;
	PyObject_SetAttrString(py_module, "NISTMS_MAXMASS_PEAK", Py_BuildValue("i", peak_type));
	peak_type = NISTMS_AM2_PEAK;
	PyObject_SetAttrString(py_module, "NISTMS_AM2_PEAK", Py_BuildValue("i", peak_type));
	peak_type = NISTMS_RANK_PEAK;
	PyObject_SetAttrString(py_module, "NISTMS_RANK_PEAK", Py_BuildValue("i", peak_type));
	peak_type = NISTMS_EXACT_MASS_PEAK;
	PyObject_SetAttrString(py_module, "NISTMS_EXACT_MASS_PEAK", Py_BuildValue("i", peak_type));

	enum tagNIST_INSTR_TYPE instr_type;
	instr_type = NISTMS_INSTR_TYPE_NONE;
	PyObject_SetAttrString(py_module, "NISTMS_INSTR_TYPE_NONE", Py_BuildValue("i", instr_type));
	instr_type = NISTMS_INSTR_TYPE_IONTRAP;
	PyObject_SetAttrString(py_module, "NISTMS_INSTR_TYPE_IONTRAP", Py_BuildValue("i", instr_type));
	instr_type = NISTMS_INSTR_TYPE_QTOF;
	PyObject_SetAttrString(py_module, "NISTMS_INSTR_TYPE_QTOF", Py_BuildValue("i", instr_type));
	instr_type = NISTMS_INSTR_TYPE_QQQ;
	PyObject_SetAttrString(py_module, "NISTMS_INSTR_TYPE_QQQ", Py_BuildValue("i", instr_type));
	instr_type = NISTMS_INSTR_TYPE_UNK;
	PyObject_SetAttrString(py_module, "NISTMS_INSTR_TYPE_UNK", Py_BuildValue("i", instr_type));
	instr_type = NISTMS_INSTR_TYPE_MASK;
	PyObject_SetAttrString(py_module, "NISTMS_INSTR_TYPE_MASK", Py_BuildValue("i", instr_type));
	instr_type = NIST_INSTR_TYPE_NOT_IN_LIBREC;
	PyObject_SetAttrString(py_module, "NIST_INSTR_TYPE_NOT_IN_LIBREC", Py_BuildValue("i", instr_type));

	enum tagNISTMS_BIT_INSTR_TYPE bit_instr_type;
	bit_instr_type = NISTMS_BIT_INSTR_TYPE_NONE;
	PyObject_SetAttrString(py_module, "NISTMS_BIT_INSTR_TYPE_NONE", Py_BuildValue("i", bit_instr_type));
	bit_instr_type = NISTMS_BIT_INSTR_TYPE_IONTRAP;
	PyObject_SetAttrString(py_module, "NISTMS_BIT_INSTR_TYPE_IONTRAP", Py_BuildValue("i", bit_instr_type));
	bit_instr_type = NISTMS_BIT_INSTR_TYPE_QTOF;
	PyObject_SetAttrString(py_module, "NISTMS_BIT_INSTR_TYPE_QTOF", Py_BuildValue("i", bit_instr_type));
	bit_instr_type = NISTMS_BIT_INSTR_TYPE_QQQ;
	PyObject_SetAttrString(py_module, "NISTMS_BIT_INSTR_TYPE_QQQ", Py_BuildValue("i", bit_instr_type));
	bit_instr_type = NISTMS_BIT_INSTR_TYPE_OTHER;
	PyObject_SetAttrString(py_module, "NISTMS_BIT_INSTR_TYPE_OTHER", Py_BuildValue("i", bit_instr_type));

	enum tagNISTMS_SPECTRUM_FLAGS spec_flags;
	spec_flags = NISTMS_SPEC_FLAG_PEPSEQ_MASK;
	PyObject_SetAttrString(py_module, "NISTMS_SPEC_FLAG_PEPSEQ_MASK", Py_BuildValue("i", spec_flags));
	spec_flags = NISTMS_SPEC_FLAG_PEPSEQ_NOT_SEARCHED;
	PyObject_SetAttrString(py_module, "NISTMS_SPEC_FLAG_PEPSEQ_NOT_SEARCHED", Py_BuildValue("i", spec_flags));
	spec_flags = NISTMS_SPEC_FLAG_PEPSEQ_IN_NAME;
	PyObject_SetAttrString(py_module, "NISTMS_SPEC_FLAG_PEPSEQ_IN_NAME", Py_BuildValue("i", spec_flags));
	spec_flags = NISTMS_SPEC_FLAG_PEPSEQ_IN_SYN;
	PyObject_SetAttrString(py_module, "NISTMS_SPEC_FLAG_PEPSEQ_IN_SYN", Py_BuildValue("i", spec_flags));
	spec_flags = NISTMS_SPEC_FLAG_PEPSEQ_NOT_PRESENT;
	PyObject_SetAttrString(py_module, "NISTMS_SPEC_FLAG_PEPSEQ_NOT_PRESENT", Py_BuildValue("i", spec_flags));
	spec_flags = NISTMS_SPEC_FLAG_PEPSEQ_GENERATED;
	PyObject_SetAttrString(py_module, "NISTMS_SPEC_FLAG_PEPSEQ_GENERATED", Py_BuildValue("i", spec_flags));

	enum tagNISTMS_SEARCH_TYPE search_type;
	search_type = NISTMS_INIT_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_INIT_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_CLOSE_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_CLOSE_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_GET_SPECTRUM_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_GET_SPECTRUM_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_GET_STRUCTURE_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_GET_STRUCTURE_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_GET_SYNONYMS_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_GET_SYNONYMS_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_NAME_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_NAME_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_CASNO_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_CASNO_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_ID_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_ID_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_ANYPEAK_INIT_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_ANYPEAK_INIT_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_ANYPEAK_ONE_PEAK_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_ANYPEAK_ONE_PEAK_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_ANYPEAK_GET_HITS_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_ANYPEAK_GET_HITS_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_INC_FIRST_NAME_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_INC_FIRST_NAME_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_INC_NEXT_NAME_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_INC_NEXT_NAME_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_INC_PREV_NAME_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_INC_PREV_NAME_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_INC_GET_NAME_KEY;
	PyObject_SetAttrString(py_module, "NISTMS_INC_GET_NAME_KEY", Py_BuildValue("i", search_type));
	search_type = NISTMS_MW_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_MW_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_REP_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_REP_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_FORMULA_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_FORMULA_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_SEQ_ID_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_SEQ_ID_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_SCREEN_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_SCREEN_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_COMPARE_SPECTRA_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_COMPARE_SPECTRA_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_NO_PRE_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_NO_PRE_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_ADD_TO_LIBRARY_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_ADD_TO_LIBRARY_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_DELETE_FROM_LIBRARY_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_DELETE_FROM_LIBRARY_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_INDEX_LIBRARY_NAMES;
	PyObject_SetAttrString(py_module, "NISTMS_INDEX_LIBRARY_NAMES", Py_BuildValue("i", search_type));
	search_type = NISTMS_CREATE_LIBRARY;
	PyObject_SetAttrString(py_module, "NISTMS_CREATE_LIBRARY", Py_BuildValue("i", search_type));
	search_type = NISTMS_CL_BR_EST;
	PyObject_SetAttrString(py_module, "NISTMS_CL_BR_EST", Py_BuildValue("i", search_type));
	search_type = NISTMS_MW_EST;
	PyObject_SetAttrString(py_module, "NISTMS_MW_EST", Py_BuildValue("i", search_type));
	search_type = NISTMS_SUBSTR_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_SUBSTR_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_MW_ESTIMATION_2;
	PyObject_SetAttrString(py_module, "NISTMS_MW_ESTIMATION_2", Py_BuildValue("i", search_type));
	search_type = NISTMS_OPEN_MOLFILE;
	PyObject_SetAttrString(py_module, "NISTMS_OPEN_MOLFILE", Py_BuildValue("i", search_type));
	search_type = NISTMS_CLOSE_MOLFILE;
	PyObject_SetAttrString(py_module, "NISTMS_CLOSE_MOLFILE", Py_BuildValue("i", search_type));
	search_type = NISTMS_SCAN_USER_STRU_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_SCAN_USER_STRU_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_STRU_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_STRU_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_INDEX_USER_STRU;
	PyObject_SetAttrString(py_module, "NISTMS_INDEX_USER_STRU", Py_BuildValue("i", search_type));
	search_type = NISTMS_STRING_TO_ASCII;
	PyObject_SetAttrString(py_module, "NISTMS_STRING_TO_ASCII", Py_BuildValue("i", search_type));
	search_type = NISTMS_STRING_TO_GREEK;
	PyObject_SetAttrString(py_module, "NISTMS_STRING_TO_GREEK", Py_BuildValue("i", search_type));
#if (MSTXTDATA == 1)
	search_type = NISTMS_SET_VERSION;
	PyObject_SetAttrString(py_module, "NISTMS_SET_VERSION", Py_BuildValue("i", search_type));
	search_type = NISTMS_DECODE_MODS;
	PyObject_SetAttrString(py_module, "NISTMS_DECODE_MODS", Py_BuildValue("i", search_type));
#endif
	search_type = NISTMS_MAKE_MOLFILE;
	PyObject_SetAttrString(py_module, "NISTMS_MAKE_MOLFILE", Py_BuildValue("i", search_type));
	search_type = NISTMS_ALT2AROM;
	PyObject_SetAttrString(py_module, "NISTMS_ALT2AROM", Py_BuildValue("i", search_type));
	search_type = NISTMS_MARK_LIBS;
	PyObject_SetAttrString(py_module, "NISTMS_MARK_LIBS", Py_BuildValue("i", search_type));
	search_type = NISTMS_MARK_ALL_LIBS;
	PyObject_SetAttrString(py_module, "NISTMS_MARK_ALL_LIBS", Py_BuildValue("i", search_type));
#if (EXACTMW == 1)
	search_type = NISTMS_INDEX_LIBRARY_EXACT_MASS;
	PyObject_SetAttrString(py_module, "NISTMS_INDEX_LIBRARY_EXACT_MASS", Py_BuildValue("i", search_type));
	search_type = NISTMS_EXACT_MASS_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_EXACT_MASS_SRCH", Py_BuildValue("i", search_type));
	search_type = NISTMS_GET_EXACT_MASS_LIMITS;
	PyObject_SetAttrString(py_module, "NISTMS_GET_EXACT_MASS_LIMITS", Py_BuildValue("i", search_type));
	search_type = NISTMS_EXACT_MZ_TO_INT_PEAKS;
	PyObject_SetAttrString(py_module, "NISTMS_EXACT_MZ_TO_INT_PEAKS", Py_BuildValue("i", search_type));
#endif
	search_type = NISTMS_CASNO_SRCH2;
	PyObject_SetAttrString(py_module, "NISTMS_CASNO_SRCH2", Py_BuildValue("i", search_type));
	search_type = NISTMS_NISTNO_SRCH;
	PyObject_SetAttrString(py_module, "NISTMS_NISTNO_SRCH", Py_BuildValue("i", search_type));

	enum SEARCH_MODE_FLAGS search_mode_flags;
	search_mode_flags = SEARCH_MODE_FLAG_IGNORE_PRECURSOR;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_IGNORE_PRECURSOR", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_FLAG_FAST_PRESEARCH;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_FAST_PRESEARCH", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_FLAG_ALT_PEAK_MATCHING;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_ALT_PEAK_MATCHING", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_FLAG_GENERIC_MSMS;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_GENERIC_MSMS", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_FLAG_REJECT_OTHER;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_REJECT_OTHER", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_FLAG_PRECUR_MZ_TOL_PPM;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_PRECUR_MZ_TOL_PPM", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_FLAG_PROD_PEAK_TOL_PPM;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_PROD_PEAK_TOL_PPM", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_FLAG_MASK;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_FLAG_MASK", Py_BuildValue("i", search_mode_flags));
	search_mode_flags = SEARCH_MODE_CHAR_MASK;
	PyObject_SetAttrString(py_module, "SEARCH_MODE_CHAR_MASK", Py_BuildValue("i", search_mode_flags));

#ifdef MSPEPSEARCH
	/* used in MSPepSEarch only */
	#ifndef MAP_LIB_FILE_TYPE_DEFINED

	enum MAP_LIB_FILE_TYPE lib_file_type;
	lib_file_type = MM_PEAKIN_PM0;
	PyObject_SetAttrString(py_module, "MM_PEAKIN_PM0", Py_BuildValue("i", lib_file_type));
	lib_file_type = MM_PEAKDB_PM0;
	PyObject_SetAttrString(py_module, "MM_PEAKDB_PM0", Py_BuildValue("i", lib_file_type));
	lib_file_type = MM_MZBIN_INU;
	PyObject_SetAttrString(py_module, "MM_MZBIN_INU", Py_BuildValue("i", lib_file_type));
	lib_file_type = MM_MZBIN_DBU;
	PyObject_SetAttrString(py_module, "MM_MZBIN_DBU", Py_BuildValue("i", lib_file_type));
	lib_file_type = MM_MZPRECUB_INU;
	PyObject_SetAttrString(py_module, "MM_MZPRECUB_INU", Py_BuildValue("i", lib_file_type));

	#endif
#endif

	/*
	USER_DLL_STR_2_0
	USER_DLL_STR_2_1_1
	USER_DLL_STR_2_1_4
	USER_DLL_STR_2_1_5
	USER_DLL_STR_VER
	NISTMS_PATH_SEPARATOR
	*/

	return py_module;
}
