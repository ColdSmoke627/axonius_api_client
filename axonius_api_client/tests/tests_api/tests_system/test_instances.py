# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

import pytest
from axonius_api_client.api import ApiEndpoints, Signup, json_api
from axonius_api_client.exceptions import ApiError, NotFoundError


class TestInstancesPrivate:
    def test_get_api_keys(self, api_client):
        data = api_client.instances._get_api_keys()
        assert isinstance(data, dict)
        assert isinstance(data["api_key"], str) and data["api_key"]
        assert isinstance(data["api_secret"], str) and data["api_secret"]

    def test_get_update(self, api_client):
        data = api_client.instances._get()
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, json_api.instances.Instance)

        instance = data[0]

        node_id = instance.node_id
        node_name = instance.node_name
        hostname = instance.hostname
        use_env = instance.use_as_environment_name

        update = api_client.instances._update_attrs(
            node_id=node_id,
            node_name=node_name,
            hostname=hostname,
            use_as_environment_name=not use_env,
        )
        assert not update

        reget = api_client.instances._get()[0].use_as_environment_name
        assert reget is not use_env

        reset = api_client.instances._update_attrs(
            node_id=node_id,
            node_name=node_name,
            hostname=hostname,
            use_as_environment_name=use_env,
        )
        assert not reset

        reget = api_client.instances._get()[0].use_as_environment_name
        assert reget is use_env

    def test_get_update_central_core(self, api_client):
        settings = api_client.instances._get_central_core_config()
        assert isinstance(settings, json_api.system_settings.SystemSettings)

        config_key = "delete_backups"
        value_orig = settings.config[config_key]
        value_to_set = not value_orig

        to_update = {}
        to_update.update(settings.config)
        to_update[config_key] = value_to_set
        updated = api_client.instances._update_central_core_config(**to_update)
        assert isinstance(updated, json_api.system_settings.SystemSettings)
        assert updated.config == to_update

        to_restore = {}
        to_restore.update(settings.config)
        to_restore[config_key] = value_orig

        restored = api_client.instances._update_central_core_config(**to_restore)
        assert restored.config == settings.config

    def test_feature_flags(self, api_client):
        value = api_client.instances._feature_flags()
        assert isinstance(value, json_api.system_settings.FeatureFlags)
        assert isinstance(value.config, dict)
        assert isinstance(value.document_meta["schema"], dict)


