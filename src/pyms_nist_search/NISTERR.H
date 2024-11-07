/*
NISTERR.H

C Interface to the NIST MS Search DLL

From ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip

*/

/*  %Z%%M%   %I%   %G%   RELEASE: %R%   TFLAG %Y%   */
/* from WGET_ID.C */
#define ERR_OUT_OF_RAM -1
#define ERROR_NOT_USER_LIB -2
#define ERR_CANNOT_INIT_CTREEGV -3
#define ERR_CANNOT_INIT_CTREE -4
#define ERR_CANNOT_GET_USER_PATH -5
#define ERR_TOO_MANY_PEAKS -6
#define ERR_CANNOT_LOAD_NAME -7
#define ERR_CANNOT_OPEN_NAMEFILE -8
#define ERR_CANNOT_SETUP_PATHS -9
#define ERR_CANNOT_OPEN_LIB_FILES -10
#define ERR_UNRECOGNIZED_SEARCH_TYPE -11
#define ERR_COULD_NOT_READ_PEAKS -12
#define ERR_LINE_TOO_LONG -13
#define ERR_BUFFERS_NOT_ALLOCATED -14
#define ERR_SEARCH_REENTRY -15		   /* attempt to call search while another search is in progress */
#define ERR_WRONG_ACTIVE_LIB_COUNT -16 /* added 2010-10-08 */
#define ERR_WRONG_LIBRARY -17		   /* added 2010-10-08 */

/* from NISTMS.H */
#define ERR_CANNOT_SETUP_DBS -101
#define ERR_BAD_INPUT_DATA -102
#define ERR_BAD_SEARCH_LIBS -103
#define ERR_CANNOT_SET_ACTIVE_LIBS -104
#define ERR_MKDIR -105
#define ERR_LIB_ALREADY_EXIST -106
#define ERR_CANNOT_CREATE_LIB -107
#define ERR_READING_SPEC -108	   /* 2-10-99 DCh */
#define ERR_CONSTRAINT_SYNTAX -109 /* 4-13-06 DCh */

/* WGET_ANY.C */
#define ERR1 -201	/* out of RAM A */
#define ERR2 -202	/* out of RAM B */
#define ERR3 -203	/* out of RAM C */
#define ERR4 -204	/* current peak values out of range */
#define ERR5 -205	/* selected delete with no peaks */
#define ERR6 -206	/* problem deleting peak */
#define ERR7 -207	/* asked for hits without providing peaks */
#define ERR8 -208	/* too many allowable misses */
#define ERR9 -209	/* problem finding hit id numbers */
#define ERR10 -210	/* problem in find all */
#define ERR11 -211	/* cannot open peakdb file */
#define ERR12 -212	/* error in sorting */
#define ERR13 -213	/* cannot open or read PEAK.DB file */
#define ERR14 -214	/* error in screen search counting */
#define ERR15 -215	/* too many peaks requested; peak ignored */
#define NONEFOUND 2 /* no hits found */

/* WGET_AUT.C */
#define ERR_AUT_OUT_OF_RAM -301
#define ERR_CANNOT_FIND_PEAKS -302
#define ERR_PROBLEM_GETTING_MATCHES -303
#define WRN_NO_SPECTRA_TO_COMPARE -304
#define WRN_TOO_MANY_HITS -305
#define WRN_COULD_NOT_FIND_IDKEY -306

/* MAINMSDB.C */
#define ERR_BAD_DBNUM -400
#define ERR_SEARCH_LIBS_STRING -401
#define ERR_NOT_A_USERLIB -402
#define ERR_MAINLIB_NOT_INSTALLED -403
#define ERR_REPLIB_NOT_INSTALLED -404
#define ERR_WRONG_NUM_LIBS -405
#define ERR_WRONG_ACTIVE_LIBS -406
#define ERR_NOT_INITIALIZED -407
#define ERR_CANNOT_REINITIALIZE -408
#define ERR_NO_NAME_PROVIDED -409
#define ERR_MAX_HITS_DESIRED_TOO_SMALL -409
#define ERR_CANNOT_ALLOCATE_STRUBUF -410
#define ERR_BAD_MOLFILE_HANDLE -411

/* WGET_NAM.C */
#define ERR_NAM_OUT_OF_RAM -501

/* WGET_INP.C */
#define ERR_CANNOT_OPEN_INPUT_FILE -600
#define ERR_PARSING_INPUT_FILE -601
#define ERR_COULD_NOT_FIND_NUM_PEAKS -602
#define ERR_CANNOT_FIND_ASCII_SPECTRUM -603
#define ERR_CANNOT_ALLOC_ABUND -604

#define ERR_MAX_SPEC_LOCS_TOO_SMALL -605

#define WRN_SEARCH_ABORTED -606 /* CallBack returned Cancel. */
