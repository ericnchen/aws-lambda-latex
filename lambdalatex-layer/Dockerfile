FROM lambci/lambda:build-python3.7

# TeXLive doesn't *need* wget, but without it seems like network errors happen too much.
RUN yum -y install wget perl-Digest-MD5 && \
    yum -y clean all && \
    rm -rf /var/cache/yum

# Install TeXLive. The bin directory is symlinked to /opt/bin with the provided profile.
WORKDIR /tmp
ADD vendor/install-tl-unx.tar.gz .
COPY texlive.profile .
RUN cd install-tl-* && \
    ./install-tl --profile ../texlive.profile

# Install/remove TeXLive packages as needed.
WORKDIR /tmp
COPY install-tlmgr-packages.sh .
RUN bash install-tlmgr-packages.sh

# Add the multimarkdown6 include files.
# See: https://github.com/fletcher/MultiMarkdown-6/tree/develop/texmf/tex/latex/mmd6
#COPY vendor/multimarkdown6-latex-includes /opt/texlive/texmf-local/tex/latex/local/mmd/
#RUN texhash
