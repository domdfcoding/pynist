import datetime
from pyms.Spectrum import MassSpectrum  # type: ignore
import pyms_nist_search
import sys

if sys.platform == "win32":
	FULL_PATH_TO_MAIN_LIBRARY = "C:\\Users\\dom13\\Python\\mainlib"
	FULL_PATH_TO_USER_LIBRARY = "C:\\Users\\dom13\\Python\\01 GitHub Repos\\pynist\\tests\\\\MoNA-export-GC-MS_Spectra"
	FULL_PATH_TO_WORK_DIR = "C:\\Users\\dom13\\Python\\00 Projects\\pynist"
else:
	FULL_PATH_TO_MAIN_LIBRARY = "/home/domdf/Python/mainlib"
	FULL_PATH_TO_USER_LIBRARY = "/home/domdf/Python/01 GitHub Repos/pynist/tests/MoNA-export-GC-MS_Spectra"
	FULL_PATH_TO_WORK_DIR = "/home/domdf/Python/00 Projects/pynist"

# search = pyms_nist_search.Engine(
# 		FULL_PATH_TO_MAIN_LIBRARY,
# 		pyms_nist_search.NISTMS_MAIN_LIB,
# 		FULL_PATH_TO_WORK_DIR,
# 		debug=True,
# 		)

search = pyms_nist_search.Engine(
		FULL_PATH_TO_USER_LIBRARY,
		pyms_nist_search.NISTMS_USER_LIB,
		FULL_PATH_TO_WORK_DIR,
		debug=True,
		)

mz_int_pairs = [
		(27, 138),
		(28, 210),
		(32, 59),
		(37, 70),
		(38, 273),
		(39, 895),
		(40, 141),
		(41, 82),
		(50, 710),
		(51, 2151),
		(52, 434),
		(53, 49),
		(57, 41),
		(59, 121),
		(61, 73),
		(62, 229),
		(63, 703),
		(64, 490),
		(65, 1106),
		(66, 932),
		(67, 68),
		(70, 159),
		(71, 266),
		(72, 297),
		(73, 44),
		(74, 263),
		(75, 233),
		(76, 330),
		(77, 1636),
		(78, 294),
		(84, 1732),
		(87, 70),
		(88, 86),
		(89, 311),
		(90, 155),
		(91, 219),
		(92, 160),
		(93, 107),
		(101, 65),
		(102, 111),
		(103, 99),
		(104, 188),
		(113, 107),
		(114, 120),
		(115, 686),
		(116, 150),
		(117, 91),
		(126, 46),
		(127, 137),
		(128, 201),
		(129, 73),
		(130, 69),
		(139, 447),
		(140, 364),
		(141, 584),
		(142, 279),
		(143, 182),
		(152, 37),
		(153, 60),
		(154, 286),
		(166, 718),
		(167, 3770),
		(168, 6825),
		(169, 9999),
		(170, 1210),
		(171, 85),
		]

mass_list = []
intensity_list = []
for mass, intensity in mz_int_pairs:
	mass_list.append(mass)
	intensity_list.append(intensity)

mass_spec = MassSpectrum(mass_list, intensity_list)

start_time = datetime.datetime.now()
print("Performing Full Search")

hit_list = search.full_search_with_ref_data(mass_spec)

for hit_no, (hit, ref_data) in enumerate(hit_list):
	print(f"Hit {hit_no}")
	print(hit)
	print(ref_data)
	print(ref_data.mass_spec)
	print()

	# reference_data = search.get_r#eference_data(hit.spec_loc)
	# print(reference_data.mass_spec == ref_data.mass_spec)
	# print(reference_data == ref_data)

print(f"Completed Full Search in {(datetime.datetime.now() - start_time).total_seconds()}")

############

start_time = datetime.datetime.now()
print("Performing Quick Search")

hit_list = search.spectrum_search(mass_spec, n_hits=10)

for hit_no, hit in enumerate(hit_list):
	print(f"Hit {hit_no}")
	print(hit)
	print()

print(f"Completed Quick Search in {(datetime.datetime.now() - start_time).total_seconds()}")
