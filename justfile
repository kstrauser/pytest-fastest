test:
	tox

build:
	poetry build

upload:
	twine upload --repository pytest-fastest dist/pytest_fastest-`cat VERSION`-py3-none-any.whl
