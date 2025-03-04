# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
from typing import List, Optional, Type, Union

import marshmallow
import marshmallow_jsonapi

from ...tools import json_load
from .base import BaseModel, BaseSchema, BaseSchemaJson
from .custom_fields import SchemaDatetime, get_field_dc_mm
from .generic import Deleted


class EnforcementDetailsSchema(BaseSchemaJson):  # pragma: no cover
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    last_updated = SchemaDatetime(allow_none=True)
    updated_by = marshmallow_jsonapi.fields.Str(allow_none=True)
    actions_main = marshmallow_jsonapi.fields.Str()
    actions_main_type = marshmallow_jsonapi.fields.Str()
    triggers_view_name = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_last_triggered = marshmallow_jsonapi.fields.Str(allow_none=True)
    triggers_times_triggered = marshmallow_jsonapi.fields.Int(allow_none=True)
    triggers_period = marshmallow_jsonapi.fields.Str(allow_none=True)

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> type:  # pragma: no cover
        """Pass."""
        return EnforcementDetails

    @marshmallow.pre_load
    def pre_load_fix(self, data, **kwargs) -> Union[dict, BaseModel]:  # pragma: no cover
        """Pass."""
        data = {k.replace(".", "_"): v for k, v in data.items()}
        return data


@dataclasses.dataclass
class EnforcementDetails(BaseModel):  # pragma: no cover
    """Pass."""

    id: str
    name: str
    date_fetched: str
    updated_by: str
    actions_main_type: str
    triggers_period: Optional[str] = None
    triggers_view_name: Optional[str] = None
    last_updated: Optional[datetime.datetime] = get_field_dc_mm(
        mm_field=SchemaDatetime(allow_none=True, load_default=None, dump_default=None), default=None
    )
    actions_main: str = marshmallow_jsonapi.fields.Str()
    triggers_last_triggered: Optional[str] = None
    triggers_times_triggered: Optional[int] = None
    document_meta: Optional[dict] = dataclasses.field(default_factory=dict)

    def __post_init__(self):  # pragma: no cover
        """Pass."""
        self.updated_by = json_load(self.updated_by, error=False)

    @property
    def uuid(self) -> str:  # pragma: no cover
        """Pass."""
        return self.id

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:  # pragma: no cover
        """Pass."""
        return EnforcementDetailsSchema

    @staticmethod
    def _str_properties() -> List[str]:  # pragma: no cover
        """Pass."""
        return [
            "name",
            "uuid",
            "actions_main",
            "actions_main_type",
        ]

    def to_tablize(self):  # pragma: no cover
        """Pass."""
        return {self._human_key(k): getattr(self, k, None) for k in self._str_properties()}

    def get_full_object(self) -> "Enforcement":  # pragma: no cover
        """Pass."""
        from .. import ApiEndpoints

        api_endpoint = ApiEndpoints.enforcements.get_full
        return api_endpoint.perform_request(http=self.HTTP, uuid=self.uuid)

    def delete_object(self) -> Deleted:  # pragma: no cover
        """Pass."""
        from .. import ApiEndpoints

        api_endpoint = ApiEndpoints.enforcements.delete
        request_obj = api_endpoint.load_request(value={"ids": [self.uuid], "include": True})
        return api_endpoint.perform_request(http=self.HTTP, request_obj=request_obj)


class EnforcementSchema(BaseSchemaJson):  # pragma: no cover
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    uuid = marshmallow_jsonapi.fields.Str()
    date_fetched = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_details_schema"

    @staticmethod
    def get_model_cls() -> type:  # pragma: no cover
        """Pass."""
        return Enforcement


@dataclasses.dataclass
class Enforcement(BaseModel):  # pragma: no cover
    """Pass."""

    id: str
    uuid: str
    name: str
    date_fetched: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:  # pragma: no cover
        """Pass."""
        return EnforcementSchema

    @staticmethod
    def _str_properties() -> List[str]:  # pragma: no cover
        """Pass."""
        return [
            "name",
            "uuid",
        ]


class EnforcementCreateSchema(BaseSchemaJson):  # pragma: no cover
    """Pass."""

    name = marshmallow_jsonapi.fields.Str()
    actions = marshmallow_jsonapi.fields.Dict()
    triggers = marshmallow_jsonapi.fields.List(marshmallow_jsonapi.fields.Dict())

    class Meta:
        """Pass."""

        type_ = "enforcements_schema"

    @staticmethod
    def get_model_cls() -> type:  # pragma: no cover
        """Pass."""
        return EnforcementCreate


@dataclasses.dataclass
class EnforcementCreate(BaseModel):  # pragma: no cover
    """Pass."""

    name: str
    actions: dict
    triggers: List[dict]

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:  # pragma: no cover
        """Pass."""
        return EnforcementCreateSchema


class ActionSchema(BaseSchemaJson):  # pragma: no cover
    """Pass."""

    default = marshmallow_jsonapi.fields.Dict()
    schema = marshmallow_jsonapi.fields.Dict()

    class Meta:
        """Pass."""

        type_ = "actions_schema"

    @staticmethod
    def get_model_cls() -> type:  # pragma: no cover
        """Pass."""
        return Action


@dataclasses.dataclass
class Action(BaseModel):  # pragma: no cover
    """Pass."""

    id: str
    default: dict
    schema: dict

    @staticmethod
    def get_schema_cls() -> Optional[Type[BaseSchema]]:  # pragma: no cover
        """Pass."""
        return ActionSchema

    @property
    def name(self):  # pragma: no cover
        """Pass."""
        return self.id
