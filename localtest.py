# -*- coding: utf-8 -*-
"""Test the custom built runtime layer locally.
"""
import base64
import json
import os
import pathlib
import subprocess
import zipfile

import click

import lambdalatex


@click.command()
@click.option(
    "-i",
    "--input_dir",
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help="input directory to zip up and use",
)
@click.option(
    "-o",
    "--output_dir",
    type=click.Path(file_okay=False),
    default=str(pathlib.Path().cwd() / "output"),
    help="directory to write output files to",
    show_default=True,
)
@click.option(
    "--compile-with",
    default="docker",
    type=click.Choice(["docker", "aws", "native"]),
    show_default="docker",
)
def main(input_dir, output_dir, compile_with):
    input_dir = pathlib.Path(input_dir).resolve()
    output_dir = pathlib.Path(output_dir).resolve()
    layer_zipfile = pathlib.Path("lambdalatex-layer/lambdalatex-layer.zip").resolve()

    layer_opt_dir = output_dir / "opt"
    layer_opt_dir.mkdir(exist_ok=True, parents=True)
    unzip_zipfile(layer_zipfile, layer_opt_dir, replace=True)

    input_zipfile = zip_input_dir(input_dir=input_dir, output_dir=output_dir)
    input_zipfile_b64 = base64.b64encode(input_zipfile.read_bytes()).decode("utf-8")

    context = json.dumps({})

    if compile_with == "docker":
        event = json.dumps({"body": {"input": input_zipfile_b64}})
        command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{layer_opt_dir}:/opt",
            "-v",
            f"{pathlib.Path.cwd()}:/var/task",
            "lambci/lambda:python3.7",
            "handler.lambda_handler",
            event,
            context,
        ]
        r = subprocess.run(command, encoding="utf-8", capture_output=True)

    elif compile_with == "native":
        event = {"body": {"input": input_zipfile_b64}}
        lambda_response = lambdalatex.lambda_handler(event, context)
        response_body = json.loads(lambda_response["body"])

        class ResponseWrapper:
            pass

        r = ResponseWrapper()
        if "stderr" in response_body:
            r.stderr = response_body["stderr"]
        if "output" in response_body:
            r.stdout = json.dumps(
                {"body": json.dumps({"output": response_body["output"]})}
            )
    else:
        raise NotImplementedError

    if r.stderr != "":
        (output_dir / "_stderr.txt").write_text(r.stderr)

    response_body = json.loads(json.loads(r.stdout)["body"])

    for k in ("stdout", "stderr"):
        if response_body.get(k, "") != "":
            (output_dir / k).with_suffix(".txt").write_text(response_body[k])

    if "output" in response_body:
        decoded_pdf = base64.b64decode(response_body["output"])
        (output_dir / "output.pdf").write_bytes(decoded_pdf)
        click.echo(f"lambdalatex: saved pdf to {output_dir}")


def unzip_zipfile(zipfile_: pathlib.Path, layer: pathlib.Path, replace: bool = True):
    """Call subprocess because extracting via Python removes executable permissions."""
    this_dir = pathlib.Path.cwd()
    os.chdir(str(layer))
    if replace:
        cmd = ["unzip", "-qo", str(zipfile_)]
    else:
        cmd = ["unzip", "-q", str(zipfile_)]
    subprocess.run(cmd)
    os.chdir(str(this_dir))
    click.echo(f"unzipped: {zipfile_.name} to {layer}")


def zip_input_dir(input_dir: pathlib.Path, output_dir: pathlib.Path) -> pathlib.Path:
    input_zipfile = output_dir / "input.zip"
    with zipfile.ZipFile(input_zipfile, "w") as zf:
        for fn in input_dir.iterdir():
            zf.write(fn, fn.name)
    return input_zipfile


if __name__ == "__main__":
    main()
