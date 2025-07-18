/*
pyms-nist-search_min.c

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

#include "NISTMS_min.H"
#include "NISTERR.H"

#define MAX_NAME_LEN 120 /*  longest string returned for a name in hit list */

#ifdef WIN32
	#define MAX_FINAL_HITS 6000 /*  largest number of spectra in final hit list */ /*  This value MUST be >= 120 */
#else
	#define MAX_FINAL_HITS 1000 /*  largest number of spectra in final hit list */
/*  This value MUST be >= 120 */
#endif

static PyMethodDef Methods[] = { { NULL, NULL } };

static struct PyModuleDef _core = {
	PyModuleDef_HEAD_INIT,
	"_core",
	"Python interface for the NIST Spectral Search library",
	-1,
	Methods
};

PyMODINIT_FUNC PyInit__core(void) {
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

	enum tagSEARCH_MODE_FLAGS search_mode_flags;
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
