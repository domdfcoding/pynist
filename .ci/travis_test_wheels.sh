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

  # Tell Pyenv which python version to use
  PY_DOT=$(echo "$1" | sed 's/.\{1\}/&./g;s/.$//')
  define PY_DOT
  pyenv global PY_DOT

  python --version
  which python
  python -m pip install pytest

  # for diagnostics
  ls wheelhouse

  # Bundle external shared libraries into the wheels
  for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-cp$1-cp$1m-manylinux*.whl; do

       # Install pyms_nist_search and test
       python -m pip install "$whl"

       # Move pyms_nist_search directory temporarily so it doesn't interfere with tests
       mv pyms_nist_search pyms_nist_search_tmp

       python -m pytest tests/

       mv pyms_nist_search_tmp pyms_nist_search

       # TODO: coverage with coverage, pytest-cov and coveralls, then upload to coveralls
  done

}

test_wheel "36" "3.6"
test_wheel "37" "3.7"
# test_wheel "38" "3.8"