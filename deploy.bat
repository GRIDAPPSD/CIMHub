rd /s /q dist
python -m build
twine check dist/* 
twine upload -r testpypi dist/*
rem twine upload dist/*
rem pip install -i https://test.pypi.org/simple/ cimhub==1.0.8
