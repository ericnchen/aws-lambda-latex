# -*- coding: utf-8 -*-
import base64
import subprocess


def test_stdout_from_subprocess_is_str():
    from lambdalatex import get_stdout

    response = subprocess.run(["ls"], encoding="utf-8", capture_output=True)
    assert isinstance(get_stdout(response), str)


def test_stderr_from_subprocess_is_str():
    from lambdalatex import get_stderr

    response = subprocess.run(["ls", "-"], encoding="utf-8", capture_output=True)
    assert isinstance(get_stderr(response), str)


def test_pdfstr_is_correctly_base64_encoded_str():
    from lambdalatex import get_pdfstr

    with open("tests/out.pdf", "rb") as f:
        expected = base64.b64encode(f.read()).decode("utf-8")

    assert get_pdfstr("tests/out.pdf") == expected
