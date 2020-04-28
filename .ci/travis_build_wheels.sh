#!/bin/bash
set -e -x

PYVERSIONS=(
  "cp36-cp36m"
  "cp37-cp37m"
  "cp38-cp38m"
  )

export VERSION_NO="0.4.13"

for PYVERSION in "${PYVERSIONS[@]}"; do

    export PYBIN="/opt/python/${PYVERSION}/bin"

    # Upgrade auditwheel to fix borked docker image from 26 Mar 2020
    "${PYBIN}/pip" install auditwheel --upgrade
#    "${PYBIN}/pip" wheel /io/ -w /wheelhouse/

    # Build wheel
    cd /io/
    "${PYBIN}"/python setup.py bdist_wheel -d /wheelhouse
    cd /

    # Bundle external shared libraries into the wheels
    for whl in /wheelhouse/pyms_nist_search-${VERSION_NO}-${PYVERSION}*.whl; do
         "${PYBIN}/python" -m auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/

    done

done

