APP = pyfco

.PHONY: default test isort

default: test

test:
	tox

isort:
	isort --recursive ${APP}
