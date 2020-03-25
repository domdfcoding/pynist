echo "Deploying to PyPI..."
pip3 install twine
twine upload  -u DomDF -p ${pypi_password} --skip-existing *.whl
