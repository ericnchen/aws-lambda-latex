default: help

.PHONY: build


help:
	@echo "Targets:\n"
	@echo "\tbuild\tBuild the Docker image containing the Perl and TeXLive runtimes."
	@echo "\tclean\tRemove any/all files that can be regenerated."
	@echo "\tclean-downloads\tRemove only the downloadable files."
	@echo
	@echo "\tlocaltest\t"



build: build/perl-5.30.0.tar.gz build/install-tl-unx.tar.gz
	docker build --force-rm -t echen/lambdalatex:latest .


layers:
	rm -f build/layers.zip
	docker run --rm -it -v ${PWD}/build:/var/host echen/lambdalatex bash -c "cd /opt; zip --symlinks -r -9 /var/host/layers.zip ."


localtest: layers
	rm -rf build/opt && mkdir build/opt && cd build/opt && unzip ../layers.zip
	rm -rf build/test-input.zip && cd test-input && zip ../build/test-input.zip *
	docker run --rm -v ${PWD}:/var/task -v ${PWD}/build/opt:/opt lambci/lambda:python3.7 localtest.localtest


clean: clean-downloads clean-tests
	rm -f build/layers.zip


clean-downloads:
	rm -f build/install-tl-unx.tar.gz build/perl-5.30.0.tar.gz


clean-tests:
	rm -rf build/test-input.zip build/main.pdf build/opt




build/perl-5.30.0.tar.gz:
	cd build && curl -LO https://www.cpan.org/src/5.0/perl-5.30.0.tar.gz

build/install-tl-unx.tar.gz:
	cd build && curl -LO http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
