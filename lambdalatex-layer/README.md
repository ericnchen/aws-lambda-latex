# lambdalatex-layer

This subdirectory contains everything needed to build, package, and deploy the
required AWS Lambda Layer through Serverless.

This is set up as it's own Serverless stack to avoid re-creating the layer
every time lambdalatex-sls is (re)deployed.

## Quickstart

Build the Docker image with the required binaries and libraries:

    make build

Package the latest built layer:

    make package

Test the built layer to ensure it works:

    make test

Deploy the layer to AWS Lambda:

    make deploy
