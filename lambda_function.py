# -*- coding: utf-8 -*-
import base64
import io
import json
import os
import pathlib
import subprocess
import zipfile


def get_base64_encoded_zip_string(event):
    """Extract the base64 encoded zip file as a string from an input event."""
    # When lambda_handler is called through the API Gateway extra parsing needed.
    if "body" in event:
        return json.loads(event["body"])["input"]

    # When lambda_handler is called directly just take the input key.
    return event["input"]


def lambda_handler(event, context):
    # Parse and extract inputs.
    input_str = get_base64_encoded_zip_string(event)
    input_zip = zipfile.ZipFile(io.BytesIO(base64.b64decode(input_str)))

    # Extract the contents to a temporary directory and change to it.
    unzip_dir = "/tmp/latex"
    input_zip.extractall(path=unzip_dir)
    os.chdir(unzip_dir)

    # Always use main.tex for the main file to compile.
    infile = pathlib.Path("main.tex")
    outfile = pathlib.Path(infile.name).with_suffix(".pdf")

    # Run pdflatex...
    r = subprocess.run(
        [
            "latexmk",
            "-verbose",
            "-interaction=batchmode",
            "-pdf",
            "-output-directory=/tmp/latex",
            infile.name,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # The response needs to have, at minimum, the "body" key.
    return {
        "body": json.dumps(
            {
                "output": base64.b64encode(outfile.read_bytes()).decode("utf-8"),
                "stdout": r.stdout.decode("utf-8") if r.stdout is not None else None,
                "stderr": r.stderr.decode("utf-8") if r.stderr is not None else None,
            }
        ),
        "isBase64Encoded": False,
        "statusCode": 200,
    }
