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

for PYVERSION in ${PYVERSIONS[@]}; do
    # Upgrade auditwheel to fix borked docker image from 26 Mar 2020
    "/opt/python/${PYVERSION}/bin/pip" install auditwheel --upgrade
    "/opt/python/${PYVERSION}/bin/pip" wheel /io/ -w wheelhouse/

    # for diagnostics
    ls wheelhouse

    # Bundle external shared libraries into the wheels
    for whl in wheelhouse/pyms_nist_search-*-${PYVERSION}*.whl; do
         "/opt/python/${PYVERSION}/bin/python" -m auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/
    done

    # Install pyms_nist_search and pytest
    "${PYBIN}/pip" install pytest
    "${PYBIN}/pip" install wheelhouse/pyms_nist_search-*-${PYVERSION}-manylinux*_x86_64.whl

    # Run pytest
    "${PYBIN}/python" -m pytest
    # TODO: coverage with coverage, pytest-cov and coveralls, then upload to coveralls
done

