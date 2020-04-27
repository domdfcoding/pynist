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

  pyenv global "$3"

  $2 --version
  which python
  $2 -m pip install pytest

  # for diagnostics
  ls wheelhouse

  # Bundle external shared libraries into the wheels
  for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-cp$1-cp$1m-manylinux*.whl; do

       # Install pyms_nist_search and test
       $2 -m pip install "$whl"

       # Move pyms_nist_search directory temporarily so it doesn't interfere with tests
       mv pyms_nist_search pyms_nist_search_tmp

       $2 -m pytest tests/

       mv pyms_nist_search_tmp pyms_nist_search

       # TODO: coverage with coverage, pytest-cov and coveralls, then upload to coveralls
  done

}

test_wheel "36" "python3.6", "3.6"
test_wheel "37" "python3.7", "3.7"
# test_wheel "38" "python3.8.2"