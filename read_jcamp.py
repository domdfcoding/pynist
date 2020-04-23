# stdlib
import pathlib

# this package
from pyms_nist_search import ReferenceData

file_name = pathlib.Path("/home/domdf/Python/01 GitHub Repos/pynist/tests/test_spectra/71-43-2-Mass.jdx")

print(ReferenceData.from_jcamp(file_name))
