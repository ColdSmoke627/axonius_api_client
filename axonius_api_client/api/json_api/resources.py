# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
from typing import Optional, Type

import dataclasses_json
import marshmallow
import marshmallow_jsonapi

from ...constants.api import MAX_PAGE_SIZE
from ...tools import coerce_int
from ..models import DataModel, DataSchema, DataSchemaJson
from .custom_fields import SchemaBool, get_field_dc_mm


class PaginationSchema(marshmallow.Schema):
    """Pass."""

    offset = marshmallow_jsonapi.fields.Integer(default=0, missing=0)
    limit = marshmallow_jsonapi.fields.Integer(default=140, missing=140)


class ResourcesGetSchema(DataSchemaJson):
    """Pass."""

    sort = marshmallow_jsonapi.fields.Str()
    page = marshmallow_jsonapi.fields.Nested(PaginationSchema)
    search = marshmallow_jsonapi.fields.Str(default="", missing="")
    get_metadata = SchemaBool(missing=True)
    filter = marshmallow_jsonapi.fields.Str(default="", missing="")

    @staticmethod
    def _get_model_cls() -> type:
        """Pass."""
        return ResourcesGet

    class Meta:
        """Pass."""

        type_ = "resource_base_schema"


@dataclasses.dataclass
class PaginationRequest(dataclasses_json.DataClassJsonMixin):
    """Pass."""

    offset: Optional[int] = 0
    """Row to start from"""

    limit: Optional[int] = MAX_PAGE_SIZE
    """Number of rows to return"""

    def __post_init__(self):
        """Pass."""
        self.limit = coerce_int(
            obj=self.limit, max_value=MAX_PAGE_SIZE, min_value=1, fallback=MAX_PAGE_SIZE
        )
        self.offset = coerce_int(obj=self.offset, min_value=0, fallback=0)


@dataclasses.dataclass
class PageSortRequest(dataclasses_json.DataClassJsonMixin):
    """Data attributes for pagination and sort."""

    sort: Optional[str] = None
    """Field to sort on and direction to sort.

    not used by api client (sort using client side logic)

    examples:
        for descending: "-field"
        for ascending: "field"
    """

    page: Optional[PaginationRequest] = get_field_dc_mm(
        marshmallow_jsonapi.fields.Nested(PaginationSchema), default=None
    )
    """Row to start at and number of rows to return.

    examples:
        in get request: page[offset]=0&page[limit]=2000
        in post request: {"data": {"attributes": {"page": {"offset": 0, "limit": 2000}}}
    """
    # FYI: with out using mm_field metadata for nested schemas for dataclasses_json,
    # the mm field that dataclasses_json dynamically creates produces warnings
    # about using deprecated additional_meta args

    get_metadata: bool = True
    """Return pagination metadata in response."""

    def __post_init__(self):
        """Pass."""
        self.page = self.page if self.page else PaginationRequest()


@dataclasses.dataclass
class ResourcesGet(PageSortRequest, DataModel):
    """Request attributes for getting resources."""

    search: Optional[str] = None
    """AQL search term

    not used by api client (filter using client side logic)

    examples:
        (name == regex("test", "i"))
        (name == regex("test", "i")) and tags in ["Linux"]
    """
    filter: Optional[str] = None

    @staticmethod
    def _get_schema_cls() -> Optional[Type[DataSchema]]:
        """Pass."""
        return ResourcesGetSchema


@dataclasses.dataclass
class ResourceDelete(DataModel):
    """Pass."""

    uuid: str
