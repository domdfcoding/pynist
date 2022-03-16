# 3rd party
import pytest

# this package
from pyms_nist_search import utils


# yapf: disable
def test_parse_name_chars():
	test_strings = {
		"Hello World!": [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 33, 0],
		"The quick brown fox jumps over a lazy dog.": [
		84, 104, 101, 32, 113, 117, 105, 99, 107, 32, 98, 114,  # noqa: E122
		111, 119, 110, 32, 102, 111, 120, 32, 106, 117, 109, 112,  # noqa: E122
		115, 32, 111, 118, 101, 114, 32, 97, 32, 108, 97, 122, 121,  # noqa: E122
		32, 100, 111, 103, 46, 0],  # noqa: E122
		"Pack my box with five dozen liquor jugs": [
		80, 97, 99, 107, 32, 109, 121, 32, 98, 111, 120, 32, 119, 105,  # noqa: E122
		116, 104, 32, 102, 105, 118, 101, 32, 100, 111, 122, 101, 110,  # noqa: E122
		32, 108, 105, 113, 117, 111, 114, 32, 106, 117, 103, 115, 0],  # noqa: E122
		"Mr. Jock, TV quiz PhD, bags few lynx": [
		77, 114, 46, 32, 74, 111, 99, 107, 44, 32, 84, 86, 32, 113,  # noqa: E122
		117, 105, 122, 32, 80, 104, 68, 44, 32, 98, 97, 103, 115, 32,  # noqa: E122
		102, 101, 119, 32, 108, 121, 110, 120, 0],  # noqa: E122
		"α-Zearalenol": [224, 45, 90, 101, 97, 114, 97, 108, 101, 110, 111, 108, 0],
		"β-Carotene": [225, 45, 67, 97, 114, 111, 116, 101, 110, 101, 0],
		"γ-Butyrolactone": [231, 45, 66, 117, 116, 121, 114, 111, 108, 97, 99, 116, 111, 110, 101, 0],
		"δ-Tocopherol": [235, 45, 84, 111, 99, 111, 112, 104, 101, 114, 111, 108, 0],
		}
	# yapf: enable

	for ascii, codes in test_strings.items():  # noqa: A001  # pylint: disable=redefined-builtin
		assert utils.parse_name_chars(codes) == ascii

	# Extra 0s at end:
	for i in range(5):
		for ascii, codes in test_strings.items():  # noqa: A001  # pylint: disable=redefined-builtin
			assert utils.parse_name_chars(codes + ([0] * i)) == ascii

	# Test remaining special characters

	assert utils.parse_name_chars([238, 0]) == 'ε'
	assert utils.parse_name_chars([227, 0]) == 'π'
	assert utils.parse_name_chars([229, 0]) == 'σ'
	assert utils.parse_name_chars([230, 0]) == 'μ'
	assert utils.parse_name_chars([234, 0]) == 'ω'
	assert utils.parse_name_chars([241, 0]) == '±'
	assert utils.parse_name_chars([252, 0]) == 'η'

	# Test unrecognised characters
	for i in range(-31, 0):
		with pytest.warns(UserWarning):
			assert utils.parse_name_chars([i, 0]) == '�'

	# Test secret message
	assert utils.parse_name_chars([
			78,
			111,
			116,
			104,
			105,
			110,
			103,
			32,
			84,
			111,
			32,
			83,
			101,
			101,
			32,
			72,
			101,
			114,
			101,
			0,
			65,
			108,
			97,
			110,
			32,
			84,
			117,
			114,
			105,
			110,
			103,
			0
			]) == "Nothing To See Here"

	# Errors
	with pytest.raises(TypeError):
		utils.parse_name_chars(['a', 'b', 'c'])  # type: ignore
