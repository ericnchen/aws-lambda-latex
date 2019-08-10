# -*- coding: utf-8 -*-
import base64
import io
import json
import os
import pathlib
import subprocess
import tempfile
import zipfile

STATUS_SUCCESS_PDF_GENERATED = 200


# noinspection PyUnusedLocal
def lambda_handler(event, context):
    """
    Events:
        main_filename: name of the main latex file to compile (defaults to main.tex)
    """
    td = tempfile.TemporaryDirectory()

    unzip_dir = pathlib.Path(td.name)
    extract_zipfile(get_zipfile(event), target=unzip_dir)

    infile = unzip_dir / event.get("main_filename", "main.tex")

    os.environ["PATH"] = "/opt/bin:" + os.environ["PATH"]
    cmd = ["latexmk", "-verbose", "-interaction=batchmode", "-pdf", infile]
    r = subprocess.run(cmd, cwd=unzip_dir, encoding="utf-8", capture_output=True)

    body = {
        "pdf": read_pdf(infile.with_suffix(".pdf")),
        "stdout": r.stdout,
        "stderr": r.stderr,
    }

    td.cleanup()

    return {
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
        "isBase64Encoded": False,
        "statusCode": STATUS_SUCCESS_PDF_GENERATED if body["pdf"] != "" else 500,
    }


def read_pdf(pdf):
    """Read a pdf file and base64 encode into a string."""
    return base64.b64encode(pdf.read_bytes()).decode("utf-8") if pdf.exists() else ""


def extract_zipfile(zip_file: zipfile.ZipFile, target: pathlib.Path):
    """Extract the zipfile to the target directory."""
    zip_file.extractall(path=target)


def get_zipfile(event):
    """Get input as a zipfile from event trigger."""
    return zipfile.ZipFile(io.BytesIO(base64.b64decode(event["input"])))
