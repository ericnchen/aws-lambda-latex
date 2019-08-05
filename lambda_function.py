# -*- coding: utf-8 -*-
import base64
import io
import os
import pathlib
import subprocess
import zipfile


def lambda_handler(event, context):
    # Extract input ZIP file to /tmp/latex...
    unzip_dir = "/tmp/latex"
    input_zip = zipfile.ZipFile(io.BytesIO(base64.b64decode(event["input"])))
    input_zip.extractall(path=unzip_dir)
    os.chdir(unzip_dir)

    # Always use main.tex for the main file to compile.
    input_fn = pathlib.Path("main.tex").name
    output_fn = pathlib.Path(input_fn).with_suffix('.pdf').name

    # Run pdflatex...
    r = subprocess.run(
        [
            "latexmk",
            "-verbose",
            "-interaction=batchmode",
            "-pdf",
            "-output-directory=/tmp/latex",
            input_fn,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Read the compiled document and encode it for output.
    with open(output_fn, "rb") as f:
        pdf64 = base64.b64encode(f.read()).decode("ascii")

    # Return base64 encoded pdf and stdout log from pdflatex...
    return {"output": pdf64, "stdout": r.stdout.decode("utf_8"), "filename": output_fn}
