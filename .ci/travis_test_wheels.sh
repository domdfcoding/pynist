#!/bin/bash
set -e -x

PYVERSIONS=(
  "36"
  "37"
  #"38"
  )

export VERSION_NO="0.4.12"

# download docker image
docker pull domdfcoding/pywine-pyms-nist


test_wheel() {
  # First argument is the python version number (36, 37 etc)
  # Second argument is the command to invoke the python interpreter

  $2 -m pip install pytest

  # for diagnostics
  ls wheelhouse

  # Bundle external shared libraries into the wheels
  PYVERSION=$($2)
  define PYVERSION
  for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-cp${PYVERSION}-cp${PYVERSION}m-manylinux*.whl; do

       # Install pyms_nist_search and test
       ${PYTHON} -m pip install "$whl"

       # Move pyms_nist_search directory temporarily so it doesn't interfere with tests
       mv pyms_nist_search pyms_nist_search_tmp

       ${PYTHON} -m pytest tests/

       mv pyms_nist_search_tmp pyms_nist_search

       # TODO: coverage with coverage, pytest-cov and coveralls, then upload to coveralls
  done

}

test_wheel "36" "python3.6.10"
test_wheel "37" "python3.7.6"
# test_wheel "38" "python3.8.2"