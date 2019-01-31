#
# Makefile
# AuroreMariscal, 2019-01-17 14:03
#
#!/usr/bin/make
#
build:
	virtualenv-2.7 .
	bin/pip install -I -r requirements.txt
	bin/buildout
