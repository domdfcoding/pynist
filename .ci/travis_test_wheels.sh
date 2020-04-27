#!/bin/bash
set -e -x

PYVERSIONS=(
  "36"
  "37"
  #"38"
  )

export VERSION_NO="0.4.12"

for PYVERSION in ${PYVERSIONS[@]}; do

    PY_DOT=$(echo "${PYVERSION}" | sed 's/.\{1\}/&./g;s/.$//')
    declare PY_DOT
    export PYTHON="python${PY_DOT}"

    ${PYTHON} -m pip install pytest

    # for diagnostics
    ls wheelhouse

    # Bundle external shared libraries into the wheels
    for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-cp${VERSION_NO}-cp${PYVERSION}m-manylinux*.whl; do

         # Install pyms_nist_search and test
         ${PYTHON} -m pip install "$whl"

         ls /io

         # Move pyms_nist_search directory temporarily so it doesn't interfere with tests
         mv /io/pyms_nist_search /io/pyms_nist_search_tmp

         "${PYTHON}/python" -m pytest /io/tests/

         mv /io/pyms_nist_search_tmp /io/pyms_nist_search

         # TODO: coverage with coverage, pytest-cov and coveralls, then upload to coveralls
    done

done

