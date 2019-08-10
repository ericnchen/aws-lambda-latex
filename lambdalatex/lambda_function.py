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
    body = get_body(event)

    td = tempfile.TemporaryDirectory()

    unzip_dir = pathlib.Path(td.name)
    extract_zipfile(get_zipfile(body), target=unzip_dir)

    infile = unzip_dir / "main.tex"
    pdf = infile.with_suffix(".pdf")

    os.environ["PATH"] = "/opt/bin:" + os.environ["PATH"]
    cmd = ["latexmk", "-verbose", "-interaction=batchmode", "-pdf", infile]
    r = subprocess.run(cmd, cwd=unzip_dir, encoding="utf-8", capture_output=True)

    output_body = {
        "pdf": get_pdfstr(pdf),
        "stdout": get_stdout(r),
        "stderr": get_stderr(r),
    }

    td.cleanup()

    return {
        "body": json.dumps(output_body),
        "headers": {"Content-Type": "application/json"},
        "isBase64Encoded": False,
        "statusCode": STATUS_SUCCESS_PDF_GENERATED if output_body["pdf"] != "" else 500,
    }


def get_stderr(response: subprocess.CompletedProcess) -> str:
    """Get the stderr of the response."""
    return response["stderr"] if isinstance(response, dict) else response.stderr


def get_stdout(response: subprocess.CompletedProcess) -> str:
    """Get the stdout of the response."""
    return response["stdout"] if isinstance(response, dict) else response.stdout


def get_pdfstr(filename: str) -> str:
    """Return a pdf file as a Base64 encoded string."""
    return base64.b64encode(pathlib.Path(filename).read_bytes()).decode("utf-8")


def extract_zipfile(zip_file: zipfile.ZipFile, target: pathlib.Path):
    """Extract the zipfile to the target directory."""
    zip_file.extractall(path=target)


def get_body(event: dict) -> dict:
    """Get the event body from the lambda handler."""
    return json.loads(event["body"]) if "body" in event else event


def get_zipfile(body: dict) -> zipfile.ZipFile:
    """Get input as a zipfile from event trigger."""
    return zipfile.ZipFile(io.BytesIO(base64.b64decode(body["input"])))
