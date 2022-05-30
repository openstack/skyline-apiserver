# Copyright 2021 99cloud
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
from logging import StreamHandler
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture
from _pytest.fixtures import SubRequest

from skyline_apiserver.log import LOG, setup as log_setup
from skyline_apiserver.tests.fake import FAKER
from skyline_apiserver.tests.models import ArgumentData, TestData


class TestLog:
    @pytest.fixture
    def file_sink_captor(self, request: SubRequest, tmp_path: Path) -> Path:
        file_name: str = request.param
        file = tmp_path.joinpath(file_name)
        file.touch()
        return file

    @pytest.mark.ddt(
        TestData(
            arguments=("file_sink_captor",),
            indirect=("file_sink_captor",),
            argument_data_set=[
                ArgumentData(
                    id="str_file_path",
                    values=(FAKER.text.word(),),
                ),
            ],
        ),
        TestData(
            arguments=("debug",),
            argument_data_set=[
                ArgumentData(
                    id="enable_debug",
                    values=(True,),
                ),
                ArgumentData(
                    id="disable_debug",
                    values=(False,),
                ),
            ],
        ),
        TestData(
            arguments=("level",),
            argument_data_set=[
                ArgumentData(
                    id="debug_level",
                    values=("debug",),
                ),
                ArgumentData(
                    id="info_level",
                    values=("info",),
                ),
                ArgumentData(
                    id="warning_level",
                    values=("warning",),
                ),
                ArgumentData(
                    id="error_level",
                    values=("error",),
                ),
            ],
        ),
    )
    def test_file_sink_setup(self, file_sink_captor: Path, debug: bool, level: str) -> None:
        log_setup(file_sink_captor.as_posix(), debug)
        content = FAKER.text.text()
        log = getattr(LOG, level)
        log(content)
        file_content = file_sink_captor.read_text()
        if debug is False and level in ["debug"]:
            assert f"| {level.upper():<8} |" not in file_content
            assert content not in file_content
        else:
            assert f"| {level.upper():<8} |" in file_content
            assert content in file_content

    @pytest.fixture
    def stream_sink_captor(
        self,
        request: SubRequest,
        capsys: CaptureFixture[str],
    ) -> CaptureFixture[str]:
        return capsys

    @pytest.mark.ddt(
        TestData(
            arguments=("stream_sink_captor",),
            indirect=("stream_sink_captor",),
            argument_data_set=[
                ArgumentData(
                    id="std_output",
                    values=(StreamHandler,),
                ),
            ],
        ),
        TestData(
            arguments=("debug",),
            argument_data_set=[
                ArgumentData(
                    id="enable_debug",
                    values=(True,),
                ),
                ArgumentData(
                    id="disable_debug",
                    values=(False,),
                ),
            ],
        ),
        TestData(
            arguments=("level",),
            argument_data_set=[
                ArgumentData(
                    id="debug_level",
                    values=("debug",),
                ),
                ArgumentData(
                    id="info_level",
                    values=("info",),
                ),
                ArgumentData(
                    id="warning_level",
                    values=("warning",),
                ),
                ArgumentData(
                    id="error_level",
                    values=("error",),
                ),
            ],
        ),
    )
    def test_stream_sink_setup(
        self,
        stream_sink_captor: CaptureFixture[str],
        debug: bool,
        level: str,
    ) -> None:
        log_setup(StreamHandler(), debug)
        content = FAKER.text.text()
        log = getattr(LOG, level)
        log(content)
        std_out, std_err = stream_sink_captor.readouterr()
        if debug is False and level in ["debug"]:
            assert f"| {level.upper():<8} |" not in std_err
            assert content not in std_err
        else:
            assert f"| {level.upper():<8} |" in std_err
            assert content in std_err

    @pytest.mark.ddt(
        TestData(
            arguments=("file_sink_captor",),
            indirect=("file_sink_captor",),
            argument_data_set=[
                ArgumentData(
                    id="str_file_path",
                    values=(FAKER.text.word(),),
                ),
            ],
        ),
        TestData(
            arguments=("debug",),
            argument_data_set=[
                ArgumentData(
                    id="enable_debug",
                    values=(True,),
                ),
                ArgumentData(
                    id="disable_debug",
                    values=(False,),
                ),
            ],
        ),
        TestData(
            arguments=("level",),
            argument_data_set=[
                ArgumentData(
                    id="debug_level",
                    values=("debug",),
                ),
                ArgumentData(
                    id="info_level",
                    values=("info",),
                ),
                ArgumentData(
                    id="warning_level",
                    values=("warning",),
                ),
                ArgumentData(
                    id="error_level",
                    values=("error",),
                ),
            ],
        ),
    )
    def test_standard_logging(self, file_sink_captor: Path, debug: bool, level: str) -> None:
        log_setup(file_sink_captor.as_posix(), debug)
        content = FAKER.text.text()
        std_logger = logging.getLogger()
        log = getattr(std_logger, level)
        log(content)
        file_content = file_sink_captor.read_text()
        if debug is False and level in ["debug"]:
            assert f"| {level.upper():<8} |" not in file_content
            assert content not in file_content
        else:
            assert f"| {level.upper():<8} |" in file_content
            assert content in file_content