class TestInstancesPublic:
    def test_get(self, api_client):
        data = api_client.instances.get()
        assert isinstance(data, list) and data
        for item in data:
            assert isinstance(item, dict)

    def test_get_cached(self, api_client):
        data = api_client.instances.get_cached()
        assert isinstance(data, list) and data
        for item in data:
            assert isinstance(item, json_api.instances.Instance)

    def test_get_collectors(self, api_client):
        instances = api_client.instances.get_collectors()
        assert isinstance(instances, list)

        for instance in instances:
            assert isinstance(instance, dict)

    def test_get_central_core_config(self, api_client):
        data = api_client.instances.get_central_core_config()
        bools = ["delete_backups", "enabled"]

        for i in bools:
            v = data.pop(i)
            assert isinstance(v, bool)

        assert not data

    def test_get_set_core_delete_mode(self, api_client):
        orig_value = api_client.instances.get_core_delete_mode()
        assert isinstance(orig_value, bool)

        update_value = api_client.instances.set_core_delete_mode(enabled=not orig_value)
        assert update_value is not orig_value

        reset_value = api_client.instances.set_core_delete_mode(enabled=orig_value)
        assert reset_value == orig_value

    def test_get_set_central_core_mode(self, api_client):
        orig_value = api_client.instances.get_central_core_mode()
        assert isinstance(orig_value, bool)

        update_value = api_client.instances.set_central_core_mode(enabled=not orig_value)
        assert update_value is not orig_value

        reset_value = api_client.instances.set_central_core_mode(enabled=orig_value)
        assert reset_value == orig_value

    def test_get_set_is_env_name(self, api_client):
        node_name = api_client.instances.get_core(key="node_name")
        orig_value = api_client.instances.get_is_env_name(name=node_name)
        assert isinstance(orig_value, bool)

        update_value = api_client.instances.set_is_env_name(name=node_name, enabled=not orig_value)
        assert update_value is not orig_value

        reset_value = api_client.instances.set_is_env_name(name=node_name, enabled=orig_value)
        assert reset_value == orig_value

    def test_get_set_hostname(self, api_client):
        node_name = api_client.instances.get_core(key="node_name")
        orig_value = api_client.instances.get_hostname(name=node_name)
        assert isinstance(orig_value, str)

        new_value = f"{orig_value}-a"
        update_value = api_client.instances.set_hostname(name=node_name, value=new_value)
        assert update_value == new_value

        reset_value = api_client.instances.set_hostname(name=node_name, value=orig_value)
        assert reset_value == orig_value

    def test_feature_flags(self, api_client):
        value = api_client.instances.feature_flags
        assert isinstance(value, json_api.system_settings.FeatureFlags)
        assert isinstance(value.config, dict)
        assert isinstance(value.document_meta["schema"], dict)

    def test_has_cloud_compliance(self, api_client):
        value = api_client.instances.has_cloud_compliance
        assert isinstance(value, bool)

    def test_license_expiry(self, api_client):
        value = api_client.instances.license_expiry
        assert isinstance(value, datetime.datetime) or value is None

    def test_license_days_left(self, api_client):
        value = api_client.instances.license_days_left
        assert isinstance(value, int) or value is None

    def test_trial_expiry(self, api_client):
        value = api_client.instances.trial_expiry
        assert isinstance(value, datetime.datetime) or value is None

    def test_trial_days_left(self, api_client):
        value = api_client.instances.trial_days_left
        assert isinstance(value, int) or value is None

    def test_get_by_name_id_core_value(self, api_client):
        core = api_client.instances.get_core()
        value = api_client.instances.get_by_name_id_core(value=core["name"])
        assert isinstance(value, dict) and value

        value = api_client.instances.get_by_name_id_core(value=core["node_id"])
        assert isinstance(value, dict) and value

    def test_get_by_name_id_core_core_serial_true(self, api_client):
        value = api_client.instances.get_by_name_id_core(serial=True)
        assert isinstance(value, dict) and value

    def test_get_by_name_id_core_core_serial_false(self, api_client):
        value = api_client.instances.get_by_name_id_core(serial=False)
        assert isinstance(value, json_api.instances.Instance)

    def test_get_by_name_id_core_invalid(self, api_client):
        with pytest.raises(NotFoundError):
            api_client.instances.get_by_name_id_core("badwolf")

    def test_get_by_name_invalid(self, api_client):
        with pytest.raises(NotFoundError):
            api_client.instances.get_by_name("badwolf")

    def test_set_name(self, api_client):
        orig_value = api_client.instances.get_core(key="name")
        new_value = "Test"

        update_value = api_client.instances.set_name(name=orig_value, new_name=new_value)
        assert update_value == new_value

        reset_value = api_client.instances.set_name(name=new_value, new_name=orig_value)
        assert reset_value == orig_value

    def test_admin_script_upload_path_file(self, api_client, tmp_path):
        file_path = tmp_path / "admin_script_test.txt"
        file_path.write_text("badwolf\nbadwolf\nbadwolf")
        data = api_client.instances.admin_script_upload_path(path=file_path)
        assert isinstance(data, dict) and data
        assert data["file_name"] == "admin_script_test.txt"
        assert isinstance(data["file_uuid"], str) and data["file_uuid"]
        assert data["execute_result"] == "file executed"

    def test_admin_script_upload_path_url(self, api_client):
        path = f"{api_client.HTTP.url}/{ApiEndpoints.meta.about.path}"
        data = api_client.instances.admin_script_upload_path(path=path)
        assert isinstance(data, dict) and data
        assert data["file_name"] == "about"
        assert isinstance(data["file_uuid"], str) and data["file_uuid"]
        assert data["execute_result"] == "file executed"

    def test_get_api_keys(self, api_client):
        data = api_client.instances.get_api_keys()
        assert isinstance(data, dict)
        assert isinstance(data["api_key"], str) and data["api_key"]
        assert isinstance(data["api_secret"], str) and data["api_secret"]

    def test_get_api_keys_not_signed_up(self, api_client, monkeypatch):
        monkeypatch.setattr(Signup, "is_signed_up", False)
        with pytest.raises(ApiError):
            api_client.instances.get_api_keys()

    def test_reset_api_keys_not_signed_up(self, api_client, monkeypatch):
        monkeypatch.setattr(Signup, "is_signed_up", False)
        with pytest.raises(ApiError):
            api_client.instances.reset_api_keys()
