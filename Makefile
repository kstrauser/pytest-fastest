.PHONY: build

build:
	python setup.py bdist_wheel

upload:
	twine upload dist/pytest_fastest-$(shell cat VERSION)-py3-none-any.whl