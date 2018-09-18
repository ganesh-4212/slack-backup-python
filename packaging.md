TO dicrectly edit and install
pip install --editable slack-backup-python

to create dist 
 python setup.py sdist bdist_wheel

 to upload to test indext
  twine upload --repository-url https://test.pypi.org/legacy/ dist/*