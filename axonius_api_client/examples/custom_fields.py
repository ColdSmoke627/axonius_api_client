"""Pass."""
import dataclasses
import re
from typing import Any, Callable, Dict, List, Pattern, Union

from axonius_api_client import Connect, get_env_connect
from axonius_api_client.api import ApiEndpoint, Devices, Users
from axonius_api_client.api.assets.fields import Fields
from axonius_api_client.api.mixins import ChildMixins
from axonius_api_client.exceptions import ApiError, ToolsError
from axonius_api_client.tools import coerce_bool, coerce_int, listify

SNAKE_RE: str = r"([^A-Za-z0-9])"
SNAKE_PATTERN: Pattern = re.compile(SNAKE_RE)
NAME_RE: str = r"^([a-z])[a-z0-9_]*$"
NAME_PATTERN: Pattern = re.compile(NAME_RE)
TYPES_SIMPLE = Union[bool, str, float, int]
KEY_ID: str = "internal_axon_id"


def snake_str(value: str) -> str:
    """Pass."""
    if value is None:
        value = ""

    if not isinstance(value, str):
        value = str(value)

    value = SNAKE_PATTERN.sub("_", value)
    value = value.strip("_").lower()
    return value


def coerce_float(obj: Any) -> float:
    """Convert an object into float.

    Args:
        obj: object to convert to float

    Raises:
        :exc:`ToolsError`: if obj is not able to be converted to float
    """
    try:
        value = float(obj)
    except Exception:
        vtype = type(obj).__name__
        raise ToolsError(f"Supplied value {obj!r} of type {vtype} is not a float.")
    return value


def get_ax_id(item: Union[str, dict]) -> str:
    """Pass."""
    if isinstance(item, str):
        return item

    if isinstance(item, dict) and KEY_ID in item:
        return item[KEY_ID]

    raise ApiError(f"Item {item!r} must be a string or a dictionary with a {KEY_ID!r} key")


def get_ax_ids(items: Union[List[str], List[dict]]) -> List[str]:
    """Pass."""
    ret = [y for y in [get_ax_id(x) for x in listify(items)] if y]

    if not ret:
        raise ApiError(f"No {KEY_ID!r} supplied as a list of strings or dictionaries")

    return ret


@dataclasses.dataclass
class CustomFieldsBuilder:
    """Pass."""

    apiobj: Union[Devices, Users]
    fields: dict = dataclasses.field(default_factory=dict)

    def add_custom(
        self,
        title: str,
        value: Union[TYPES_SIMPLE, List[TYPES_SIMPLE]],
        type: str = "string",
        as_list: bool = False,
        coerce: bool = True,
    ) -> dict:
        """Pass."""
        title = self._check_title(title=title)
        type = self._check_type(type=type)
        name = self._build_name(title=title)
        # XXX string type can't take empty string??

        if isinstance(value, (list, tuple)):
            as_list = True

        if as_list:
            value = listify(value)

        if coerce:
            value = self._coerce_value(value=value, type=type, as_list=as_list)

        if type == "boolean" and isinstance(value, list):
            raise ApiError("Boolean types can not be a list")

        existing_schema = self._get_schema(name=name, title=title)

        if existing_schema:
            stype = existing_schema["type_norm"]
            if "array" in stype:
                value = listify(value)
                stype = stype.replace("array_", "")

            if type != stype:
                raise ApiError(
                    f"Type {type!r} does not match type {stype!r} of pre-existing custom field"
                )

        if isinstance(value, list) and not type.startswith("list_"):
            type = f"list_{type}"

        self.fields[name] = {
            "predefined": False,
            "title": title,
            "type": type,
            "value": value,
        }
        return self.fields

    def _build_name(self, title: str):
        name = snake_str(value=title)
        name = self._check_name(name=name)

        if not name.startswith("custom_"):
            name = f"custom_{name}"

        return name

    def _get_schema(self, name: str, title: str) -> dict:
        """Pass."""
        for schema in self._schemas_gui:
            if schema["name_base"] == name:
                return schema
            if schema["name_qual"] == name:
                return schema
            if schema["title"] == title:
                return schema
        return {}

    @staticmethod
    def _schema_filter(obj: dict) -> bool:
        if obj.get("is_details"):
            return True

        if obj.get("is_all"):
            return True

        return False

    @property
    def _schemas_gui(self) -> List[dict]:
        """Pass."""
        return [x for x in self._schemas["gui"] if not self._schema_filter(x)]

    @property
    def _schemas(self) -> dict:
        """Pass."""
        return self.apiobj.fields.get()

    def _coerce_value(
        self,
        value: Union[TYPES_SIMPLE, List[TYPES_SIMPLE]],
        type: str,
        as_list: bool = False,
    ) -> Union[TYPES_SIMPLE, List[TYPES_SIMPLE]]:
        """Pass."""
        coercer = self._types.get(type)

        if isinstance(value, (list, tuple)) or as_list:
            return [coercer(x) for x in listify(value)]

        return coercer(value)

    def _check_name(self, name: str) -> str:
        """Pass."""
        name = str(name).strip().lower()

        if not NAME_PATTERN.match(name):
            raise ApiError(f"Invalid field name {name!r}, must match regex {NAME_RE}")

        if name in self._illegal_names:
            raise ApiError(f"Invalid field name {name!r}, for internal use only")

        return name

    def _check_title(self, title: str) -> str:
        """Pass."""
        pre = f"Invalid title {title!r}"
        title = str(title).strip()

        if not title:
            raise ApiError(f"{pre} - must be a non-empty string")

        if title in self._illegal_names:
            raise ApiError(f"{pre} - for internal use only")

        return title

    def _check_type(self, type: str) -> str:
        """Pass."""
        pre = f"Invalid type {type!r}"
        type = str(type).strip().lower()

        if type not in self._types:
            valid = ", ".join(list(self._types))
            raise ApiError(f"{pre} - valid choices: {valid}")

        return type

    @property
    def _types(self) -> Dict[str, Callable]:
        """Pass."""
        return {
            "string": str,
            "boolean": coerce_bool,
            "number": coerce_float,
            "integer": coerce_int,
        }

    @property
    def _illegal_names(self) -> List[str]:
        """Pass."""
        return ["id", "asset_entity_info"]

    # TODO: OUT OF SCOPE FOR CURRENT REQUIREMENTS
    # def add_agg_simple(self, field: str, value: Union[TYPES_SIMPLE, List[TYPES_SIMPLE]]) -> dict:
    #     """Pass."""

    # def add_agg_complex(self, field: str, value: dict) -> dict:
    #     """Pass."""

    # def delete_custom(self, title: str) -> dict:
    #     """Pass."""
    #     title = self._check_title(value=title)

    #     name = self._check_name(value=name)
    #     key = f"custom_{name}"

    #     self.fields[key] = {
    #         "toDelete": True,
    #     }
    #     return self.fields

    # def __str__(self):
    #     """Pass."""
    #     items = []
    #     for k, v in self.fields.items():
    #         name = k
    #         title = v["title"]
    #         value = v["value"]
    #         type = v["type"]


