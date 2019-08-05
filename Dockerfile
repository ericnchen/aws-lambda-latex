FROM lambci/lambda:build

# Add externally downloaded files to compile inside the container.
WORKDIR /var/src
ADD build/perl-5.30.0.tar.gz .
ADD build/install-tl-unx.tar.gz .

# Build Perl because Amazon Linux instances no longer include it.
RUN cd perl-5.* && \
    ./Configure -des -Dprefix=/opt/perl && \
    make install && \
    make clean && \
    rm -r /opt/perl/man

# Install prerequisites for TeXLive (installer uses wget, not curl).
RUN yum -y install wget && \
    yum clean all && \
    rm -rf /var/cache/yum

# Install TeXLive (using our self-built Perl).
COPY texlive.profile .
RUN cd install-tl-* && \
    /opt/perl/bin/perl install-tl --profile ../texlive.profile

# Update PATH.
ENV PATH=/opt/perl/bin:/opt/texlive/2019/bin/x86_64-linux:$PATH

# Install/remove TeXLive packages (check to make sure I need/want all of these).
RUN tlmgr install \
            latexmk \
#            xcolor \
#            tcolorbox \
#            pgf \
#            environ \
#            trimspaces \
#            etoolbox \
#            booktabs \
#            lastpage \
#            pgfplots \
#            marginnote \
#            tabu \
#            varwidth \
#            makecell \
#            enumitem \
#            setspace \
#            xwatermark \
#            catoptions \
#            ltxkeys \
#            framed \
#            parskip \
#            endnotes \
#            footmisc \
#            zapfding \
#            symbol \
#            lm \
#            sectsty \
#            stringstrings \
#            koma-script \
#            multirow \
#            calculator \
#            adjustbox \
#            xkeyval \
#            collectbox \
#            siunitx \
#            l3kernel \
#            l3packages \
#            helvetic \
#            charter \
            && \
#    tlmgr remove --force luatex && \
    rm -f /opt/texlive/2019/tlpkg/texlive.tlpdb* && \
    rm -f /opt/texlive/2019/tlpkg/translations/*.po
#           /opt/texlive/2019/texmf-dist/source/latex/koma-script/doc \
#           /opt/texlive/2019/texmf-dist/doc

# Make symlinks to /opt/bin and /opt/lib since that's where Lambda expects it.
RUN mkdir /opt/bin /opt/lib && \
    cd /opt/bin && \
    ln -s ../perl/bin/* . && \
    cd /opt/lib && \
    ln -s ../perl/lib/* . && \
    cd /opt/bin && \
    ln -s ../texlive/2019/bin/x86_64-linux/* .
