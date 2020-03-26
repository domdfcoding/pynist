#!/bin/bash
set -e -x

# Compile wheels
PYBINS=(
  "/opt/python/cp36-cp36m/bin"
  "/opt/python/cp37-cp37m/bin"
#  "/opt/python/cp38-cp38m/bin"
  )

for PYBIN in ${PYBINS[@]}; do
    # Upgrade auditwheel to fix borked docker image from 26 Mar 2020
    "${PYBIN}/pip" install auditwheel --upgrade
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/pyms_nist_search*.whl; do
    auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/
done
