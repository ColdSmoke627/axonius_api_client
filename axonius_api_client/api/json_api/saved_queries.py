# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type

import marshmallow_jsonapi

from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaBool, SchemaDateTime, get_field_dc_mm


class SavedQuerySchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    always_cached = SchemaBool(load_default=False, dump_default=False)
    asset_scope = marshmallow_jsonapi.fields.Bool(load_default=False, dump_default=False)
    private = marshmallow_jsonapi.fields.Bool(load_default=False, dump_default=False)
    description = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    view = marshmallow_jsonapi.fields.Dict()
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    predefined = marshmallow_jsonapi.fields.Bool(load_default=False, dump_default=False)
    date_fetched = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )
    is_asset_scope_query_ready = SchemaBool()
    is_referenced = SchemaBool()
    query_type = marshmallow_jsonapi.fields.Str()
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())
    timestamp = marshmallow_jsonapi.fields.Str(allow_none=True)
    last_updated = SchemaDateTime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(
        allow_none=True, load_default=None, dump_default=None
    )
    user_id = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)
    uuid = marshmallow_jsonapi.fields.Str(allow_none=True, load_default=None, dump_default=None)

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return SavedQuery

    class Meta:
        """Pass."""

        type_ = "views_details_schema"


class SavedQueryCreateSchema(DataSchemaJson):
    """Pass."""

    name = marshmallow_jsonapi.fields.Str(required=True)
    view = marshmallow_jsonapi.fields.Dict()
    description = marshmallow_jsonapi.fields.Str(load_default="", dump_default="", allow_none=True)
    always_cached = SchemaBool(load_default=False, dump_default=False)
    private = marshmallow_jsonapi.fields.Bool(load_default=False, dump_default=False)
    tags = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Str())

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return SavedQueryCreate

    class Meta:
        """Pass."""

        type_ = "views_schema"


@dataclasses.dataclass
class SavedQuery(DataModel):
    """Pass."""

    id: str
    name: str
    view: dict
    query_type: str
    updated_by: Optional[str] = None
    user_id: Optional[str] = None
    uuid: Optional[str] = None
    date_fetched: Optional[str] = None
    timestamp: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDateTime(allow_none=True), default=None
    )
    always_cached: bool = False
    asset_scope: bool = False
    private: bool = False
    description: Optional[str] = ""
    tags: List[str] = dataclasses.field(default_factory=list)
    predefined: bool = False
    is_asset_scope_query_ready: bool = False
    is_referenced: bool = False

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return SavedQuerySchema


@dataclasses.dataclass
class SavedQueryCreate(DataModel):
    """Pass."""

    name: str
    view: dict
    description: Optional[str] = ""
    always_cached: bool = False
    private: bool = False
    tags: List[str] = dataclasses.field(default_factory=list)

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return SavedQueryCreateSchema
