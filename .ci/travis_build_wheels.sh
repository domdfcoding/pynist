#!/bin/bash
set -e -x

# Compile wheels

PYBINS=(
  "/opt/python/cp36-cp36m/bin"
  "/opt/python/cp37-cp37m/bin"
  "/opt/python/cp38-cp38m/bin"
  )

# and later...
for PYBIN in ${PYBINS[@]}; do
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" --plat $PLAT -w /io/wheelhouse/
done

# Install packages and test
for PYBIN in /opt/python/*/bin/; do
    "${PYBIN}/pip" install python-manylinux-demo --no-index -f /io/wheelhouse
    (cd "$HOME"; "${PYBIN}/nosetests" pymanylinuxdemo)
done