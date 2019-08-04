default: help

.PHONY: build perl texlive

help:
	@echo "Targets:"
	@echo "\tbuild\tBuild the Docker image containing the Perl and TeXLive runtimes."
	@echo "\tperl\tBuild the perl runtime layer."
	@echo "\ttexlive\tBuild the texlive runtime layer."
	@echo "\tclean\tRemove any/all files that can be regenerated."
	@echo "\tclean-downloads\tRemove only the downloadable files."

build: build/perl-5.30.0.tar.gz build/install-tl-unx.tar.gz
	docker build --force-rm -t echen/lambdalatex:latest .

perl:
	docker run --rm -it -v ${PWD}/build:/var/host echen/lambdalatex zip --symlinks -r -9 /var/host/perl.zip /opt/perl

texlive:
	docker run --rm -it -v ${PWD}/build:/var/host echen/lambdalatex zip --symlinks -r -9 /var/host/texlive.zip /opt/texlive

clean: clean-downloads
	rm -f build/perl.zip build/texlive.zip

clean-downloads:
	rm -f build/install-tl-unx.tar.gz build/perl-5.30.0.tar.gz

build/perl-5.30.0.tar.gz:
	cd build && curl -LO https://www.cpan.org/src/5.0/perl-5.30.0.tar.gz

build/install-tl-unx.tar.gz:
	cd build && curl -LO http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
