default: help

.PHONY: build

help:
	@echo "Targets:"
	@echo "\tbuild\tBuild the Docker image containing the Perl and TeXLive runtimes."
	@echo "\truntime\tCompress the built runtime artifacts into a zip file for AWS."
	@echo "\tclean\tRemove any/all files that can be regenerated."

build: build/perl-5.30.0.tar.gz build/install-tl-unx.tar.gz
	docker build --force-rm -t echen/lambdalatex:latest .

runtime: build/lambdalatex-runtime.zip

clean:
	rm -f build/install-tl-unx.tar.gz
	rm -f build/lambdalatex-runtime.zip
	rm -f build/perl-5.30.0.tar.gz

build/perl-5.30.0.tar.gz:
	cd build && curl -LO https://www.cpan.org/src/5.0/perl-5.30.0.tar.gz

build/install-tl-unx.tar.gz:
	cd build && curl -LO http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz

build/lambdalatex-runtime.zip:
	docker run --rm -it -v ${PWD}/build:/var/host echen/lambdalatex zip --symlinks -r -9 /var/host/lambdalatex-runtime.zip /opt
