#!/bin/bash
set -e -x

echo "Available Python versions:"
ls /opt/python/
echo ""

PYVERSIONS=(
  "cp36-cp36m"
  "cp37-cp37m"
  "cp38-cp38"
  )

#export VERSION_NO="$TRAVIS_TAG"
export VERSION_NO="0.4.14"

for PYVERSION in "${PYVERSIONS[@]}"; do
    cd /io/
    export PYBIN="/opt/python/${PYVERSION}/bin"

    # Build wheel
    "${PYBIN}/pip" install wheel auditwheel --upgrade
    "${PYBIN}"/python setup.py bdist_wheel -d /wheelhouse
    cd /

    # Bundle external shared libraries into the wheels
    for whl in /wheelhouse/pyms_nist_search-${VERSION_NO}-${PYVERSION}*.whl; do
         "${PYBIN}/python" -m auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/

    done
done
