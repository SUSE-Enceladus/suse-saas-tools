# Makefile to build package sources from poetry
buildroot = /

python_version = 3
python_lookup_name = python$(python_version)
python = $(shell which $(python_lookup_name))
namespace = $(shell dirname */version.py)
basedir = $(shell basename $(shell pwd))

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
	helper/update_changelog.py --from ../${basedir} \
		--since package/python-${namespace}.changes --utc > \
	dist/python-${namespace}.changes
	helper/update_changelog.py --from ../${basedir} \
		--file package/python-${namespace}.changes --utc >> \
	dist/python-${namespace}.changes
	cat package/python-${namespace}-spec-template | sed -e s'@%%VERSION@${version}@' \
		> dist/python-${namespace}.spec

setup:
	poetry install --all-extras

check: setup
	poetry run flake8 --statistics -j auto --count ${namespace}
	poetry run flake8 --statistics -j auto --count test/unit

test: setup
	poetry run mypy ${namespace}
	poetry run bash -c 'pushd test/unit && pytest -n 5 \
		--doctest-modules --no-cov-on-fail --cov=${namespace} \
		--cov-report=term-missing --cov-fail-under=100 \
		--cov-config .coveragerc'
