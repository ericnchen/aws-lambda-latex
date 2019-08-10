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
    "--output",
    "output_fn",
    type=click.Path(),
    default="out.pdf",
    help="path to/of output file (if error then extension will be replaced with .txt)",
    show_default=True,
)
@click.option(
    "--layer",
    type=click.File("rb"),
    default="lambdalatex-layer/lambdalatex-layer.zip",
    show_default=True,
    help="path to the layer file to use",
)
def main(input_dir, output_fn, layer):
    # Transform inputs.
    input_path = pathlib.Path(input_dir)
    output_path = pathlib.Path(output_fn)
    layer_zipfile_path = pathlib.Path(layer.name).resolve()

    click.echo("Running local test with the following arguments:")
    click.echo(f"    Input     {input_dir}")
    click.echo(f"    Output    {output_fn}")
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
            json.dumps({"input": make_input_str(input_path)}),
            json.dumps({}),
        ],
        encoding="utf-8",
        capture_output=True,
    )

    stdout_test = r.stdout
    output_path.with_suffix(".stdout.txt").write_text(stdout_test)
    output_path.with_suffix(".stderr.txt").write_text(r.stderr)
    body = json.loads(json.loads(stdout_test)["body"])
    output_path.with_suffix(".stdout.latexmk.txt").write_text(body["stdout"])
    output_path.with_suffix(".stderr.latexmk.txt").write_text(body["stderr"])
    output_path.write_bytes(base64.b64decode(body["pdf"]))

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
