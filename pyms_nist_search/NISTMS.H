/*
NISTMS.H

C Interface to the NIST MS Search DLL

From ftp://chemdata.nist.gov/mass-spc/v1_7/NISTDLL3.zip

*/

#ifndef NISTMS_H
	#define NISTMS_H

	#if ( _MSC_VER >= 1200  )
		#pragma pack(push, 1)
	#endif

	#ifdef __cplusplus
		extern "C" {
	#endif

	/*------- a list of changed sizes -----------
	#define NISTMS_MAXBONDS   254     // was 200
	#define NISTMS_MAXCIRCS   254     // was 200
	#define NISTMS_MAXSTRINGS 254     // was 200
	#define NISTMS_MAXNAMELEN 512     // was 300
	NISTMS_MAXCONTRIBLEN     1024     // was 512 until v.2.0.0.21
	--------------------------------------------*/
	// 2013-02-20 Always #define INTERNALBUILD
	#ifndef INTERNALBUILD
		#define INTERNALBUILD
	#endif

	/* NIST MS DLL user interface specific: use this file
	   *only* in CallDll and NISTMSCL projects.
	   in the dll code, NIST_MS_DLL is defined in the IDE compiler command line
	   for configurations (Release/Debug)_peptides, (Release/Debug)_pep_2gb */
	#ifndef NIST_MS_DLL
		#define NIST_MS_DLL
	#endif

	#ifdef INTERNALBUILD  // new additions: peptide library
		#define MSTXTDATA 1
		//#define NISTMS_6BYTE_RECLOC  // new dll user interface; defined in the Visual Studio IDE project */

		#ifndef EXACTMW_CONS
			#define EXACTMW_CONS     1   /* NIST 11 exact mw constraint */
		#endif

		#ifndef INSTR_TYPE_CONS
			#define INSTR_TYPE_CONS  1   /* NIST 11 instrument type */
		#endif

		#if( (defined(MSPEPSEARCH) || defined(NIST_MS_DLL)) && !defined(COUNT_REF_PEAKS) )
			#define COUNT_REF_PEAKS  1 // 1=> count matching and non-matching reference peaks (=have annotation, not '?')
		#endif

		#if ( !defined(COUNT_REF_PEAKS) )
			#define COUNT_REF_PEAKS  0
		#elif( COUNT_REF_PEAKS == 1 )
			#define PROD_PEAK_TOL_IN_PPM      1  // 1=> allow ppm in peak tolerance 2012-07-24 DCh
			#define PRECUR_MZ_TOL_IN_PPM      1  // 1=> allow ppm in peak tolerance 2012-07-24 DCh
		#endif

	#else  // unsupported old version
		#define MSTXTDATA 0
		#define COUNT_REF_PEAKS  0

	#endif

	#define NO_VALUE          999999999 /* greater than any reasonable value */

	#define USER_DLL_STR_2_0   "2.0"
	#define USER_DLL_STR_2_1_1 "2.1.1"
	#define USER_DLL_STR_2_1_4 "2.1.4"
	#define USER_DLL_STR_2_1_5 "2.1.5"

	#if ( MSTXTDATA == 1 )
		#if ( defined(COUNT_REF_PEAKS) && EXACTMW_CONS==1 && INSTR_TYPE_CONS==1 )
			#define USER_DLL_STR_VER   USER_DLL_STR_2_1_5

		#elif (EXACTMW_CONS==1 && INSTR_TYPE_CONS==1)
			#define USER_DLL_STR_VER   USER_DLL_STR_2_1_4

		#else
			#define USER_DLL_STR_VER   USER_DLL_STR_2_1_1

		#endif

	#else
		#define USER_DLL_STR_VER   USER_DLL_STR_2_0

	#endif

	#if ( MSTXTDATA == 1 )
		#define NISTMS_MAXCONTRIBLEN   2048 /* max length of aux_data->contributor */
		#define NUM_ADD_SPEC_MATCHFACT    (4+COUNT_REF_PEAKS) /* add peptide-specific spectrum match statistics to the Hitlist */

		#define COLHDRLEN                12 /* length of peptide-specific match statistics header string in the the Hitlist */

	#else
		/************ useful limitations on library records *************************/
		#define NISTMS_MAXCONTRIBLEN  1024  // max length of aux_data->contributor
									// field in the user library record
	#endif

	#define NISTMS_MAXSYNONYMLEN  4500  // max. length of aux_data->synonyms
										// retrieved from the NIST 11 Main Library.
	// Note. Since the there is a limit on user library record length (5012 bytes),
	//       at the time the spectrum is added to the user library the number of
	//       synonyms in the record can be automatically reduced to fit the record
	//       length. This change is not reflected in the aux_data->num_synonyms;
	//       the record should be reread to find if the synonyms truncation
	//       actually took place.

	#define NISTMS_MAXREFERENCESLEN 4096 // may be exceeded
	/****************************************************************************/

	/* This character separates library path in NISTMS_IO field lib_paths[] */
	#define NISTMS_PATH_SEPARATOR "\r"

	/**************************************************************************
	 Library types used both for specifying for library initialization
	 (lib_type in the NISTMS_IO structure) and for giving the order of
	 libraries to be searched (active_libs in the NISTMS_IO structure)
	***************************************************************************/
	#define NISTMS_MAIN_LIB 1
	#define NISTMS_USER_LIB 2   // includes MS/MS libraries
	#define NISTMS_REP_LIB  4

	#define NISTMS_NOT_A_LIBRARY -1

	#define NISTMS_MAX_FPOS 6000  /* System limit for number of hits */

	 /* NISTMS_MAX_LIBS = Max. number of libraries that may be initiated at once */
	#if   ( defined(MSPEPSEARCH) )
		#define NISTMS_MAX_LIBS  16    /* System limit for number of libraries in MSPepSearch */

	#elif ( !defined(NIST_MS_DLL) )
		#define NISTMS_MAX_LIBS 127    /* System limit for number of libraries in MS Search */

	#elif ( defined(NISTMS_6BYTE_RECLOC) )
		#define NISTMS_MAX_LIBS 127    /* System limit for number of libraries in Pep_2gb config of NIST MS DLL 2GB */

	#else
		#define NISTMS_MAX_LIBS  16    /* System limit for number of libraries in Peptides config. of NIST MS DLL 0.25 GB */

	#endif


	#define MAX_NOPRESRCH_HITS 400 /* Largest number of hits nistms_search can deliver*/
								   /* in case of sequential spectrum search */

	#define MAX_LIB_SRCH_HITS 100 /* Largest number of hits nistms_search can deliver*/
								  /* in case of library spectrum search. */
								  /* It is a min. value of io->hit_list->max_hits_desired */

	/* These defines and structure are for storage of chemical structure */
	/* information */
	/* -------- previously used sizes
	#define NISTMS_MAXBONDS 200
	#define NISTMS_MAXCIRCS 200
	#define NISTMS_MAXSTRINGS 200
	---------------------------------*/

	/*------ starting from 7-7-99 -----*/
	#define NISTMS_MAXBONDS 254
	#define NISTMS_MAXCIRCS 254
	#define NISTMS_MAXSTRINGS 254
	/*----------------------------------*/
	#define NISTMS_MAXSTRINGLEN 6

	/* added 2013-02-26 */
	#ifdef MAXREPLICAS
		#define NISTMS_MAXREPLICATES MAXREPLICAS

	#else
		#define NISTMS_MAXREPLICATES   10

	#endif


	#ifdef NISTMS_6BYTE_RECLOC
		#if ( STUDY_PRESEARCH == 1 )
			typedef struct tagNISTMS_RECLOC { long loc; char ftype; char lib; short nsc; } NISTMS_RECLOC;
		#else
			typedef struct tagNISTMS_RECLOC { long loc; char ftype; char lib; } NISTMS_RECLOC;
		#endif

		typedef char SLACK_2BYTES[2];
		#define NISTMS_RECLOCSLACK(X) SLACK_2BYTES dummy##X ;
		#define NISTMS_REC_OFFS(X)      (X).loc
		#define NISTMS_REC_OFFS_FULL(X) (X).loc
	#else
		typedef long NISTMS_RECLOC;
		#define NISTMS_RECLOCSLACK(X)
		#define NISTMS_REC_OFFS(X)      ((X) & 0x0FFFFFF)
		#define NISTMS_REC_OFFS_FULL(X) (X)
	#endif

	/**************************************************************************
	 This macro derives the library sequence number from a spectrum position (x)
	 returned by various library access routines.  The first path (and type)
	 given in lib_paths (and lib_types) during initialization is number 0,
	 the second is number 1, and so on.
	***************************************************************************/
	#ifdef NISTMS_6BYTE_RECLOC
		#define NISTMS_LIB_NUM(x) ( (int)( (x).lib ) )

	#else
		#define NISTMS_LIB_NUM(x) ( (int)( ((unsigned long)(x) & 0xF0000000) >> 28 ) )

	#endif

	typedef struct tagNISTMS_STDATA {
		int xl[NISTMS_MAXBONDS], yl[NISTMS_MAXBONDS];
		int num_line_points;
		int num_points;
		char bond_type[NISTMS_MAXBONDS];
		int xc[NISTMS_MAXCIRCS], yc[NISTMS_MAXCIRCS];
		int num_circs;
		int xs[NISTMS_MAXSTRINGS], ys[NISTMS_MAXSTRINGS];
		int num_strs;
		int radpix;  /* not used */
		char str_point[NISTMS_MAXSTRINGS];
		char str[NISTMS_MAXSTRINGS][NISTMS_MAXSTRINGLEN];

		#if( defined(TESTDLL) ) /* unavailable in current releases */
			char iso_atw_diff[NISTMS_MAXSTRINGS];
		#endif
	} NISTMS_STDATA;

	/* used for incremental name search only */
	typedef struct tagNISTMS_INC_NAME_INFO {
		int alpha_only; /*if non-zero only A-Z allowed and prefixes are ignored */
		int num_names_desired; /* maximum # of names returned */
		int one_name_len;  /* length provided for each name */
		char *names; /*allocated by user, length = num_names_desired * one_name_len */

		int num_names; /* number of names actually found */
		unsigned long *id_nums;/* allocated by user, filled with ID number for */
							   /* the library to be searched */
							   /* length = num_names_desired * sizeof(int) */
		/* new stuff */
		int *name_pos;         /* allocated by user, filled with name position */
							   /* numbers for the library to be searched */
							   /* length = num_names_desired * sizeof(int) */
							   /* Note: NULL means use obsolete mode and search */
							   /* MAIN NIST library only */
		int last_name_pos;     /* name_pos for the last name in the library */

		char *name_key;        /* allocated by user; must be 20 bytes or longer */
							   /* used for NISTMS_INC_GET_NAME_KEY only */
	} NISTMS_INC_NAME_INFO;

	/**********************************************************************
	  This enum and the following structure are used for the
	   complex ANYPEAKS type search.  One peak is sent each function call
	   and up to 10 "anypeaks" are allowed
	***********************************************************************/
	#define NISTMS_MAXANYPEAKS 12

	typedef enum tagNISTMS_PEAK_TYPE{
		NISTMS_ANY_PEAK,
		NISTMS_LOSS_PEAK,
		NISTMS_MAXMASS_PEAK,
		NISTMS_AM2_PEAK,
		NISTMS_RANK_PEAK,
		NISTMS_EXACT_MASS_PEAK,
	} NISTMS_PEAK_TYPE;

	typedef struct tagNISTMS_F32PeakSpec {
		/* 12 bytes */
		unsigned int exact_mw_min; /* f32 - 4 bytes */
		unsigned int exact_mw_max; /* f32 - 4 bytes */
		short    abmin; /* 2 bytes */
		short    abmax; /* 2 bytes */
	} NISTMS_PSEXACT;

	typedef struct tagNISTMS_PEAK_INFO {
		/* individual peak specs */
		union {
			struct { /* 12 bytes */
				int mass;
				int abmin;
				int abmax;
			};
			NISTMS_PSEXACT ExactPeak;
		};
		NISTMS_PEAK_TYPE type;

		/* output ANYPEAK #hits info */
		long num_for_peak; /* # spectra found for ANYPEAK peak query */
		long net_num_matches[NISTMS_MAXANYPEAKS]; /* # hits for different # of */

		/* input for getting spectra locations */
		int num_matches_required; /* input minimum number of peaks required */
	} NISTMS_PEAK_INFO;

	/* used to store retrieved library spectrum or to send a spectrum for */
	/*   addition to user library */
	#define NISTMS_MAXPEAKS 800  /* system limit */

	#if( MSTXTDATA == 1 )
		/* limits for NIST MS Search */
		#define NISTMS_DFLT_MAX_PEAK_TXTDATA_NUM  10000
		#define NISTMS_DFLT_MAX_PEAK_TXTDATA_LEN  14*NISTMS_DFLT_MAX_PEAK_TXTDATA_NUM
	#endif

	typedef struct tagNISTMS_MASS_SPECTRUM {
		unsigned int num_peaks;
		unsigned int mass[NISTMS_MAXPEAKS];
		unsigned int abund[NISTMS_MAXPEAKS];

		#if( MSTXTDATA == 1 )     /* DCh 2005-12-05 */
			/* Peptide spectrum searching, retrieval, addition to a user MS library */
			/* version 2.1; in 2.1.1 the order has been changed to the following */
			unsigned precursor_ion_100mz; /* Precursor_m/z*100 as int, or as f32 without mult. by 100 */
			/*long precursor_ion_100mz;*/ /* Changed to unsigned 2011-07-20 DT */
			int  num_exact_mz;     /* number of peaks stored in exact_mz */
			/* User-allocated memory for Petide spectrum retrieval */
			char **exact_mz;       /* allocated by the user array of pointers to tab-delimited
									  zero-terminated triplets "m/z abund annotation" */
			int  exact_mz_len;     /* number of allocated pointers in exact_mz */
			char *buf_exact_mz;    /* a buffer to hold '\0'-delimited exact_mz strings */
			long buf_exact_mz_len; /* allocated length of buf_exact_mz */
		#endif
	} NISTMS_MASS_SPECTRUM;

	typedef enum tagNIST_INSTR_TYPE {
		/* get (NISTMS_AUX_DATA::instr_type & NISTMS_INSTR_TYPE_MASK) to interpret low 5 bits in the byte */
		/* MS/MS spectrum Instrument Type */
		NISTMS_INSTR_TYPE_NONE      = 0,
		NISTMS_INSTR_TYPE_IONTRAP   = 1,
		NISTMS_INSTR_TYPE_QTOF      = 2,  /* QTOF or HCD */
		NISTMS_INSTR_TYPE_QQQ       = 3,
		NISTMS_INSTR_TYPE_UNK       = 0x1F,
		NISTMS_INSTR_TYPE_MASK      = 0x1F,  /* instrument type mask for NISTMS_MASS_SPECTRUM::instr_type */

		NIST_INSTR_TYPE_NOT_IN_LIBREC = 0x20, // when read from lib this bit means no entry found

	} NISTMS_INSTR_TYPE;

	typedef enum tagNISTMS_BIT_INSTR_TYPE {
		NISTMS_BIT_INSTR_TYPE_NONE     = 1<< NISTMS_INSTR_TYPE_NONE,
		NISTMS_BIT_INSTR_TYPE_IONTRAP  = 1<< NISTMS_INSTR_TYPE_IONTRAP,
		NISTMS_BIT_INSTR_TYPE_QTOF     = 1<< NISTMS_INSTR_TYPE_QTOF,
		NISTMS_BIT_INSTR_TYPE_QQQ      = 1<< NISTMS_INSTR_TYPE_QQQ,
		NISTMS_BIT_INSTR_TYPE_OTHER    = ~(NISTMS_BIT_INSTR_TYPE_NONE|
										   NISTMS_BIT_INSTR_TYPE_IONTRAP|
										   NISTMS_BIT_INSTR_TYPE_QTOF|
										   NISTMS_BIT_INSTR_TYPE_QQQ),
	} NISTMS_BIT_INSTR_TYPE;

	/* get (NISTMS_AUX_DATA::spec_flags & NISTMS_SPEC_FLAG_PEPSEQ_MASK) to interpret 2 least significant bits */
	/* which describe location of aminoacid sequence in a peptide spectrum read from NIST 12 nist_msms2 library */
	typedef enum tagNISTMS_SPECTRUM_FLAGS {
		NISTMS_SPEC_FLAG_PEPSEQ_MASK          = 0x03,  // amino acid sequence and charge locaion mask
		NISTMS_SPEC_FLAG_PEPSEQ_NOT_SEARCHED  = 0x00,  // it is unknown if the name or synonyms contain amino acid sequence
		NISTMS_SPEC_FLAG_PEPSEQ_IN_NAME       = 0x01,  // amino acid sequence and charge are in the main name (old format)
		NISTMS_SPEC_FLAG_PEPSEQ_IN_SYN        = 0x02,  // amino acid sequence and NO charge are in $:26 synonym; mods are in $:27 synonym
		NISTMS_SPEC_FLAG_PEPSEQ_NOT_PRESENT   = 0x03,  // NO amino acid sequence is in the spectrum

		NISTMS_SPEC_FLAG_PEPSEQ_GENERATED     = 0x04   // main name was generated from synonyms $:26, $:27 and charge

	} NISTMS_SPECTRUM_FLAGS;


	/* non spectral information associated with library data record */
	#define NISTMS_MAXNAMELEN 512 // was 300
	#define NISTMS_MAXFORMLEN 24

	typedef struct tagNISTMS_AUX_DATA {
		NISTMS_RECLOC spec_loc;      /* location of spectrum */
		NISTMS_RECLOCSLACK(1)        /* make sure the next item is 4-byte boundary aligned */
		NISTMS_RECLOC stru_loc;      /* location of chemical structure */
		NISTMS_RECLOCSLACK(2)        /* make sure the next item is 4-byte boundary aligned */
		unsigned long ident;         /* Database ID number */
		long casno;                  /* CAS Registry Number */
		long specno;                 /* NIST Accession number */
		unsigned int mw;             /* nominal molecular weight */
		int other_dbs;               /* bit string */
		unsigned char name[NISTMS_MAXNAMELEN];    /* chemical name */
		char formula[NISTMS_MAXFORMLEN]; /* chemical formula */
		char *contributor;           /* only filled if allocated (non NULL) */
		int contributor_len;         /* allocated length of contributor */
		char *synonyms;              /* only filled if allocated (non NULL) */
		int synonyms_len;            /* allocated length of synonyms */
		int num_synonyms;            /* number of synonyms returned */
		int num_rep_locs;            /* input: allocated number of longs in rep_loc */
									 /* output: number of replicate spectra found */
		NISTMS_RECLOC *rep_locs;     /*if non-NULL, replicate spectra locations */
									 /* are put here */
		#if( MSTXTDATA == 1 )            /* Peptide Search, v.2.1 */
			char *references;            /* only filled if allocated */
			int  references_len;         /* allocated length of NIST peptide lib spectrum references */
			int  num_references;         /* number of references returned */
		#endif

		/* NIST 11 or 12 */
		#if ( EXACTMW_CONS == 1 ) /* assuming 32-bit or 64-bit Windows */
			unsigned int exact_mw;     /* f32 format; 0=> missing or has not been read from the library record */
		#endif

		//#if ( PEPSEQ_MODS_IN_SYNONS == 1 && INSTR_TYPE_CONS == 1 )
			unsigned int spec_flags;   /* see NISTMS_SPECTRUM_FLAGS */
		//#endif

		#if ( INSTR_TYPE_CONS == 1 )
			unsigned char instr_type;  /* NISTMS_INSTR_TYPE; 0x1F=NISTMS_INSTR_TYPE_MASK=instr type mask;
										   0x20=NIST_INSTR_TYPE_NOT_IN_LIBREC=no instr. type;  */
		#endif
			signed char charge;        /* ms/ms spectrum precursor charge */
	} NISTMS_AUX_DATA;

	/* information for hit list */
	typedef struct tagNISTMS_HIT_LIST {
		/* SCREEN and SET_OF_FPOS use only following three */
		unsigned int max_spec_locs;  /* allocated length of spec_locs array */
									 /* recommended value = 2,000 */
		NISTMS_RECLOC *spec_locs;    /* allocated by calling pgm, assigned values by DLL */
		unsigned int num_hits_found; /* # spectra found and returned in spec_locs[] */

		int max_hits_desired; /* <= max_spec_locs, largest number of hits returned */
							  /*  in variable length buffers below: sim_num, */
							  /*  rev_sim_num, hit_prob, lib_names, stru_pos */
							  /*  MUST be >= 120 !!! */

		/* for lib search only, each should have space for max_hits_desired */
		int *sim_num;    /* similarity index (forward search), 1000 = perfect match */
		int *rev_sim_num; /* reverse-search similarity index value */

		/* the following two values only have meaning for forward, Identity searches */
		int *hit_prob;    /* probability X 100 that each hit is correct, */
						  /* used only for forward, identity search of NIST library */
		int in_library_prob; /* relative probability X 100 that unknown is in library, */
				   /* only meaningful for forward, identity search of NIST library */

		/* the following are optional for showing names, */
		/* or structures, if NULL or 0 they will be ignored */
		unsigned char *lib_names;     /* buffer to receive series of NULL terminated names */
		unsigned int lib_names_len; /* allocated length of lib_names, INPUT value */
		int max_one_lib_name_len; /* maximum length of a name in lib_names, INPUT */
		NISTMS_RECLOC *stru_pos;  /* file offsets to chemical structure */
		long *casnos;

		#if ( STUDY_PRESEARCH == 1 )
			long lNumSpecCompared, lNumSpecComparedScreenedOut;
		#endif

		#if ( defined(NUM_ADD_SPEC_MATCHFACT) && NUM_ADD_SPEC_MATCHFACT > 0 )
			/* version 2.1.1 */
			float   *pep_Mf[NUM_ADD_SPEC_MATCHFACT]; /* match factors */
			//float   *pfDbgMf[NUM_ADD_SPEC_MATCHFACT]; /* debug match factors */
			/* the following MUST have exactly same sizes as bDbgMf in MF */
			char     pep_hdr_Mf[NUM_ADD_SPEC_MATCHFACT][COLHDRLEN];  /* columns headings; display or not */
			//char     bfDbgMf[NUM_ADD_SPEC_MATCHFACT][COLHDRLEN];  /* columns headings; display or not */
		#endif
	} NISTMS_HIT_LIST;

	/* Used to specify type of automated library search */
	typedef struct tagNISTMS_SRCH_CONTROLS {
		int search_mode;/* 'Q', 'I', 'S', 'L', or 'H' */ /* 2005-12-05 added: 'E', 'F' => peptide searches */
						/* Additional flag: 0x00000100 => remove precursor ion from comparison */
						/* Additional flag: 0x00000200 => fast any peaks type presearch; */
						/* See SEARCH_MODE_FLAGS for all search mode flags */
		int user_mw;    /* for neutral loss searching (used with L, and H) */
		int impure;     /* = 0, uses all peaks in unknown spectrum (forward search) */
						/* !=0,  uses only those peaks in unknown that are also */
						/* in library spectra (reverse search) */
		int min_mass;   /* lowest mass used in comparison; 0=> same as 1;
						   -1 => ignore non-overlapping area:
						   lower mass limit=max(min_mass(libms),min_mass(userms)) */
		int max_mass;   /* max. mass used in comparison; 0=> same as 2000;
						   -1=>no upper mass limit */
		int min_abund;  /* lowest abundance used (base peak = 999) */

		#if( MSTXTDATA == 1 )
			/* Peptide Search, v.2.1 */
			float  precursor_ion_tolerance; /* m/z half-interval, multiplied by 100 */
			float  product_ions_tolerance;  /* m/z half-interval, multiplied by 100 */
			/*long precursor_ion_100mz;*/   /* changed to unsigned 2011-07-20 */
			unsigned precursor_ion_100mz;   /* Precursor_m/z*100 as int, or as f32 without mult. by 100;
											   overrides precursor m/z from NISTMS_MASS_SPECTRUM */
			/* Peptide Search, v.2.1.1 */
			//--- output indicators ---
			char pep_bTF_qry;    // yes/no
			char pep_bE_Omssa;   // yes/no
			char pep_bTF_lib;    // yes/no
			char bRevImpure;     // yes/no  added 2006-10-23; was not used until 2008-05-15
			//--- Weight indicators ----
			char pep_bOmssa;         // yes/no
			char pep_bNumReplicates; // yes/no
			char pep_bQ_TOF;         // yes/no
			char pep_cThreshold;    // 2=low, 1=medium, 0=high; used in all ms/ms searches in ms/ms libraries
			//--- Not used
			int  pep_nCysteineModification;
			/* Peptide Search, v.2.1.5 */
			//--- output indicator ---

			#if( COUNT_REF_PEAKS == 1 )
				char pep_bRefPeakFraction; // yes/no; fraction of matched reference peaks
			#endif
		#endif
	} NISTMS_SRCH_CONTROLS;

	/*
	Displ: sparm->bTF_qry     = cntls->pep_bTF_qry  -> "T/F-qry" -> (float)log10(qry_prob)
	Displ: sparm->bE_Omssa    = cntls->pep_bE_Omssa -> "E-Omssa" -> (float)match_info.omssa_overlap
	Displ: sparm->bTF_lib     = cntls->pep_bTF_lib  -> "T/F-lib" -> (float)log10(lib_prob)
	Displ: sparm->bRevImpure  = cntls->bRevImpure   -> "Rev-Dot" -> (float)(10.* match_info.dot_rev)

	Weight:  sparm->bOmssa          = cntls->pep_bOmssa
	Weight:  sparm->bNumReplicates  = cntls->pep_bNumReplicates
	Weight:  sparm->bQ_TOF          = cntls->pep_bQ_TOF
	Weight:  sparm->cThreshold      = cntls->pep_cThreshold

	*/
	/* user structural data information */
	typedef struct tagNISTMS_USER_STRUCT_INFO {
		int max_structs_desired; /* max number of structures to find, INPUT */
		char *name_filter;       /* substring to search for in struct. names, INPUT */

		int num_structs_found;   /* number of found structures, OUTPUT */

		/* the following are optional for showing names, */
		/* or structures, if NULL or 0 they will be ignored */
		char* struct_names; /* buffer to receive series of NULL-terminated names*/
		int max_one_struct_name_len; /* maximum length of a name in struct_names, INPUT */

		NISTMS_RECLOC *stru_pos;
		//long *stru_pos;        /* file offsets to chemical structures + 1 (in text mode) */
		long *stru_seq_nums;   /* ordering numbers of structures, starts from 1 */

	}NISTMS_USER_STRUCT_INFO;

	/* types of element list */
	#define NISTMS_EXACT 0  /* Elements in hit must be same as elements in */
							/*  el_list */
	#define NISTMS_ELS_IN_LIST 1   /* Each element in hit must appear in el_list */

	 /* mode peak comparison */
	#define NISTMS_REL_PEAKS 0  /* first peak with absolute abundances, */
								/*    others relative to the first */
	#define NISTMS_ABS_PEAKS 1  /* absolute peak abundances */

	#define NISTMS_NUM_CONSTR_EL 10
	#define NISTMS_LEN_CONSTR_EL 2
	#define NISTMS_NUM_CONSTR_PK 10
	#define NISTMS_NAMEFRAG_LEN  40
	#define NISTMS_COMMNT_TAG_LEN 1024
	#define NISTMS_PEPNAME_FRAG_LEN 128

	typedef struct tagNISTMS_CONSTRAINTS {
		unsigned int mw_min; /* minimum MW allowed */
		unsigned int mw_max; /* maximum MW allowed */
		char name_frag[NISTMS_NAMEFRAG_LEN];  /* name fragment  */

		int mode_el_list; /* NISTMS_EXACT or NISTMS_ELS_IN_LIST */
		int num_el_list;  /* number of elements specified */
		char el_list[NISTMS_NUM_CONSTR_EL][NISTMS_LEN_CONSTR_EL]; /* list of 1 or 2 character element symbols */

		int num_atom_comp;  /* number of elements specified for this constraint */
		char comp_list[NISTMS_NUM_CONSTR_EL][NISTMS_LEN_CONSTR_EL]; /* element name */
		char sign[NISTMS_NUM_CONSTR_EL];         /* one of these:  < = > */
		int num_each_el[NISTMS_NUM_CONSTR_EL];   /* number of elememts */

		int mode_peaks;  /* NISTMS_REL_PEAKS or NISTMS_ABS_PEAKS */
		int num_other_peaks; /* number of peaks specified */
		unsigned int abmin[NISTMS_NUM_CONSTR_PK];  /* minimum abundance (% base peak) or rank */
		unsigned int abmax[NISTMS_NUM_CONSTR_PK]; /* maximum abundance (%base peak) or rank */
		unsigned int mass[NISTMS_NUM_CONSTR_PK]; /* mass of peak */
		char peak_type[NISTMS_NUM_CONSTR_PK]; /* type of peak: N, M, L or R */
		int max_misses; /* not used */

		int other_dbs; /* bit string */

		/* dll version 2.1.1 */
		char comment_tags[NISTMS_COMMNT_TAG_LEN];

		#if( MSTXTDATA == 1 )
			char pep_name_frag[NISTMS_PEPNAME_FRAG_LEN];
			int  pep_min_charge;
			int  pep_max_charge;
			int  pep_min_protons;
			int  pep_max_protons;
			int  pep_min_residues;
			int  pep_max_residues;
		#endif

		/* NIST 11 -- v.2.1.5 */
		#if ( EXACTMW_CONS == 1 )
			int num_top_isotopes;      /* added 2011-01-20 DCh */
			unsigned int exact_mw_min; /* f32 floating point */
			unsigned int exact_mw_max; /* f32 floating point */
		#endif

		#if ( INSTR_TYPE_CONS == 1 )
			unsigned int bits_instr_type; /* instrument type bitmap, see NISTMS_BIT_INSTR_TYPE */
		#endif

	} NISTMS_CONSTRAINTS;

	/************************************************************************************/

	#ifndef _DEF_CLBR_STRUCT
		#define _DEF_CLBR_STRUCT
		#define WARNING_NUM   8  /* Must Match SIZE_WARNING value in DCLCLBR.H */
		#define MAX_WARN_STR 70

		typedef struct tagClBrStruct {
			int  nCl;                   /* predicted # Cl atoms  */
			int  nBr;                   /* predicted # Br atoms */
			int  nWarnings;
			char Warnings[WARNING_NUM][MAX_WARN_STR];
			char Error[40];
			int  WarningTypes[WARNING_NUM]; /* contains type of warnings*/

			/* calculated in clbr_prob*/
			int prob;       /* probability that cl and br above are correct */
			int prob_clbr;  /* probability that compound has Cl or Br */
			int any_cl;     /* probability that compound has Cl */
			int any_br;     /* probability that compound has Br */
		} ClBrStruct;

	#endif

	#ifndef INTERP_DEF
		#define INTERP_DEF
		/* typedef struct ReturnStruct ReturnStruct; */
		#define NUM_SUBS  541
		#define NUM_MW_ESTIMATES 5

		typedef struct tagINTERP_MS {
			 ClBrStruct  ClBr;  /* ClBr values */
								/* mw estimates       */
			int mw_est[NUM_MW_ESTIMATES];
			int mw_est_prob[NUM_MW_ESTIMATES];
			int mw_si[NUM_MW_ESTIMATES];
								/* substru info */
			int num_substrus;
			int substru_prob[NUM_SUBS];
			long OffsetInNameFile[NUM_SUBS]; /* Offset in "stru.ou2"  file , where substructure names are*/
		} INTERP_MS;

	#endif

	/*****callback structure *******/
	#ifndef CALLBACK_DEF
		#define CALLBACK_DEF

		typedef enum tagIQ_VERBS {
			WRITE_MSGLINE_,     /* Message is expected in String field of IQ... */
			TEST_CANCEL_,       /*if ( canceled ) ReturnValue == 1 else ReturnValue == 0... */
			SET_CURSOR_BUSY_,   /* display busy cursor, in Incremental Name Search only */
			SET_CURSOR_NORMAL_, /* display normal cursor, in Incremental Name Search only */
			DISPLAY_PROGRESS_,  /* progress only, do not change the message */
		} IQ_VERBS;

		typedef struct tagIQ{
			IQ_VERBS WhatToDo;
			unsigned char String[128];
			long ReturnValue;
		} IQ;

		// IQ::String reserved bytes interpretation for some calls (for internal use)
		#define IQ_LONG( ptrIQ )      ( *(long*) ( (ptrIQ)->String + sizeof( (ptrIQ)->String ) - sizeof( long ) ) )
		#define IQ_PROGRESS( ptrIQ )  ( *(char*) ( (ptrIQ)->String + sizeof( (ptrIQ)->String ) - sizeof( long ) - sizeof( char) ) )

		// NISTMS_IO::callback type definition; meaningful for 16-bit or VB/Pascal apps only
		#ifdef WIN32
			// Win 32 exe and dll
			#define NISTMS_CALLBACK             __cdecl
			#define NISTMS_CALLBACK_PASCAL      __stdcall

		#else
			#if( defined(NISTDLL) || defined( _WINDLL ) )
				// 16-bit dll
				#define NISTMS_CALLBACK         __far
				#define NISTMS_CALLBACK_PASCAL  __far __pascal
			#else
				// 16-bit exe
				#define NISTMS_CALLBACK         __far __saveregs __loadds
				#define NISTMS_CALLBACK_PASCAL  __far __saveregs __loadds __pascal
			#endif

		#endif

	#endif

	/*******************************************************************
	********************************************************************
		 PRINCIPAL ACTION VERBS AND I/O DATA FOR NISTMS_SEARCH()
	********************************************************************
	********************************************************************/

	/* Action "verb" passed with NISTMS_IO to select the type of search desired */

	typedef enum tagNISTMS_SEARCH_TYPE {
		NISTMS_INIT_SRCH,
		NISTMS_CLOSE_SRCH,
		NISTMS_GET_SPECTRUM_SRCH,
		NISTMS_GET_STRUCTURE_SRCH,
		NISTMS_GET_SYNONYMS_SRCH,

		/* get one hit */
		NISTMS_NAME_SRCH,
		NISTMS_CASNO_SRCH,
		NISTMS_ID_SRCH,

		/* ANYPEAKS search, one peak at a time   */
		NISTMS_ANYPEAK_INIT_SRCH, /* initialization */
		NISTMS_ANYPEAK_ONE_PEAK_SRCH,
		NISTMS_ANYPEAK_GET_HITS_SRCH, /* get hit locations */

		/* get set of hits */
		NISTMS_INC_FIRST_NAME_SRCH,
		NISTMS_INC_NEXT_NAME_SRCH,
		NISTMS_INC_PREV_NAME_SRCH,
		NISTMS_INC_GET_NAME_KEY,

		NISTMS_MW_SRCH,
		NISTMS_REP_SRCH, /* not used */
		NISTMS_FORMULA_SRCH,
		NISTMS_SEQ_ID_SRCH,

		/* user spectrum library search  */
		NISTMS_SCREEN_SRCH,
		NISTMS_COMPARE_SPECTRA_SRCH,

		NISTMS_BUILD_HITLIST_SRCH,

		NISTMS_NO_PRE_SRCH,
		/* user library maintenance */
		NISTMS_ADD_TO_LIBRARY_SRCH,
		NISTMS_DELETE_FROM_LIBRARY_SRCH,
		NISTMS_INDEX_LIBRARY_NAMES,
		NISTMS_CREATE_LIBRARY,

		NISTMS_CL_BR_EST,   /* Cl/Br and MW prediction */
		NISTMS_MW_EST,
		NISTMS_SUBSTR_SRCH,
		NISTMS_MW_ESTIMATION_2,

		NISTMS_OPEN_MOLFILE,
		NISTMS_CLOSE_MOLFILE,
		NISTMS_SCAN_USER_STRU_SRCH,
		NISTMS_STRU_SRCH,
		NISTMS_INDEX_USER_STRU,

		NISTMS_STRING_TO_ASCII,
		NISTMS_STRING_TO_GREEK,

		#if( MSTXTDATA == 1 )
			NISTMS_SET_VERSION,       /* set version "2.1", include Peptide search */
			NISTMS_DECODE_MODS,       /* decode pepide modifications read from new binary record */
		#endif

		NISTMS_MAKE_MOLFILE,      /* create a new molfile out of user lib struct or STDATA or add to an existing molfile 2010-01-13 */
		NISTMS_ALT2AROM,          /* transform STDATA according to bits in string_in */
		NISTMS_MARK_LIBS,         /* mark specific libraries with non-space characters, '!', in aux->name[]; string_in contains lib. type number;
									 the position of the non-space character in the string = ordering number of an active library 2010-04-06 */
		/*----  v.2.1.4/5 --------------------*/
		NISTMS_MARK_ALL_LIBS,     /* mark all initiated libraries with non-space characters, '!', in aux->name[]; string_in contains lib. type number;
									 the position of the non-space character in the string = ordering number of an active library 2010-04-06 */
		#if ( EXACTMW == 1 )
			NISTMS_INDEX_LIBRARY_EXACT_MASS,    /* create exact mass index */
			NISTMS_EXACT_MASS_SRCH,         /* search exact mass */
			NISTMS_GET_EXACT_MASS_LIMITS,       /* create exact mass constraint */
			NISTMS_EXACT_MZ_TO_INT_PEAKS, /* fill out int peaks in mass spectrum out of exact m/z peaks */
		#endif

		NISTMS_CASNO_SRCH2,           /* search for CAS r.n. among main CAS r.n. and related CAS r.n. */
		NISTMS_NISTNO_SRCH,
	} NISTMS_SEARCH_TYPE;

	/* NISTMS_SRCH_CONTROLS::search_mode high 8 bits flags */
	typedef enum tagSEARCH_MODE_FLAGS{
		SEARCH_MODE_FLAG_IGNORE_PRECURSOR  = 0x00000100,   /* flag ignore peaks close to precursor m/z */
		SEARCH_MODE_FLAG_FAST_PRESEARCH    = 0x00000200,   /* flag use faster version of any peaks type presearch */
		/* v.2.1.5.1 -- NIST 11 */
		SEARCH_MODE_FLAG_ALT_PEAK_MATCHING = 0x00000400,   /* flag use alt. method for peak matching in ms/ms spectra compare */
		SEARCH_MODE_FLAG_GENERIC_MSMS      = 0x00000800,   /* 2012 flag do not use peak weighting and annotations in ms/ms spectra compare */
		SEARCH_MODE_FLAG_REJECT_OTHER      = 0x00001000,   /* 2012 flag reject peptide lib spectra in Generic and non-peptige in Peptide ms/ms spectra compare */

		#if( PRECUR_MZ_TOL_IN_PPM == 1 )
			SEARCH_MODE_FLAG_PRECUR_MZ_TOL_PPM = 0x00002000,   /* 2012 flag precorsor m/z tolerance is in ppm */
		#endif

		#if( PROD_PEAK_TOL_IN_PPM == 1 )
			SEARCH_MODE_FLAG_PROD_PEAK_TOL_PPM = 0x00004000,   /* 2012 flag product peak m/z tolerance is in ppm */
		#endif

		/* masks */
		SEARCH_MODE_FLAG_MASK              = 0x00FFFF00,   /* flag mask */
		SEARCH_MODE_CHAR_MASK              = 0x000000FF    /* search_mode letter mask */
	} SEARCH_MODE_FLAGS;

	/* Principal I/O structure */
	typedef struct tagNISTMS_IO {
		/* available libraries, used only for initialization */
		unsigned int num_libs;
		char *lib_paths;
		char *lib_types;
		char *work_dir_path;

		/* specifies libraries for searching */
		char *active_libs;

		int  molfile_handle; /* if non-zero than get structures ONLY from
								this previously opened molfile. Used in:
								NISTMS_OPEN_MOLFILE, NISTMS_CLOSE_MOLFILE,
								NISTMS_SCAN_USER_STRU_SRCH, NISTMS_STRU_SRCH,
								NISTMS_ADD_TO_LIBRARY_SRCH.
							 */

		/* input only */
		NISTMS_RECLOC input_spec_loc;
		NISTMS_RECLOCSLACK(1)          /* make sure the next item is 4-byte boundary aligned */
		char *string_in;
		NISTMS_MASS_SPECTRUM *userms;
		NISTMS_SRCH_CONTROLS *cntls;
		NISTMS_CONSTRAINTS *constraints;

		/* output only */
		NISTMS_RECLOC output_spec_loc;
		NISTMS_RECLOCSLACK(2)          /* make sure the next item is 4-byte boundary aligned */
		NISTMS_MASS_SPECTRUM *libms;
		NISTMS_STDATA *stdata;

		/* input and output */
		NISTMS_HIT_LIST *hit_list;
		NISTMS_INC_NAME_INFO *name_info;
		NISTMS_PEAK_INFO *peak_info;
		NISTMS_AUX_DATA *aux_data;
		NISTMS_USER_STRUCT_INFO *user_struct_info;

		void (NISTMS_CALLBACK * callback)( IQ* ); /* message passing; set upon libraries initiation */
		int error_code;                         /* 0 if no error, otherwise see NISTERR.H */
		INTERP_MS  *interp_ms;
	} NISTMS_IO;

	#define NISTMS_MAX_USER_STRUCT_FILES 4 /* max number of simultaneously opened MOL/SDfiles */

	/*----------- exported from the DLL functions prototypes --------------*/

	/* C calling conventions */

	#ifndef WIN32
		#ifdef _WINDLL
			#define NISTMS_C_EXPORT _export
			#define NISTMS_PASCAL_EXPORT _export pascal
		#else
			#define NISTMS_C_EXPORT
			#define NISTMS_PASCAL_EXPORT pascal
		#endif

	#else   /* WIN32 */
		#define NISTMS_C_EXPORT  __cdecl
		#define NISTMS_PASCAL_EXPORT __stdcall

	#endif /* WIN32 */

	/* C calling conventions */

	void NISTMS_C_EXPORT nistms_search( NISTMS_SEARCH_TYPE srch_type, NISTMS_IO *io);
	int  NISTMS_C_EXPORT CreateUserLibrary(char* NISTMSpath, char *libPath);
	long NISTMS_C_EXPORT GetNumberOfEntries(char * pLibPath);
	int  NISTMS_C_EXPORT GetLibraryType(char *pLibPath, int bufferSize);
	/* first time introduced in v2.1.5.1 */
	double NISTMS_C_EXPORT nistms_f32_to_dbl( unsigned f32 );
	unsigned NISTMS_C_EXPORT nistms_dbl_to_f32( double d );
	int NISTMS_C_EXPORT nistms_f32_dec_places( unsigned f32 );

	/* PASCAL calling conventions */
	void NISTMS_PASCAL_EXPORT nistms_search_CLI(NISTMS_SEARCH_TYPE srch_type, NISTMS_IO *io);
	void NISTMS_PASCAL_EXPORT NISTMS_SEARCH(NISTMS_SEARCH_TYPE srch_type, NISTMS_IO *io);
	int  NISTMS_PASCAL_EXPORT CREATEUSERLIBRARY(char* NISTMSpath,char *libPath);
	long NISTMS_PASCAL_EXPORT GETNUMBEROFENTRIES(char * pLibPath);
	int  NISTMS_PASCAL_EXPORT GETLIBRARYTYPE(char *pLibPath, int bufferSize);
	/* for VB programmers, first time introduced in v2.0.0.5 */
	long NISTMS_PASCAL_EXPORT GETCPOINTER(char *ref);
	/* first time introduced in v2.1.5.1 */
	double NISTMS_PASCAL_EXPORT NISTMS_F32_TO_DBL( unsigned f32 );
	unsigned NISTMS_PASCAL_EXPORT NISTMS_DBL_TO_F32( double d );
	int NISTMS_PASCAL_EXPORT NISTMS_F32_DEC_PLACES( unsigned f32 );

	/* f32-specific values */
	#define NISTMS_F32_VALUE_ONE   0x40000000        /* f32(1.0) = min precursor m/z value */
	#define NISTMS_F32_VALUE_075   0x3C000000        /* f32(0.75) = fake precursor m/z value in case of ms1 with accurate peak m/z; should not be used */
	#define NISTMS_PREC_MZ_ONE     100               /* 100*1.0 = min. precursor m/z as int(100*value) */
	#define NISTMS_FAKE_PREC_MZ    75                /* precursor_ion_100mz for in-source spectra */

	#define NISTMS_IS_F32_PEAK_MZ(X) ( (unsigned)(X) >= NISTMS_F32_VALUE_ONE  && (unsigned)(X) != ~0U )
	#define NISTMS_IS_F32_MZ(X)      ( (unsigned)(X) >= NISTMS_F32_VALUE_075  && (unsigned)(X) != ~0U )
	#define NISTMS_PRECUR_MZ_TO_DBL(X) ( NISTMS_IS_F32_MZ(X)? nistms_f32_to_dbl(X) : 0.01*(X) )
	#define NISTMS_IS_PRECURSOR(X)   ( NISTMS_IS_F32_PEAK_MZ(X) || 100 <= (unsigned)(X) && (unsigned)(X) < NISTMS_F32_VALUE_075 )

	#ifdef MSPEPSEARCH
		/* used in MSPepSEarch only */
		#ifndef MAP_LIB_FILE_TYPE_DEFINED
			#define MAP_LIB_FILE_TYPE_DEFINED

			typedef enum tagMapLibFileType {
				MM_PEAKIN_PM0   = 0x00000001,
				MM_PEAKDB_PM0   = 0x00000002,
				MM_MZBIN_INU    = 0x00000004,
				MM_MZBIN_DBU    = 0x00000008,
				MM_MZPRECUB_INU = 0x00000010,
			} MAP_LIB_FILE_TYPE;

		#endif
	#endif


	#ifdef __cplusplus
		}
	#endif


	#if ( _MSC_VER >= 1200 )
		#pragma pack(pop)
	#endif


#endif /* NISTMS_H */
