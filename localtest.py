# -*- coding: utf-8 -*-
"""Test the custom built runtime layer locally.
"""
import base64
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import uuid
import zipfile

import click


@click.command()
@click.option(
    "--input",
    "input_dir",
    type=click.Path(exists=True),
    required=True,
    help="path to an input directory (e.g., examples/article)",
)
@click.option(
    "--output_dir",
    "output_dir",
    type=click.Path(),
    default=str(pathlib.Path.cwd()),
    help="directory to write output files to",
    show_default=True,
)
@click.option(
    "--layer",
    type=click.File("rb"),
    default="lambdalatex-layer/lambdalatex-layer.zip",
    show_default=True,
    help="path to the layer file to use",
)
def main(input_dir, output_dir, layer):
    # Transform inputs.
    input_path = pathlib.Path(input_dir)
    layer_zipfile_path = pathlib.Path(layer.name).resolve()

    output_dir = pathlib.Path(output_dir).absolute()
    output_dir.mkdir(exist_ok=True, parents=True)
    pdf_fp = output_dir / "out.pdf"
    stdout_fp = pdf_fp.with_suffix(".stdout.txt")
    stderr_fp = pdf_fp.with_suffix(".stderr.txt")
    stdout_latexmk_fp = pdf_fp.with_suffix(".stdout.latexmk.txt")
    stderr_latexmk_fp = pdf_fp.with_suffix(".stderr.latexmk.txt")

    click.echo("Running local test with the following arguments:")
    click.echo(f"    Input     {input_dir}")
    click.echo(f"    Output    out.pdf")
    click.echo(f"    Layer     {layer.name}")

    layer_path = make_layer_dir()
    unzip_layer(layer_path, layer_zipfile_path)

    r = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{layer_path}:/opt",
            "-v",
            f"{pathlib.Path.cwd()}:/var/task",
            "lambci/lambda:python3.7",
            "handler.lambda_handler",
            json.dumps({"body": {"input": make_input_str(input_path)}}),
            json.dumps({}),
        ],
        encoding="utf-8",
        capture_output=True,
    )

    # test outputs
    stdout_dict = json.loads(r.stdout)
    lambda_body = stdout_dict.pop("body")
    lambda_response = json.loads(lambda_body)

    stdout_fp.write_text(json.dumps(stdout_dict))
    stderr_fp.write_text(r.stderr)
    if "stdout" in lambda_response:
        stdout_latexmk_fp.write_text(lambda_response["stdout"])
    if "stderr" in lambda_response:
        stdout_latexmk_fp.write_text(lambda_response["stderr"])
    if "output" in lambda_response:
        pdf_fp.write_bytes(base64.b64decode(lambda_response["output"]))

    # Clean up temporary directory.
    shutil.rmtree(layer_path, ignore_errors=True)


def unzip_layer(layer_path: pathlib.Path, layer_zip_path: pathlib.Path):
    """Call subprocess because extracting via Python removes executable permissions."""
    this_dir = pathlib.Path.cwd()
    os.chdir(str(layer_path))
    subprocess.run(["unzip", "-q", str(layer_zip_path)])
    os.chdir(str(this_dir))
    click.echo(f"Unzipped {layer_zip_path.name} to {layer_path}")


def make_layer_dir(layer_dir_prefix: str = "__localtest__/lambdalatex-layer-opt"):
    """Create and return a path to a temporary directory for our layer."""
    layer_path = pathlib.Path(f"{layer_dir_prefix}-{uuid.uuid4()}").resolve()
    layer_path.mkdir(parents=True)
    return layer_path


def make_input_str(input_path: pathlib.Path):
    """Create a base64 encoded zip file of the input directory."""
    with tempfile.SpooledTemporaryFile() as tf:
        with zipfile.ZipFile(tf, "w") as zf:
            for fn in input_path.iterdir():
                zf.write(fn, fn.name)
        # Reset temporary file pointer, read the contents, and base64 encode.
        tf.seek(0)
        input_str = base64.b64encode(tf.read()).decode("utf-8")
    return input_str


if __name__ == "__main__":
    main()
