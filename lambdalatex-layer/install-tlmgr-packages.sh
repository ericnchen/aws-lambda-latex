#!/usr/bin/env bash

# /opt/bin and /opt/lib are appended last but need to be first else wrong perl is used.
export PATH=/opt/bin:$PATH
export LD_LIBRARY_PATH=/opt/lib:$LD_LIBRARY_PATH

# Install packages as needed.
tlmgr install latexmk beamer etoolbox translator pgf microtype lm

# Additional symlinks need to be manually created.
ln -s /opt/texlive/2019/bin/x86_64-linux/latexmk /opt/bin/latexmk

#RUN tlmgr install \
#            xcolor \
##            tcolorbox \
##            environ \
##            trimspaces \
#            booktabs \
##            lastpage \
##            pgfplots \
##            marginnote \
##            tabu \
##            varwidth \
##            makecell \
##            enumitem \
##            setspace \
##            xwatermark \
##            catoptions \
##            ltxkeys \
#            framed \
##            parskip \
##            endnotes \
##            footmisc \
##            zapfding \
##            symbol \
##            sectsty \
##            stringstrings \
##            koma-script \
##            multirow \
##            calculator \
##            adjustbox \
#            xkeyval \
##            collectbox \
##            siunitx \
##            l3kernel \
##            l3packages \
##            helvetic \
##            charter \
#            memoir \
#            ifetex \
#            layouts \
#            glossaries \
#            mfirstuc \
#            textcase \
#            xfor \
#            datatool \
#            substr \
#            fp \
#            fancyvrb \
#            tabulary \
#            ec \
#            listings \
#            ulem \
#            soul \
#            xargs \
#            todonotes \
#            patchcmd \
#            acronym \
#            bigfoot \
#            xstring \
#            subfigure \
#            && \
##    tlmgr remove --force luatex && \
#    rm -f /opt/texlive/2019/tlpkg/texlive.tlpdb* && \
#    rm -f /opt/texlive/2019/tlpkg/translations/*.po
##           /opt/texlive/2019/texmf-dist/source/latex/koma-script/doc \
##           /opt/texlive/2019/texmf-dist/doc
