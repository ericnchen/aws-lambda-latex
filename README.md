# TeX Live for AWS Lambda

This project uses the [Serverless Framework](https://serverless.com) to easily provision, deploy, and manage a service stack on AWS Lambda that provides a REST API which can accept a zip file, encoded as a Base64 string, containing a `main.tex` document and optionally all of its supporting files (images, references, etc), and returns a pdf document also encoded as a Base64 string.

## Background

LaTeX is an indispensable tool that can be used to create, among other things, publication grade documents, posters, and presentations.
Compiling a LaTeX document requires a toolchain such as [TeX Live](https://www.tug.org/texlive), which unfortunately isn't available on platforms such as iOS.
Web services like [Overleaf](https://www.overleaf.com) exist which can be used on iOS, but to the best of my knowledge doesn't expose an API that can be called with files not uploaded to Overleaf.

## The AWS Lambda Layer

Documents are compiled with `latexmk` installed through TeX Live, which is provided as a AWS Lambda Layer.
This layer is built inside a Docker container mimicking the AWS Lambda runtime to ensure compatibility.
Files related to it are found in the subdirectory `lambdalatex-layer` and can be built with the provided `Makefile`:

    # From the main project directory:
    make layer

    # From the lambdalatex-layer subdirectory:
    make build
    make package

In both cases, the output is `lambdalatex-layer/lambdalatex-layer.zip` which can be deploy to AWS Lambda, or used locally.

AWS Lambda imposes a 50 MB limit on individual layer archives and so the build routine is minimal but complete.
Currently, LaTeX packages are specified in `lambdalatex-layer/install-tlmgr-packages.sh`.

## The AWS Lambda Handlers

Handlers (functions) to communicate with `latexmk` are found in the subdirectory `lambdalatex`.

## Deployment

Once `lambdalatex-layer.zip` is built it can be deployed to AWS Lambda via Serverless:

    # From the lambdalatex-layer subdirectory:
    serverless deploy

The layer only needs to be deployed if and only if it was re-built to include additional LaTeX packages.
Otherwise, it should only need to be deployed once.

The service can then be deployed to AWS Lambda also via Serverless:

    # From the main project directory:
    serverless deploy

Serverless will provision everything on the AWS end of things and return both an API token and an API endpoint.
This token should be kept secret as anyone who has it can call the API.

## Cost

AWS has a generous free usage tier and the costs for hosting this service, with normal usage, should be free or close to it.

## Todo

- [ ] Provide options to specify `latexmk` or e.g., `pdflatex`.
- [ ] Provide options to choose which files are outputted (defaults to pdf, but e.g., `pdf,aux` should work too).
- [ ] Provide a way in the background to split up the layers if > 50 MB.
- [ ] Provide an API endpoint to see what packages are installed.
- [ ] Put LaTeX packages in its own separate file to make it easier to edit/change.
- [ ] Add information on how to create custom domains for the API endpoint.
- [ ] Add usage limitation to avoid large costs.

## Prerequisites

 - [Docker](https://www.docker.com)
 - Python 3.7+
 - Serverless (installed via [npm](https://www.npmjs.com) or [Yarn](https://yarnpkg.com/en/))
    
## Acknowledgements

This project would have never began if it weren't for the work of Sam O'Connor in his original [lambdalatex](https://github.com/samoconnor/lambdalatex) project.
Originally I just wanted to refactor the Julia code into Python but I ended up setting up the entire build-deploy-test pipeline as one thing led to another.
