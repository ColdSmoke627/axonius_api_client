# -*- coding: utf-8 -*-
"""API for working with System Settings -> GUI Settings."""
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from .settings_mixins import SettingsMixins


class SettingsGui(SettingsMixins):
    """API for working with System Settings -> GUI Settings."""

    TITLE: str = "GUI Settings"
    GET_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.gui_get
    UPDATE_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.gui_update
