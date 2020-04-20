# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import logging
import pathlib
import time

import pytest

from axonius_api_client.constants import (
    LOG_LEVEL_CONSOLE,
    LOG_LEVEL_FILE,
    LOG_NAME_FILE,
    LOG_NAME_STDERR,
    LOG_NAME_STDOUT,
)
from axonius_api_client.exceptions import ToolsError
from axonius_api_client.logs import (
    LOG,
    add_file,
    add_null,
    add_stderr,
    add_stdout,
    del_file,
    del_null,
    del_stderr,
    del_stdout,
    get_obj_log,
    gmtime,
    localtime,
    str_level,
)


class TestLogs:
    """Test logs."""

    def test_gmtime(self):
        """Pass."""
        gmtime()
        assert logging.Formatter.converter == time.gmtime

    def test_localtime(self):
        """Pass."""
        localtime()
        assert logging.Formatter.converter == time.localtime

    def test_get_obj_log(self):
        """Pass."""
        log = get_obj_log(obj=self, level="warning")
        assert log.name == "axonius_api_client.tests.tests_pkg.test_logs.TestLogs"
        assert log.level == logging.WARNING

    def test_str_level_int(self):
        """Pass."""
        assert str_level(level=10) == "DEBUG"

    def test_str_level_str_int(self):
        """Pass."""
        assert str_level(level="10") == "DEBUG"

    def test_str_level_str(self):
        """Pass."""
        assert str_level(level="debug") == "DEBUG"

    def test_str_level_fail(self):
        """Pass."""
        with pytest.raises(ToolsError):
            str_level(level="xx")

    def test_add_del_stderr(self):
        """Pass."""
        h = add_stderr(obj=LOG)
        assert h.name == LOG_NAME_STDERR
        assert str_level(level=h.level).lower() == LOG_LEVEL_CONSOLE
        assert isinstance(h, logging.StreamHandler)
        assert h in LOG.handlers

        dh = del_stderr(obj=LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers

    def test_add_del_stdout(self):
        """Pass."""
        h = add_stdout(obj=LOG)
        assert h.name == LOG_NAME_STDOUT
        assert str_level(level=h.level).lower() == LOG_LEVEL_CONSOLE
        assert isinstance(h, logging.StreamHandler)
        assert h in LOG.handlers

        dh = del_stdout(obj=LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers

    def test_add_del_null(self):
        """Pass."""
        del_null(obj=LOG)
        h = add_null(obj=LOG)
        assert h.name == "NULL"
        assert isinstance(h, logging.NullHandler)
        assert h in LOG.handlers

        fh = add_null(obj=LOG)
        assert fh is None

        dh = del_null(obj=LOG)

        assert isinstance(dh, dict)
        assert isinstance(dh[LOG.name], list)

        assert LOG.name in dh
        f = dh.pop(LOG.name)

        assert h in f
        assert h not in LOG.handlers
        assert not dh

    def test_add_del_file(self):
        """Pass."""
        h = add_file(obj=LOG)
        assert h.name == LOG_NAME_FILE
        assert str_level(level=h.level).lower() == LOG_LEVEL_FILE
        assert isinstance(h, logging.handlers.RotatingFileHandler)
        assert h in LOG.handlers
        assert getattr(h, "PATH", None)
        assert isinstance(h.PATH, pathlib.Path)

        dh = del_file(LOG)
        assert isinstance(dh, dict)
        assert LOG.name in dh
        assert isinstance(dh[LOG.name], list)
        assert h in dh[LOG.name]
        assert h not in LOG.handlers
