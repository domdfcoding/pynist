#!/bin/bash
set -e -x

# Remove the pyms_nist_search directory to it doesn't interfere with tests
rm -rf pyms_nist_search

# Compile wheels
PYVERSIONS=(
  "cp36-cp36m"
  "cp37-cp37m"
  #"cp38-cp38m"
  )

export VERSION_NO="0.4.11"

for PYVERSION in ${PYVERSIONS[@]}; do

    export PYBIN="/opt/python/${PYVERSION}/bin"

    # Upgrade auditwheel to fix borked docker image from 26 Mar 2020
    "${PYBIN}/pip" install auditwheel --upgrade
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
    "${PYBIN}/pip" install pytest

    # for diagnostics
    ls wheelhouse

    # Bundle external shared libraries into the wheels
    for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-${PYVERSION}*.whl; do
         "${PYBIN}/python" -m auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/

         # Install pyms_nist_search and test
         "${PYBIN}/pip" install "$whl"
         "${PYBIN}/python" -m pytest
         # TODO: coverage with coverage, pytest-cov and coveralls, then upload to coveralls
    done

done

