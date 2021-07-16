# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import Optional, Union

import dataclasses_json
import dateutil
import marshmallow
import marshmallow_jsonapi

from ...tools import coerce_bool

DT_FMT = "%Y-%m-%dT%H:%M:%S%z"


class SchemaBool(marshmallow_jsonapi.fields.Bool):
    """Support parsing boolean using own coerce tools."""

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize for schema.dump()."""
        return None if value is None and self.allow_none else coerce_bool_wrap(value)

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize for schema.load()."""
        return None if value is None and self.allow_none else coerce_bool_wrap(value)


class SchemaDateTime(marshmallow_jsonapi.fields.DateTime):
    """Support parsing datetimes using own coerce tools."""

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize for schema.dump()."""
        return None if value is None and self.allow_none else dump_date(value)

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize for schema.load()."""
        return None if value is None and self.allow_none else load_date(value)


class SchemaPassword(marshmallow_jsonapi.fields.Field):
    """Support parsing password strings.

    Notes:
        This exists due to: ["unchanged"]
    """

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize for schema.dump()."""
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize for schema.load()."""
        return value


def coerce_bool_wrap(value: Optional[Union[str, bool]] = None) -> bool:
    """Pass."""
    try:
        return coerce_bool(value)
    except Exception as exc:
        raise marshmallow.ValidationError(str(exc))


def load_date(value: Optional[Union[str, datetime.datetime]]) -> Optional[datetime.datetime]:
    """Pass."""
    try:
        if not isinstance(value, datetime.datetime):
            value = dateutil.parser.parse(value)

        if not value.tzinfo:
            value = value.replace(tzinfo=dateutil.tz.tzutc())
        return value
    except Exception as exc:
        raise marshmallow.ValidationError(str(exc))


def dump_date(value: Optional[Union[str, datetime.datetime]]) -> Optional[str]:
    """Pass."""
    if isinstance(value, datetime.datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=dateutil.tz.tzutc())

        value = value.isoformat()

    return value


def get_field_str_req(**kwargs):
    """Pass."""
    kwargs.setdefault("required", True)
    kwargs.setdefault("allow_none", False)
    kwargs.setdefault("validate", marshmallow.validate.Length(min=1))
    return marshmallow_jsonapi.fields.Str(**kwargs)


def get_field_dc_mm(mm_field: marshmallow.fields.Field, **kwargs) -> dataclasses.Field:
    """Pass."""
    kwargs["metadata"] = dataclasses_json.config(mm_field=mm_field)
    return dataclasses.field(**kwargs)


'''
# No longer used
def get_field_oneof(
    choices: List[str], field: Type[marshmallow.fields.Field] = marshmallow.fields.Str, **kwargs
) -> marshmallow.fields.Field:
    """Pass."""
    kwargs["validate"] = marshmallow.validate.OneOf(choices=choices)
    kwargs.setdefault("required", True)
    return field(**kwargs)
'''
