# lambdalatex/lambdalatex-layer/vendor/Makefile
#
# This is just here to download/update external dependencies.

default: all

all: install-tl-unx.tar.gz

install-tl-unx.tar.gz:
	curl -LO http://mirror.ctan.org/systems/texlive/tlnet/$@

clean:
	rm -f install-tl-unx.tar.gz
