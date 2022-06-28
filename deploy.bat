rem rd /s /q dist
rem python -m build
rem twine check dist/* 
rem twine upload -r testpypi dist/*
twine upload dist/*
rem pip install -i https://test.pypi.org/simple/ cimhub==1.0.5
