#!/bin/bash
set -e -x

PYVERSIONS=(
  "36"
  "37"
  #"38"
  )

export VERSION_NO="0.4.13"

# download docker image
docker pull domdfcoding/pywine-pyms-nist

# Test tox with source package
pyenv global 3.6
python -m pip install tox
python -m tox

test_wheel() {
  # First argument is the python version number (36, 37 etc)
  # Second argument is the command to invoke the python interpreter

  # Tell Pyenv which python version to use
  PY_DOT=$(echo "$1" | sed 's/.\{1\}/&./g;s/.$//')
  pyenv global "${PY_DOT}"

  python --version
  which python

  python -m pip install pip --upgrade
  python -m pip install setuptools wheel --upgrade
  python -m pip install -r tests/requirements.txt

  for whl in wheelhouse/pyms_nist_search-${VERSION_NO}-cp$1-cp$1m-manylinux*.whl; do
    # Cleanup to prevent interference with tests
    rm -rf pyms_nist_search
    sudo rm -rf pyms_nist_search.egg-info  # Was getting "permission denied" without sudo

    # Install pyms_nist_search and run tests
#    python -m pip install pyms_nist_search --find-links wheelhouse/
#    python -m pip install "$whl" --upgrade

    # Test tox with wheels
    python -m tox -r -e py$1 --installpkg "$whl"

    python -m pytest --cov=pyms_nist_search tests/

  # TODO: Upload coverage to coveralls
  done
}

for PYVERSION in "${PYVERSIONS[@]}"; do
  test_wheel $PYVERSION
#test_wheel "37" "3.7"
# test_wheel "38" "3.8"
done
