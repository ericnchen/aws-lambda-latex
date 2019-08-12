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
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

STATUS_SUCCESS_PDF_GENERATED = 200

# Prepend to PATH so that our binaries are found first.
os.environ["PATH"] = "/opt/bin:" + os.environ["PATH"]


# noinspection PyUnusedLocal
def lambda_handler(event, context):
    """
    `event` contains the request inputs as a JSON `str`. Turn it into a `dict`:

        body = json.loads(event['body'])

    Required:
        input (str): Base64 encoded zip file containing a main.tex and its
            supporting files.

    Optional:
        pdf_processor (str): The processor to use to make the pdf. Choose from
            pdflatex, lualatex, or xelatex. The default choice is pdflatex, and
            invalid choices are also set to pdflatex.
    """
    input_body = parse_body(event["body"])
    latex_command = get_latexmk_command(input_body)

    # These next commands are wrapped in try/except statements so that some output
    # message is given if an error occurred.

    try:
        input_zipfile = parse_input(input_body["input"])
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        return lambda_response(body={"stderr": str(e)}, status_code=500)

    # noinspection PyBroadException
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_zipfile.extractall(path=temp_dir)
            response = subprocess.run(
                latex_command, cwd=temp_dir, encoding="utf-8", capture_output=True
            )
            output_body = parse_response(response, cwd=temp_dir)
    except Exception as e:
        msg = "An unknown or unaccounted for exception occurred."
        return lambda_response(body={"stderr": msg}, status_code=500)

    status_code = 200 if "output" in output_body else 500
    return lambda_response(output_body, status_code=status_code)


def parse_body(body: Union[str, Dict[str, str]]) -> Dict[str, str]:
    """Parse the request body into a dict."""
    # API Gateway gives `body` as a JSON str, but called from Docker gives dict.
    return json.loads(body) if isinstance(body, str) else body


def parse_input(input_string: str) -> zipfile.ZipFile:
    """Parse the request input (a Base64 encoded zip file string) into a zip file.

    Raises:
        zipfile.BadZipFile: When the input string is not a zip file.
        FileNotFoundError: When the input archive does not have a main.tex file.
    """
    input_zipfile = zipfile.ZipFile(io.BytesIO(base64.b64decode(input_string)))
    try:
        input_zipfile.testzip()
    except zipfile.BadZipFile:
        raise zipfile.BadZipFile("The input given is not a valid zip file.")
    if "main.tex" not in input_zipfile.namelist():
        raise FileNotFoundError("The input zip file does not contain a main.tex file.")
    logger.error("The input zip file appears to be a valid input.")
    return input_zipfile


def get_pdf_processor_flag(processor: str = "pdflatex") -> str:
    """Return the latexmk flag needed to set the pdf processor.

    Args:
        processor (optional): Choose from pdflatex, lualatex, or xelatex. The
            default is pdflatex, and invalid choices will also return pdflatex.
    """
    if processor not in ("pdflatex", "lualatex", "xelatex", "pdf", "pdflua", "pdfxe"):
        logger.error("Invalid choice for processor. Using pdflatex instead.")
        return "-pdf"
    if processor in ("lualatex", "pdflua"):
        logger.error(f"The processor chosen is lualatex.")
        logger.error(f"The lualatex processor isn't ready yet. Using pdflatex instead.")
        return "-pdf"
    if processor in ("xelatex", "pdfxe"):
        logger.error(f"The processor chosen is xelatex.")
        logger.error("The xelatex processor isn't ready yet. Using pdflatex instead.")
        return "-pdf"
    logger.error("The processor chosen is pdflatex.")
    return "-pdf"


def get_latexmk_command(body: Union[str, Dict[str, str]]) -> List[str]:
    """Return the full latexmk command as a list of strings."""
    command = [
        "latexmk",
        "-verbose",
        "-interaction=batchmode",
        get_pdf_processor_flag(body.get("pdf_processor")),
        "main.tex",
    ]
    logger.error(f"The full latexmk command is: {' '.join(command)}")
    return command


def parse_response(response: subprocess.CompletedProcess, cwd: str) -> Dict[str, str]:
    """Parse a subprocess response and return the output body as a dict.

    Args:
        response: Response object from `subprocess.run`.
        cwd: The directory the subprocess ran in (i.e., the temporary directory that
            input files were extracted to).
    """
    body = {}
    output_file = pathlib.Path(cwd + "/main.pdf")
    if not output_file.exists():
        logger.error("An error occurred and a pdf document was not generated.")
    else:
        body["output"] = base64.b64encode(output_file.read_bytes()).decode("utf-8")
        logger.error("Successfully generated a pdf document.")
    if response.stdout != "":
        body["stdout"] = response.stdout
    if response.stderr != "":
        body["stderr"] = response.stderr
    return body


def lambda_response(body: Dict[str, str], status_code: int) -> Dict[str, Any]:
    """Function to create a serialized JSON response string for the lambda handler."""
    return {
        "body": json.dumps(body),
        "headers": {"Content-Type": "application/json"},
        "isBase64Encoded": False,
        "statusCode": status_code,
    }
