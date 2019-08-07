# lambdalatex/lambdalatex-layer/vendor/Makefile
#
# This is just here to download/update external dependencies.

default: all

all: perl-5.30.0.tar.gz install-tl-unx.tar.gz

perl-5.30.0.tar.gz:
	curl -LO https://www.cpan.org/src/5.0/$@

install-tl-unx.tar.gz:
	curl -LO http://mirror.ctan.org/systems/texlive/tlnet/$@

clean:
	rm -f perl-5.30.0.tar.gz install-tl-unx.tar.gz
