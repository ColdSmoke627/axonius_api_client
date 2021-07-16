# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import datetime

import dateutil
import marshmallow
import pytest
from axonius_api_client.api import json_api


class TestSchemaPassword:
    def test_allow_none_false(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaPassword()

        schema = Doctor()
        with pytest.raises(marshmallow.exceptions.ValidationError):
            schema.load({"badwolf": None})

    def test_allow_none_true(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaPassword(allow_none=True)

        schema = Doctor()
        loaded = schema.load({"badwolf": None})
        assert loaded["badwolf"] is None

        dumped = schema.dump(loaded)
        assert dumped["badwolf"] is None

    @pytest.mark.parametrize("value", ["x", ["unchanged"]])
    def test_valid(self, value):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaPassword()

        schema = Doctor()
        loaded = schema.load({"badwolf": value})
        assert loaded["badwolf"] == value
        dumped = schema.dump(loaded)
        assert dumped["badwolf"] == value


class TestSchemaBool:
    def test_allow_none_false(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaBool()

        schema = Doctor()
        with pytest.raises(marshmallow.exceptions.ValidationError):
            schema.load({"badwolf": None})

    def test_allow_none_true(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaBool(allow_none=True)

        schema = Doctor()
        loaded = schema.load({"badwolf": None})
        assert loaded["badwolf"] is None

        dumped = schema.dump(loaded)
        assert dumped["badwolf"] is None

    def test_invalid(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaBool()

        schema = Doctor()
        with pytest.raises(marshmallow.exceptions.ValidationError):
            schema.load({"badwolf": "x"})

    def test_valid(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaBool()

        schema = Doctor()
        loaded = schema.load({"badwolf": "y"})
        assert loaded["badwolf"] is True
        dumped = schema.dump(loaded)
        assert dumped["badwolf"] is True


class TestSchemaDateTime:
    def test_allow_none_false(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaDateTime()

        schema = Doctor()
        with pytest.raises(marshmallow.exceptions.ValidationError):
            schema.load({"badwolf": None})

    def test_allow_none_true(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaDateTime(allow_none=True)

        schema = Doctor()
        loaded = schema.load({"badwolf": None})
        assert loaded["badwolf"] is None

        dumped = schema.dump(loaded)
        assert dumped["badwolf"] is None

    def test_invalid(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaDateTime()

        schema = Doctor()
        with pytest.raises(marshmallow.exceptions.ValidationError):
            schema.load({"badwolf": "x"})

    def test_valid(self):
        class Doctor(marshmallow.Schema):
            badwolf = json_api.custom_fields.SchemaDateTime()

        schema = Doctor()
        loaded = schema.load({"badwolf": "2020-01-01"})
        assert loaded["badwolf"] == datetime.datetime(2020, 1, 1, 0, 0, tzinfo=dateutil.tz.tzutc())
        dumped = schema.dump(loaded)
        assert dumped["badwolf"] == "2020-01-01T00:00:00+00:00"


class TestDumpDate:
    def test_no_tz(self):
        now = datetime.datetime.now()
        assert not now.tzinfo
        value = json_api.custom_fields.dump_date(value=now)
        assert "+00:00" in value


class TestLoadDate:
    def test_no_tz(self):
        now = datetime.datetime.now()
        assert not now.tzinfo
        value = json_api.custom_fields.load_date(value=now)
        assert value.tzinfo

    def test_invalid(self):
        with pytest.raises(marshmallow.exceptions.ValidationError):
            json_api.custom_fields.load_date(value="x")
