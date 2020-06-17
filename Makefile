MAKE=make

install_python:
	@(echo "** Installing dependencies **\n")
	(sudo apt install -y python3.7 python3.7-dev python3-pip jq)

install_pip:
	$(MAKE) install_python
	(python3 -m pip install -r requirements.txt)
	@(echo "** Dependencies successfully installed**\n")

install_conda:
	$(MAKE) install_python
	(conda env create -f environment.yml)
	@(echo "** Dependencies successfully installed**\n")

check:
	@(echo "** Running UnitTests **\n")
	(python3 -m unittest discover test)
	@(echo "** Running integration tests **\n")
	@(cd test; ./run_integration_tests.sh)

makecheckfiles:
	@(cd test; ./make_checkfiles.sh)
