#!/bin/bash
set -e -x

PYVERSIONS=(
  "36"
  "37"
  "38"
  )

export VERSION_NO="0.4.13"

#pyenv install -v 3.8

# Test tox with source package
pyenv global 3.6
python -m pip install tox
sudo rm -rf pyms_nist_search.egg-info
python -m tox

test_wheel() {
  # First and only argument is the python version number (36, 37 etc)

  # Tell Pyenv which python version to use
  PY_DOT=$(echo "$1" | sed 's/.\{1\}/&./g;s/.$//')
  pyenv global "${PY_DOT}"

  python --version
  which python

  python -m pip install pip --upgrade
  python -m pip install wheel
  python -m pip install tox

  # Cleanup to prevent interference with tests
  rm -rf pyms_nist_search
  sudo rm -rf pyms_nist_search.egg-info  # Was getting "permission denied" without sudo

  for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-cp$1-cp$1*-manylinux*.whl; do

    # Test tox with wheels
    python -m tox -r -e py$1-linux --installpkg "$whl"

  # TODO: Upload coverage to coveralls
  done
}


for PYVERSION in "${PYVERSIONS[@]}"; do
  test_wheel $PYVERSION
done
