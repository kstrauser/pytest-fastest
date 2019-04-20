.PHONY: build

build:
	poetry build

upload:
	twine upload dist/pytest_fastest-$(shell cat VERSION)-py3-none-any.whl
