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

for PYVERSION in ${PYVERSIONS[@]}; do

    PY_DOT=$(echo "${PYVERSION}" | sed 's/.\{1\}/&./g;s/.$//')
    declare PY_DOT
    export PYTHON="/usr/bin/python${PY_DOT}"

    ${PYTHON} -m pip install pytest

    # for diagnostics
    ls wheelhouse

    # Bundle external shared libraries into the wheels
    for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-cp${PYVERSION}-cp${PYVERSION}m-manylinux*.whl; do

         # Install pyms_nist_search and test
         ${PYTHON} -m pip install "$whl"


         # Move pyms_nist_search directory temporarily so it doesn't interfere with tests
         mv pyms_nist_search pyms_nist_search_tmp

         ${PYTHON} -m pytest tests/

         mv pyms_nist_search_tmp pyms_nist_search

         # TODO: coverage with coverage, pytest-cov and coveralls, then upload to coveralls
    done

done

