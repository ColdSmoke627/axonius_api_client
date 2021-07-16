# -*- coding: utf-8 -*-
"""API for working with System Settings -> GUI Settings."""
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from .settings_mixins import SettingsMixins


class SettingsIdentityProviders(SettingsMixins):
    """API for working with System Settings -> Identity Providers Settings."""

    TITLE: str = "Identity Providers Settings"
    GET_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.identity_providers_get
    UPDATE_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.identity_providers_update
