# -*- coding: utf-8 -*-
"""Test the custom built runtime layer locally.
"""
import base64
import pathlib

from lambdalatex import lambda_function


def localtest(event, context):
    # Read a simple zip file and base64 encode it.
    with open("/var/task/build/test-input.zip", "rb") as pl:
        pl64 = base64.b64encode(pl.read())

    # Call the lambda function.
    out = lambda_function.lambda_handler({"input": pl64}, {})

    # Write the output to output to manually review.
    output_file = pathlib.Path(f"/var/task/build/{out['filename']}")
    output_file.write_bytes(base64.b64decode(out["output"]))

    print(f"Verify pdf at build/{out['filename']}")
