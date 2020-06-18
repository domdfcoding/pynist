# stdlib
import pathlib

# 3rd party
import requests

# this package
from pyms_nist_search import ReferenceData
# from pyms.Spectrum import MassSpectrum

#
# mz_int_pairs = [
# 		(27, 138),	(28, 210),	(32, 59),	(37, 70),	(38, 273),
# 		(39, 895),	(40, 141),	(41, 82),	(50, 710),	(51, 2151),
# 		(52, 434),	(53, 49),	(57, 41),	(59, 121),	(61, 73),
# 		(62, 229),	(63, 703),	(64, 490),	(65, 1106), (66, 932),
# 		(67, 68),	(70, 159),	(71, 266),	(72, 297),	(73, 44),
# 		(74, 263),	(75, 233),	(76, 330),	(77, 1636),	(78, 294),
# 		(84, 1732),	(87, 70),	(88, 86),	(89, 311),	(90, 155),
# 		(91, 219),	(92, 160),	(93, 107),	(101, 65),	(102, 111),
# 		(103, 99),	(104, 188),	(113, 107),	(114, 120),	(115, 686),
# 		(116, 150),	(117, 91),	(126, 46),	(127, 137),	(128, 201),
# 		(129, 73),	(130, 69),	(139, 447),	(140, 364),	(141, 584),
# 		(142, 279),	(143, 182),	(152, 37),	(153, 60),	(154, 286),
# 		(166, 718),
# 		(167, 3770),
# 		(168, 6825),
# 		(169, 9999),
# 		(170, 1210),
# 		(171, 85),
# 		]
#
#
# def make_ms_from_pairs(pairs):
# 	mass_list = []
# 	intensity_list = []
# 	for mass, intensity in pairs:
# 		mass_list.append(mass)
# 		intensity_list.append(intensity)
#
# 	return MassSpectrum(mass_list, intensity_list)

spectra = {
		# "Diphenylamine": make_ms_from_pairs(mz_int_pairs)
}

# Download required files from NIST Webbook
nist_data_dir = pathlib.Path("nist_jdx_files")

if not nist_data_dir.exists():
	nist_data_dir.mkdir(parents=True)

# Compounds from nist
for cas in [
		"122-39-4",
		"71-43-2",
		"107-10-8",
		# "50-37-3",  # LSD, shows up under synonym
		"57-13-6",
		# "77-92-9", citric acid, shows up as diisopropyl malonate
		# "118-96-7", tnt, being detected as n-sec-butyl-2,4-dinitrobenzenamine
		# "67-66-3",  # Chloroform, detected as trichloromethane (synonym)
		# "‎106-24-1",  # Geraniol, being detected as 3,7-dimethyl-2,6-octadien-1-ol(trans)
		# "121-14-2",  # 2,4-DNT	need to fix synonyms
		"507-70-0",  # Borneol
		"78-93-3",  # MEK
		]:

	jcamp_file = nist_data_dir / f"{cas}.jdx"

	if not jcamp_file.exists():
		r = requests.get(f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C{cas.replace('-', '')}&Index=0&Type=Mass")
		jcamp_file.write_bytes(r.content)

	# Read ReferenceData from Jcamp File
	ref_data = ReferenceData.from_jcamp(jcamp_file)

	# Fix for borneol
	if ref_data.cas == "507-70-0":
		spectra["Borneol"] = ref_data.mass_spec
	else:
		spectra[ref_data.name] = ref_data.mass_spec
	# spectra[ref_data.cas] = ref_data.mass_spec

	# TODO: test jdx files from other sources
	pass
