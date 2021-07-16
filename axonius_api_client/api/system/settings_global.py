# -*- coding: utf-8 -*-
"""API for working with System Settings -> Global Settings."""
from ..api_endpoints import ApiEndpoint, ApiEndpoints
from .settings_mixins import SettingsMixins


class SettingsGlobal(SettingsMixins):
    """API for working with System Settings -> Global Settings."""

    TITLE: str = "Global Settings"
    GET_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.global_get
    UPDATE_ENDPOINT: ApiEndpoint = ApiEndpoints.system_settings.global_update

    def configure_destroy(self, enabled: bool, destroy: bool, reset: bool) -> dict:
        """Enable or disable destroy and factory reset API endpoints.

        Args:
            enabled: enable or disable destroy endpoints
            destroy: enable api/devices/destroy and api/users/destroy endpoints
            reset: enable api/factory_reset endpoint
        """
        return self.update_section(
            section="api_settings",
            enabled=enabled,
            enable_factory_reset=reset,
            enable_destroy=destroy,
            check_unchanged=False,
        )
