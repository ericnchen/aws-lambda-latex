default: help

help:


all: download build zip
	julia make.jl

#%:
#	julia make.jl $@

# Won't download if already exist.
install-tl-unx.tar.gz:
	curl -LO http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz

latexlambda.zip:
	docker run --rm -it -v ${PWD}:/var/host octech/lambdalatex zip --symlinks -r -9 /var/host/latexlambda.zip .

# Download TeXLive installer.
download: install-tl-unx.tar.gz

# Build docker image from Dockerfile.
build:
	docker build -t octech/lambdalatex .

# Create Lambda deployment .ZIP file from docker image.
zip: latexlambda.zip

clean:
	rm -f install-tl-unx.tar.gz latexlambda.zip
