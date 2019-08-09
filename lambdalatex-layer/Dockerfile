FROM lambci/lambda:build-python3.7

# Build and install our own perl since AWS Lambda no longer provides it.
WORKDIR /tmp
ADD vendor/perl-5.30.0.tar.gz .
RUN cd perl-5.* && \
    ./Configure -des -Dman1dir=none -Dman3dir=none -Dprefix=/opt && \
    make install && \
    make clean

# TeXLive doesn't *need* wget, but without it seems like network errors happen too much.
RUN yum -y install wget && \
    yum -y clean all && \
    rm -rf /var/cache/yum

# Install TeXLive. The bin directory is symlinked to /opt/bin with the provided profile.
WORKDIR /tmp
ADD vendor/install-tl-unx.tar.gz .
COPY texlive.profile .
RUN cd install-tl-* && \
    /opt/bin/perl install-tl --profile ../texlive.profile

# Install/remove TeXLive packages as needed.
WORKDIR /tmp
COPY install-tlmgr-packages.sh .
RUN bash install-tlmgr-packages.sh

# Add the multimarkdown6 include files.
# See: https://github.com/fletcher/MultiMarkdown-6/tree/develop/texmf/tex/latex/mmd6
#COPY vendor/multimarkdown6-latex-includes /opt/texlive/texmf-local/tex/latex/local/mmd/
#RUN texhash
