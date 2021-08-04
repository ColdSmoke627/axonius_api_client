# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type

import marshmallow
import marshmallow_jsonapi

from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaBool


class CentralCoreSettingsUpdateSchema(DataSchemaJson):
    """Pass."""

    delete_backups = SchemaBool()
    enabled = SchemaBool()

    class Meta:
        """Pass."""

        type_ = "central_core_settings_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return CentralCoreSettingsUpdate


class AdditionalDataAws(marshmallow.Schema):
    """Pass."""

    key_name = marshmallow_jsonapi.fields.Str(required=True)
    bucket_name = marshmallow_jsonapi.fields.Str(
        required=False, allow_none=True, load_default=None, dump_default=None
    )
    preshared_key = marshmallow_jsonapi.fields.Str(
        required=False, allow_none=True, load_default=None, dump_default=None
    )
    access_key_id = marshmallow_jsonapi.fields.Str(
        required=False, allow_none=True, load_default=None, dump_default=None
    )
    secret_access_key = marshmallow_jsonapi.fields.Str(
        required=False, allow_none=True, load_default=None, dump_default=None
    )
    delete_backups = SchemaBool(
        required=False, allow_none=True, load_default=None, dump_default=None
    )
    allow_re_restore = SchemaBool(
        required=False, allow_none=True, load_default=None, dump_default=None
    )


class AdditionalDataAwsSchema(marshmallow_jsonapi.fields.Nested):
    """Pass."""

    def __init__(self):
        """Pass."""
        super().__init__(AdditionalDataAws(), data_key="additional_data")


class CentralCoreRestoreAwsRequestSchema(DataSchemaJson):
    """Pass."""

    restore_type = marshmallow_jsonapi.fields.Str(load_default="aws", dump_default="aws")
    additional_data = AdditionalDataAwsSchema()

    class Meta:
        """Pass."""

        type_ = "central_core_restore_request_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return CentralCoreRestoreAwsRequest


class CentralCoreRestoreSchema(DataSchemaJson):
    """Pass."""

    status = marshmallow_jsonapi.fields.Str(required=True)
    message = marshmallow_jsonapi.fields.Str(required=True)
    additional_data = marshmallow_jsonapi.fields.Dict(required=True)

    class Meta:
        """Pass."""

        type_ = "central_core_restore_response_schema"

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return CentralCoreRestore


@dataclasses.dataclass
class CentralCoreSettingsUpdate(DataModel):
    """Pass."""

    delete_backups: bool
    enabled: bool

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return CentralCoreSettingsUpdateSchema


@dataclasses.dataclass
class CentralCoreRestoreAwsRequest(DataModel):
    """Pass."""

    additional_data: AdditionalDataAws
    restore_type: str = "aws"

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return CentralCoreRestoreAwsRequestSchema


@dataclasses.dataclass
class CentralCoreRestore(DataModel):
    """Pass."""

    status: str
    message: str
    additional_data: dict

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return CentralCoreRestoreSchema