class CustomFields(ChildMixins):
    """Pass."""

    def get_builder(self) -> CustomFieldsBuilder:
        """Pass."""
        return CustomFieldsBuilder(apiobj=self.parent)

    def update(self, ids: Union[List[str], List[dict]], fields: dict) -> str:
        """Pass."""
        ids = get_ax_ids(items=ids)
        ret = self._update(ids=ids, fields=fields)
        # TODO: nasty work around for invalidating TTLCache on fields.get()
        self.parent.fields = Fields(parent=self.parent)
        return ret

    def _update(self, ids: List[str], fields: dict) -> str:
        """Pass."""
        endpoint = ApiEndpoint(
            method="put",
            path="api/V4.0/{entity_type}/entity_custom",
            request_schema_cls=None,
            request_model_cls=None,
            response_schema_cls=None,
            response_model_cls=None,
            response_as_text=True,
        )

        body = {
            "data": {
                "type": "entities_custom_data_schema",
                "attributes": {"selection": {"ids": ids, "include": True}, "data": fields},
            }
        }

        return endpoint.perform_request(
            http=self.auth.http, http_args={"json": body}, entity_type=self.parent.ASSET_TYPE
        )


if __name__ == "__main__":
    client_args = {}
    # --- get the URL, API key, API secret, & other variables from the default ".env" file
    client_args.update(get_env_connect())

    # create a client
    client = Connect(**client_args)

    # add support for custom_fields to each asset type
    client.devices.custom_fields = CustomFields(parent=client.devices)
    client.users.custom_fields = CustomFields(parent=client.users)

    # start the client, connecting to the Axonius REST API
    client.start()

    """
    Notes:
        - 'internal_axon_id' is all we really need from each asset, and that is one of the builtin
          fields that the REST API will always return.
        - Use fields_default=False when getting assets so that the defualt fields
          defined in the API client are requested.
        - Use fields_error=False so that the API Client doesn't throw an error because no
          additional fields were requested.

    Options for getting assets:

    # -> OPTION 1: get all
    assets = client.devices.get(fields_default=False, fields_error=False)

    # -> OPTION 2: get selection with query built by GUI query wizard
    query = '("specific_data.data.hostname" == regex("a", "i")) and ("specific_data.data.last_seen" >= date("NOW - 30d"))'
    assets = client.devices.get(query=query, fields_default=False, fields_error=False)

    # -> OPTION 3: get selection with query built by API Client query wizard
    wiz_entries = [
        {"type": "simple", "value": "hostname contains a"},
        {"type": "simple", "value": "last_seen last_days 30"},
    ]
    assets = client.devices.get(wiz_entries=wiz_entries, fields_default=False, fields_error=False)
    """  # noqa

    wiz_entries = [
        {"type": "simple", "value": "hostname contains a"},
        {"type": "simple", "value": "last_seen last_days 30"},
    ]
    assets = client.devices.get(wiz_entries=wiz_entries, fields_default=False, fields_error=False)

    # get a custom fields builder
    builder = client.devices.custom_fields.get_builder()

    # use the builder to add a custom fields
    builder.add_custom(title="this is a string", value="string value", type="string")
    builder.add_custom(title="this is a boolean", value="y", type="boolean")
    builder.add_custom(title="this is a integer", value=1, type="integer")
    builder.add_custom(title="this is a float", value=1.5, type="number")
    builder.add_custom(
        title="this is a list of strings", value=["string value1", "string value2"], type="string"
    )
    builder.add_custom(title="this is a list of integers", value=[1, "2", 3.8], type="integer")
    builder.add_custom(
        title="this is a list of floats", value=[1.2, "2.8", 3.14159265359], type="number"
    )

    #  create or update the custom fields produced by the builder on a list of assets
    client.devices.custom_fields.update(ids=assets, fields=builder.fields)
