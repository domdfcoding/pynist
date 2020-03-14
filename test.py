import pynist
import time
from pyms.Spectrum import MassSpectrum

#peptide = STAVEPLAR (z=2)

FULL_PATH_TO_MAIN_LIBRARY = "C:\\Users\\dom13\\Python\\pynist\\mainlib"
FULL_PATH_TO_WORK_DIR = "C:\\Users\\dom13\\Python\\pynist"

pynist.init_api(FULL_PATH_TO_MAIN_LIBRARY, pynist.NISTMS_MAIN_LIB, FULL_PATH_TO_WORK_DIR)

def pack(spectrum,top=20):
	spectrum.sort(key=lambda s: s[1], reverse=True)
	norm = spectrum[0][1]
	
	spectrum = [(a,999.0*b/norm) for (a,b) in spectrum[:top]]
	spectrum.sort()
	return "*".join(["%.2f\t%.2f" % (a,b) for (a,b) in spectrum]) + "*"

iterations = 1

mz_int_pairs = [
		(27,138),
		(28,210),
		(32,59),
		(37,70),
		(38,273),
		(39,895),
		(40,141),
		(41,82),
		(50,710),
		(51,2151),
		(52,434),
		(53,49),
		(57,41),
		(59,121),
		(61,73),
		(62,229),
		(63,703),
		(64,490),
		(65,1106),
		(66,932),
		(67,68),
		(70,159),
		(71,266),
		(72,297),
		(73,44),
		(74,263),
		(75,233),
		(76,330),
		(77,1636),
		(78,294),
		(84,1732),
		(87,70),
		(88,86),
		(89,311),
		(90,155),
		(91,219),
		(92,160),
		(93,107),
		(101,65),
		(102,111),
		(103,99),
		(104,188),
		(113,107),
		(114,120),
		(115,686),
		(116,150),
		(117,91),
		(126,46),
		(127,137),
		(128,201),
		(129,73),
		(130,69),
		(139,447),
		(140,364),
		(141,584),
		(142,279),
		(143,182),
		(152,37),
		(153,60),
		(154,286),
		(166,718),
		(167,3770),
		(168,6825),
		(169,9999),
		(170,1210),
		(171,85),
		]

mass_list = []
intensity_list = []
for mass, intensity in mz_int_pairs:
	mass_list.append(mass)
	intensity_list.append(intensity)

mass_spec = MassSpectrum(mass_list, intensity_list)

# values = list(zip(mzs,intensities))
values = mz_int_pairs
print()
start_time = time.time()

# for i in range(iterations):
#     print(pack(values, len(values)))
#     x = pynist.dot_product(pack(values), 169.23)
#     print(i, x)

# stop_time = time.time()
#
# print("best score = %d" % (x))
# print("%d dot_products in %.2f seconds" % (iterations, stop_time - start_time))
# print("average time: %.4f seconds" % ((stop_time - start_time) / iterations))


# print(pack(values))
# x = pynist.spectrum_search(pack(values, len(values)))
# print(f"#{x}#")

hit_list = pynist.full_spectrum_search(mass_spec)

print("Hit List")
for idx, hit in enumerate(hit_list):
	print(idx, hit)
	print(hit.spec_loc)
	x = pynist.get_spectrum_by_loc(hit.spec_loc)
	print("\n")
	print(x)
	
	input(">")
#
# print("#####")
#
# print(dir(pynist))
#
# print(pynist.COUNT_REF_PEAKS)