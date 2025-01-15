# Makefile to build package sources from poetry
buildroot = /

python_version = 3
python_lookup_name = python$(python_version)
python = $(shell which $(python_lookup_name))
namespace = $(shell dirname */version.py)

version := $(shell \
    test -d '$(namespace)' && $(python) -c \
    'from $(namespace).version import __version__; print(__version__)'\
)

.PHONY: package
package:
	@test -e pyproject.toml || sh -c "echo 'No pyproject.toml found, call this Makefile in a project directory'; exit 1"
	rm -rf dist
	poetry build --format=sdist
	mv dist/*-${version}.tar.gz dist/python-${namespace}.tar.gz
	cat package/python-${namespace}-spec-template | sed -e s'@%%VERSION@${version}@' \
		> dist/python-${namespace}.spec
	cp package/python-${namespace}.changes dist/
