import datetime
start_time = datetime.datetime.now()

from pyms.Spectrum import MassSpectrum
import requests
from pynist.utils import quote_mass_spec
from pynist.utils import PyNISTEncoder
from pynist.search_result import SearchResult
from pynist.reference_data import ReferenceData
import json

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
print(quote_mass_spec(mass_spec))


def hit_list_from_json(json_data):
	raw_output = json.loads(json_data)
	
	hit_list = []
	
	for hit in raw_output:
		hit_list.append(SearchResult(**hit))
	
	return hit_list


def hit_list_with_ref_data_from_json(json_data):
	raw_output = json.loads(json_data)
	
	hit_list = []
	
	for hit, ref_data in raw_output:
		hit_list.append((SearchResult(**hit), ReferenceData(**ref_data)))
	
	return hit_list




# res = requests.post(f"http://localhost:5001/search/spectrum/", json=json.dumps(mass_spec, cls=PyNISTEncoder))
# hit_list = hit_list_from_json(res.text)
res = requests.post(f"http://localhost:5001/search/spectrum_with_ref_data/", json=json.dumps(mass_spec, cls=PyNISTEncoder))
hit_list = hit_list_with_ref_data_from_json(res.text)

print(res)
print(res.text)
print(hit_list)


# print("Hit List")
# for idx, hit in enumerate(hit_list):
# 	print(idx, hit)
# 	print(hit.spec_loc)
# 	print(type(hit.spec_loc))
#
# 	res = requests.post(f"http://localhost:5001/search/loc/{hit.spec_loc}")
# 	print(res)
# 	print(res.text)

print(f"Completed in {(datetime.datetime.now() - start_time).total_seconds()}")