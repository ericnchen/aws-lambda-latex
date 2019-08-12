# -*- coding: utf-8 -*-
import base64
import json
import pathlib
import zipfile

import pytest

from lambdalatex import (
    get_latexmk_command,
    get_pdf_processor_flag,
    parse_body,
    parse_input,
)


def test_parse_body_returns_dict_when_given_a_json_str():
    # This is what we get when calling from the REST API.
    assert isinstance(parse_body(json.dumps({"foo": "bar"})), dict)


def test_parse_body_returns_dict_when_a_dict():
    # This is what we get when calling locally through Docker or something.
    assert isinstance(parse_body({"foo": "bar"}), dict)


def test_parse_input_returns_zipfile_when_valid_base64_zipfile_string_is_given():
    fp = pathlib.Path("tests/beamer-input.zip")
    parsed = parse_input(base64.b64encode(fp.read_bytes()).decode("utf-8"))
    assert isinstance(parsed, zipfile.ZipFile)


def test_parse_input_raises_file_not_found_error_when_zipfile_without_main_tex_is_given():
    fp = pathlib.Path("tests/dummy-input.zip")
    with pytest.raises(FileNotFoundError):
        parse_input(base64.b64encode(fp.read_bytes()).decode("utf-8"))


def test_parse_input_raises_bad_zipfile_error_when_not_given_a_zip_file():
    fp = pathlib.Path("tests/beamer-output.pdf")
    with pytest.raises(zipfile.BadZipFile):
        parse_input(base64.b64encode(fp.read_bytes()).decode("utf-8"))


def test_get_latexmk_command_returns_a_list_of_strings():
    cmd = get_latexmk_command({})
    assert isinstance(cmd, list)
    for each_part in cmd:
        assert isinstance(each_part, str)


def test_get_processor_flag_returns_pdf_for_valid_choices():
    assert get_pdf_processor_flag("pdflatex") == "-pdf"


def test_get_processor_flag_returns_pdf_for_invalid_choices():
    assert get_pdf_processor_flag("invalid") == "-pdf"


def test_get_processor_flag_returns_pdf_for_xelatex_as_its_not_implemented_yet():
    assert get_pdf_processor_flag("xelatex") == "-pdf"


def test_get_processor_flag_returns_pdf_for_lualatex_as_its_not_implemented_yet():
    assert get_pdf_processor_flag("lualatex") == "-pdf"
