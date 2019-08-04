default: help

.PHONY: build perl texlive


help:
	@echo "Targets:\n"
	@echo "\tbuild\tBuild the Docker image containing the Perl and TeXLive runtimes."
	@echo "\tclean\tRemove any/all files that can be regenerated."
	@echo "\tclean-downloads\tRemove only the downloadable files."
	@echo
	@echo "\tlocaltest\t"



build: build/perl-5.30.0.tar.gz build/install-tl-unx.tar.gz
	docker build --force-rm -t echen/lambdalatex:latest .


localtest: build/test-payload.zip build/perl.zip build/texlive.zip build/symlinks.zip
	rm -rf build/opt
	cd build && unzip perl.zip && unzip texlive.zip && unzip symlinks.zip
	docker run --rm -v ${PWD}:/var/task -v ${PWD}/build/opt:/opt lambci/lambda:python3.7 localtest.localtest


clean: clean-downloads
	rm -f build/perl.zip build/texlive.zip build/symlinks.zip


clean-downloads:
	rm -f build/install-tl-unx.tar.gz build/perl-5.30.0.tar.gz




build/perl-5.30.0.tar.gz:
	cd build && curl -LO https://www.cpan.org/src/5.0/perl-5.30.0.tar.gz

build/install-tl-unx.tar.gz:
	cd build && curl -LO http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz

build/test-payload.zip:
	zip build/test-payload.zip test_input.tex

build/perl.zip:
	docker run --rm -it -v ${PWD}/build:/var/host echen/lambdalatex zip --symlinks -r -9 /var/host/perl.zip /opt/perl

build/texlive.zip:
	docker run --rm -it -v ${PWD}/build:/var/host echen/lambdalatex zip --symlinks -r -9 /var/host/texlive.zip /opt/texlive

build/symlinks.zip:
	docker run --rm -it -v ${PWD}/build:/var/host echen/lambdalatex zip --symlinks -r -9 /var/host/symlinks.zip /opt/bin /opt/lib
