# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from . import api, auth, cli, constants, exceptions, http, tools, version
from .api import Actions, Adapters, Devices, Enforcements, Users
from .auth import ApiKey as AuthApiKey
from .auth import Creds as AuthCreds
from .exceptions import (AlreadyLoggedIn, ApiError, AuthError, AxonError,
                         ConnectError, HttpError, InvalidCredentials,
                         InvalidJson, NotLoggedIn, ObjectNotFound,
                         ResponseError, TooFewObjectsFound, ToolsError,
                         TooManyObjectsFound, UnknownError)
from .http import Http, ParserUrl
from .tools import Connect

__version__ = version.__version__
LOG = tools.LOG

__all__ = (
    # Connection handler
    "Connect",
    # http client
    "Http",
    "ParserUrl",
    # authentication
    "AuthCreds",
    "AuthApiKey",
    # api
    "Users",
    "Devices",
    "Actions",
    "Adapters",
    "Enforcements",
    # modules
    "api",
    "auth",
    "http",
    "exceptions",
    "version",
    "tools",
    "constants",
    "cli",
    # exceptions
    "AxonError",
    "ApiError",
    "ToolsError",
    "AuthError",
    "HttpError",
    "ResponseError",
    "InvalidJson",
    "ObjectNotFound",
    "TooFewObjectsFound",
    "TooManyObjectsFound",
    "UnknownError",
    "InvalidCredentials",
    "NotLoggedIn",
    "AlreadyLoggedIn",
    "ConnectError",
)
