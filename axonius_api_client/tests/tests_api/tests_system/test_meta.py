# -*- coding: utf-8 -*-
"""Test suite."""
import copy


class SystemMetaBase:
    def val_entity_sizes(self, data):
        data = copy.deepcopy(data)
        avg_document_size = data("avg_document_size")
        assert isinstance(avg_document_size, int)
        capped = data("capped")
        assert isinstance(capped, int)
        entities_last_point = data("entities_last_point")
        assert isinstance(entities_last_point, int)
        size = data("size")
        assert isinstance(size, int)
        assert not data

    def val_historical_sizes(self, data):
        data = copy.deepcopy(data)
        disk_free = data.pop("disk_free")
        assert isinstance(disk_free, int) and disk_free

        disk_used = data.pop("disk_used")
        assert isinstance(disk_used, int) and disk_used

        entity_sizes = data.pop("entity_sizes")
        assert isinstance(entity_sizes, dict)

        users = entity_sizes.pop("Users", {})
        assert isinstance(users, dict) or users is None

        devices = entity_sizes.pop("Devices", {})
        assert isinstance(devices, dict) or users is None
        assert not entity_sizes
        assert not data

    def val_about(self, data):
        """Pass."""
        data = copy.deepcopy(data)
        build_date = data.pop("Build Date")
        assert isinstance(build_date, str) and build_date

        api_version = data.pop("api_client_version")
        assert isinstance(api_version, str) and api_version

        version = data.pop("Version")
        assert isinstance(version, str)

        iversion = data.pop("Installed Version")
        assert isinstance(iversion, str)

        customer_id = data.pop("Customer Id", "")
        assert isinstance(customer_id, str)

        expiry = data.pop("Contract Expiry Date", "")
        assert isinstance(expiry, str)

        assert not data


class TestSystemMetaPrivate(SystemMetaBase):
    def test_private_about(self, api_client):
        data = api_client.meta._about()
        assert isinstance(data, dict)
        self.val_about(data)

    def test_private_historical_sizes(self, api_client):
        data = api_client.meta._historical_sizes()
        assert isinstance(data, dict)
        self.val_historical_sizes(data)


class TestSystemMetaPublic(SystemMetaBase):
    def test_version(self, api_client):
        data = api_client.meta.version
        assert isinstance(data, str)

    def test_about(self, api_client):
        data = api_client.meta.about()
        assert isinstance(data, dict)
        self.val_about(data)

    def test_historical_sizes(self, api_client):
        data = api_client.meta.historical_sizes()
        assert isinstance(data["disk_free_mb"], float)
        assert isinstance(data["disk_used_mb"], float)
        assert (
            isinstance(data["historical_sizes_devices"], dict)
            or data["historical_sizes_devices"] is None
        )
        assert (
            isinstance(data["historical_sizes_users"], dict)
            or data["historical_sizes_users"] is None
        )
