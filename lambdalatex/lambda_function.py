# -*- coding: utf-8 -*-
import base64
import io
import json
import logging
import os
import pathlib
import subprocess
import tempfile
import zipfile

logger = logging.getLogger(__name__)

STATUS_SUCCESS_PDF_GENERATED = 200

# Prepend to PATH so that our binaries are found first.
os.environ["PATH"] = "/opt/bin:" + os.environ["PATH"]


# noinspection PyUnusedLocal
def lambda_handler(event, context):
    """
    `event` contains the request inputs as a JSON `str`. Turn it into a `dict`:

        body = json.loads(event['body'])

    `body` needs to have the following keys:

        input (str): Base64 encoded zip file containing a main.tex and its
            supporting files.
    """
    body = parse_body(event["body"])
    input_zipfile = str64_to_zip(body["input"])

    cmd = ["latexmk", "-verbose", "-interaction=batchmode", "-pdf", "main.tex"]

    with tempfile.TemporaryDirectory() as td:
        input_zipfile.extractall(path=td)
        r = subprocess.run(cmd, cwd=td, encoding="utf-8", capture_output=True)

        output_body = {
            "pdf": get_pdfstr(td + "/main.pdf"),
            "stdout": get_stdout(r),
            "stderr": get_stderr(r),
        }

    return {
        "body": json.dumps(output_body),
        "headers": {"Content-Type": "application/json"},
        "isBase64Encoded": False,
        "statusCode": STATUS_SUCCESS_PDF_GENERATED if output_body["pdf"] != "" else 500,
    }


def parse_body(body) -> dict:
    """Parse the request body into a dict."""
    # When called from APIG body is a JSON str, but is an actual dict when called from
    # locally via Docker.
    return json.loads(body) if isinstance(body, str) else body


def str64_to_zip(str64: str) -> zipfile.ZipFile:
    """Decode a Base64 encoded str and convert it into a zipfile object."""
    return zipfile.ZipFile(io.BytesIO(base64.b64decode(str64)))


def get_stderr(response: subprocess.CompletedProcess) -> str:
    """Get the stderr of the response."""
    return response["stderr"] if isinstance(response, dict) else response.stderr


def get_stdout(response: subprocess.CompletedProcess) -> str:
    """Get the stdout of the response."""
    return response["stdout"] if isinstance(response, dict) else response.stdout


def get_pdfstr(filename: str) -> str:
    """Return a pdf file as a Base64 encoded string."""
    fp = pathlib.Path(filename)
    if fp.exists():
        return base64.b64encode(fp.read_bytes()).decode("utf-8")
    return ""
