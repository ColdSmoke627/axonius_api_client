# -*- coding: utf-8 -*-
"""API for working with System Settings -> Lifecycle Settings."""
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from .settings_mixins import SettingsMixins


class SettingsLifecycle(SettingsMixins):
    """API for working with System Settings -> Lifecycle Settings."""

    TITLE: str = "Lifecycle Settings"
    GET_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.lifecycle_get
    UPDATE_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.lifecycle_update
