#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automate updating a custom field with a business unit using regex searches against fields."""
import dataclasses
import json
import pathlib
import re
import textwrap
from typing import Any, ClassVar, List, Optional, Pattern, Union

import click
from axonius_api_client.api import ApiEndpoint, asset_callbacks
from axonius_api_client.cli import cli
from axonius_api_client.cli.context import CONTEXT_SETTINGS
from axonius_api_client.cli.options import AUTH, add_options
from axonius_api_client.connect import Connect
from axonius_api_client.tools import (coerce_bool, dt_now, echo_error, echo_ok,
                                      get_path, listify, path_read)


EXAMPLE: str = """
[
    {
        "business_unit": "TEST1",
        "searches": [
            {
                "field": "specific_data.data.hostname",
                "regex": "a"
            }
        ]
    },
    {
        "business_unit": "TEST2",
        "and_flag": true,
        "searches": [
            {
                "field": "specific_data.data.hostname",
                "regex": "a"
            },
            {
                "field": "specific_data.data.hostname",
                "regex": "b"
            }
        ]
    },
    {
        "business_unit": "TEST3",
        "overwrite": true,
        "searches": [
            {
                "field": "specific_data.data.hostname",
                "regex": "d"
            }
        ]
    },
    {
        "business_unit": "TEST4",
        "and_flag": true,
        "searches": [
            {
                "field": "specific_data.data.hostname",
                "regex": "a"
            },
            {
                "field": "specific_data.data.hostname",
                "regex": "c",
                "not_flag": true
            }
        ]
    }
]
"""


class Options:
    """Pass."""

    bu_field_name: str = "c_business_unit"
    bu_field_title: str = "c_Business_Unit"
    input_file: str = "bu_specs.json"
    input_file_changes: str = ""
    output_file_log: str = "{date}_bu_log.json"
    output_file_changes: str = "{date}_bu_changes.json"
    verbose: bool = False
    include_defined: bool = False
    datefmt: str = "%Y-%m-%dT%H-%M-%S"
    fields_error: bool = True
    page_progress: int = asset_callbacks.Base.args_map()["page_progress"]
    do_echo: bool = True


custom_field_update: ApiEndpoint = ApiEndpoint(
    method="put",
    path="api/V4.0/devices/entity_custom",
    request_schema_cls=None,
    request_model_cls=None,
    response_schema_cls=None,
    response_model_cls=None,
    response_as_text=True,
)


def get_bu_field_name():
    """Pass."""
    return f"adapters_data.gui.custom_{Options.bu_field_name}"


def echo_debug(msg: str):
    """Pass."""
    if Options.verbose:
        echo_ok(msg=msg, fg="blue")


def get_str(obj: dict, key: str, info: str, fallback: Optional[str] = None) -> str:
    """Get a string from a dict."""
    kinfo = f"Dictionary key {key!r} in {info}"
    mustbe = "must be a non-empty string"

    if key not in obj:
        if isinstance(fallback, str):
            return fallback

        raise echo_error(msg=f"{kinfo} not supplied, {mustbe}")

    value = obj[key]

    if isinstance(value, str):
        value = value.strip()

    if not isinstance(value, str) or not value:
        vtype = f"supplied type {type(value)} with value {value}"
        echo_error(msg=f"{kinfo} invalid value, {mustbe}, {vtype}")
    return value


def get_lod(obj: dict, key: str, info: str) -> str:
    """Get a list of dicts from a dict."""
    kinfo = f"Dictionary key {key!r} in {info}"
    mustbe = "must be a non-empty list of dictionaries"

    if key not in obj:
        raise Exception(f"{kinfo} not supplied, {mustbe}")

    value = obj[key]

    if not isinstance(value, list) or not value:
        vtype = f"supplied type {type(value)} with value {value}"
        echo_error(msg=f"{kinfo} invalid value, {mustbe}, {vtype}")

    return value


def get_bool(obj: dict, key: str, info: str, fallback: Optional[bool] = None) -> str:
    """Get a boolean from a dict."""
    kinfo = f"Dictionary key {key!r} in {info}"

    if key not in obj:
        if isinstance(fallback, bool):
            return fallback

        echo_error(msg=f"{kinfo} not supplied")

    value = obj[key]

    try:
        value = coerce_bool(obj=value, errmsg=kinfo)
    except Exception as exc:
        echo_error(msg=f"{kinfo} invalid value\n{exc}")

    return value


def get_attrs_string(obj: object, attrs: List[str]) -> str:
    """Build a string describing an object."""
    vals = [f"{x}={getattr(obj, x, None)!r}" for x in attrs]
    vals = ", ".join(vals)
    return f"{obj.__class__.__name__}({vals})"


@dataclasses.dataclass
class Search:
    """Simple regex search."""

    client: Connect

    group: "Group"
    """Parent group of this search."""

    index: int
    """Index of this search from the source group."""

    field: str
    """Field to perform regex on."""

    regex: str
    """Regex to perform on field."""

    not_flag: bool = False
    """NOT this search."""

    description: str = ""
    """Optional description of this search."""

    pattern: ClassVar[Pattern] = None
    """Compiled pattern of regex."""

    def __str__(self):
        """Pass."""
        return get_attrs_string(
            obj=self,
            attrs=[
                "index",
                "description",
                "field",
                "regex",
                "not_flag",
            ],
        )

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def __post_init__(self):
        """Pass."""
        try:
            self.pattern = re.compile(self.regex)
        except Exception as exc:
            echo_error(msg=f"Regex pattern {self.regex} in {self} failed to compile: {exc}")

        try:
            self.field = self.client.devices.fields.get_field_name(value=self.field)
        except Exception:
            msg = f"Invalid field in {self}"
            echo_error(msg=msg, abort=Options.fields_error)

        echo_debug(msg=f"Loaded {self}")

    def to_dict(self) -> dict:
        """Pass."""
        return {
            "description": self.description,
            "field": self.field,
            "regex": self.regex,
            "not_flag": self.not_flag,
        }

    @classmethod
    def load(self, obj: dict, client: Connect, group: "Group", index: int) -> "Search":
        """Load a search entry for a BU group object."""
        info = f"search index #{index} under {group}"
        not_flag = get_bool(obj=obj, key="not_flag", info=info, fallback=False)
        regex = get_str(obj=obj, key="regex", info=info)
        field = get_str(obj=obj, key="field", info=info)
        description = get_str(obj=obj, key="description", info=info, fallback="")
        obj = Search(
            group=group,
            index=index,
            not_flag=not_flag,
            regex=regex,
            field=field,
            description=description,
            client=client,
        )
        return obj

    def check(self, asset: "Asset") -> dict:
        """Pass."""
        value = asset.get_field_value(field=self.field)
        result = self.pattern.search(value)
        match = bool(result)

        if self.not_flag:
            match = not match

        ret = self.to_dict()
        ret["field_value"] = value
        ret["search_match"] = match
        return ret


@dataclasses.dataclass
class Group:
    """Pass."""

    client: Connect

    business_unit: str
    """The business unit to assign for this group."""

    searches: List[Search]
    """List of simple or complex searches to use for this group."""

    index: int
    """Index of this group from the source file."""

    description: str = ""
    """Optional description of this set of searches."""

    and_flag: bool = False
    """AND all of the searches in this group."""

    overwrite: bool = False
    """If the searches in this group result in a match, overwrite the bu_field."""

    def __str__(self):
        """Pass."""
        return get_attrs_string(
            obj=self, attrs=["index", "business_unit", "description", "overwrite", "and_flag"]
        )

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def __len__(self) -> int:
        """Pass."""
        return len(self.searches)

    def __getitem__(self, i: int) -> Search:
        """Pass."""
        return self.searches[i]

    def __post_init__(self):
        """Pass."""
        echo_debug(msg=f"Loaded {self}")
        self.searches = [
            Search.load(obj=x, index=i, group=self, client=self.client)
            for i, x in enumerate(self.searches)
        ]

    def to_dict(self, searches: bool = False) -> dict:
        """Pass."""
        ret = {
            "business_unit": self.business_unit,
            "description": self.description,
            "and_flag": self.and_flag,
            "overwrite": self.overwrite,
        }
        if searches:
            ret["searches"] = [x.to_dict() for x in self.searches]
        return ret

    @property
    def fields(self) -> List[str]:
        """Get a list of all unique fields for all searches in this group."""
        values = [x.field for x in self.searches]
        return sorted(list(set(values)))

    @classmethod
    def load(self, obj: dict, client: Connect, index: int) -> "Group":
        """Load a BU group object."""
        info = f"group #{index}"
        and_flag = get_bool(obj=obj, key="and_flag", info=info, fallback=False)
        overwrite = get_bool(obj=obj, key="overwrite", info=info, fallback=False)
        business_unit = get_str(obj=obj, key="business_unit", info=info)
        searches = get_lod(obj=obj, key="searches", info=info)
        description = get_str(obj=obj, key="description", info=info, fallback="")
        obj = Group(
            business_unit=business_unit,
            and_flag=and_flag,
            overwrite=overwrite,
            searches=searches,
            index=index,
            description=description,
            client=client,
        )
        return obj

    def check(self, asset: "Asset") -> dict:
        """Pass."""
        ret = self.to_dict()

        update = self.overwrite or (
            not asset.business_unit_current and not asset.business_unit_change
        )

        if update:
            searches = [x.check(asset=asset) for x in self.searches]
            matches = [x["search_match"] for x in searches]
            match = (self.and_flag and all(matches)) or (not self.and_flag and any(matches))
        else:
            searches = []
            match = False

        ret["searches"] = searches
        ret["group_match"] = match

        if match:
            asset.business_unit_change = self.business_unit

        return ret


@dataclasses.dataclass
class Groups:
    """Pass."""

    client: Connect
    groups: List[Group]
    path: pathlib.Path

    def __str__(self):
        """Pass."""
        return get_attrs_string(obj=self, attrs=["source"])

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def __len__(self) -> int:
        """Pass."""
        return len(self.groups)

    def __getitem__(self, i: int) -> Group:
        """Pass."""
        return self.groups[i]

    def __post_init__(self):
        """Pass."""
        echo_ok(msg=f"Loaded {self}")
        self.groups = [
            Group.load(obj=x, index=i, client=self.client) for i, x in enumerate(self.groups)
        ]

        fields = "\n  " + "\n  ".join(self.fields)
        business_units = "\n  " + "\n  ".join(self.business_units)
        echo_debug(msg=f"Fields: {fields}")
        echo_debug(msg=f"Business Units: {business_units}")

    def to_list(self, searches: bool = True) -> List[dict]:
        """Pass."""
        ret = [x.to_dict(searches=searches) for x in self.groups]
        return ret

    @property
    def source(self) -> str:
        """Pass."""
        return str(self.path)

    @property
    def business_units(self) -> List[str]:
        """Get a list of all unique business units."""
        values = [x.business_unit for x in self.groups]
        return sorted(list(set(values)))

    @property
    def fields(self) -> List[str]:
        """Get a list of all unique fields."""
        values = [y for x in self.groups for y in x.fields]
        return sorted(list(set(values)))

    @classmethod
    def load(self, path: Union[str, pathlib.Path], client: Connect) -> "Groups":
        """Load the JSON input file."""
        try:
            path, groups = path_read(obj=path, is_json=True)
        except Exception as exc:
            echo_error(msg=f"Failed to load data from path {path}: {exc}")

        if not isinstance(groups, list) or not groups:
            vtype = f"supplied type {type(groups)} with value {groups}"
            echo_error(msg=f"Groups must be non-empty list of dictionaries, {vtype}")

        obj = Groups(
            groups=groups,
            path=path,
            client=client,
        )
        return obj

    def check(self, asset: "Asset"):
        """Pass."""
        return [x.check(asset=asset) for x in self.groups]


@dataclasses.dataclass
class Changes:
    """Pass."""

    client: Connect
    changes: dict
    groups: List[dict]
    bu_field_name: str
    bu_field_title: str
    path: pathlib.Path

    def __str__(self):
        """Pass."""
        return get_attrs_string(obj=self, attrs=["source"])

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def __post_init__(self):
        """Pass."""
        echo_ok(msg=f"Loaded {self}")

    @property
    def source(self) -> str:
        """Pass."""
        return str(self.path)

    def get_request_body(self, ids: List[str], business_unit: str):
        """Pass."""
        return {
            "data": {
                "type": "entities_custom_data_schema",
                "attributes": {
                    "selection": {"ids": ids, "include": True},
                    "data": {
                        f"custom_{self.bu_field_name}": {
                            "value": business_unit,
                            "predefined": False,
                            "title": self.bu_field_title,
                            "type": "string",
                        }
                    },
                },
            }
        }

    def perform_request(self, ids: List[str], business_unit: str):
        """Pass."""
        api_endpoint = custom_field_update
        http_args = {"json": self.get_request_body(ids=ids, business_unit=business_unit)}
        return api_endpoint.perform_request(http=self.client.HTTP, http_args=http_args)

    def run(self):
        """Pass."""
        for business_unit, ids in self.changes.items():
            echo_ok(
                f"Setting custom field {self.bu_field_name!r} to "
                f"{business_unit!r} for {len(ids)} assets"
            )
            self.perform_request(ids=ids, business_unit=business_unit)
        echo_ok("Done!")

    @classmethod
    def load(self, path: Union[str, pathlib.Path], client: Connect) -> "Changes":
        """Load the JSON input file."""
        try:
            path, data = path_read(obj=path, is_json=True)
        except Exception as exc:
            echo_error(msg=f"Failed to load data from path {path}: {exc}")

        keys = ["changes", "groups", "bu_field_name", "bu_field_title"]

        if not isinstance(data, dict) or not all([x in data for x in keys]):
            vtype = f"supplied type {type(data)} with value {data}"
            echo_error(msg=f"Changes must be a dictionary with keys {keys}, {vtype}")

        obj = Changes(
            changes=data["changes"],
            groups=data["groups"],
            bu_field_name=data["bu_field_name"],
            bu_field_title=data["bu_field_title"],
            path=path,
            client=client,
        )
        return obj


@dataclasses.dataclass
class Asset:
    """Pass."""

    asset: dict
    client: Connect
    groups: Groups

    results: ClassVar[List[dict]] = None
    business_unit_change: ClassVar[str] = None

    def __post_init__(self):
        """Pass."""
        self.results = []

    def __str__(self):
        """Pass."""
        return get_attrs_string(obj=self, attrs=["id", "business_unit_current"])

    def __repr__(self):
        """Pass."""
        return self.__str__()

    @property
    def id(self) -> str:
        """Pass."""
        return self.asset["internal_axon_id"]

    @property
    def business_unit_current(self) -> str:
        """Pass."""
        ret = self.get_field_value(field=get_bu_field_name())
        return ret

    def get_field_values(self, field: str) -> List[Any]:
        """Pass."""
        ret = listify(self.asset.get(field))
        return ret

    def get_field_value(self, field: str, as_str: bool = True) -> str:
        """Pass."""
        ret = self.get_field_values(field=field)
        ret = ret[0] if ret else ""

        if not isinstance(ret, str) and as_str:
            ret = str(ret)

        return ret

    def check(self) -> List[dict]:
        """Pass."""
        ret = {}
        ret.update(self.asset)
        ret["results"] = [x.check(asset=self) for x in self.groups]
        ret["business_unit_current"] = self.business_unit_current
        ret["business_unit_change"] = self.business_unit_change
        return ret


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options(AUTH)
@click.option(
    "--bu-field-name",
    "-b",
    "bu_field_name",
    help="Name of Custom field to store business unit in",
    metavar="FIELD NAME",
    required=False,
    default=Options.bu_field_name,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--bu-field-title",
    "-b",
    "bu_field_title",
    help="Title of Custom field to store business unit in",
    metavar="FIELD TITLE",
    required=False,
    default=Options.bu_field_title,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--datefmt",
    "-df",
    "datefmt",
    help="Date format to use in output files with {date}",
    metavar="FORMAT",
    required=False,
    default=Options.datefmt,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--input-file",
    "-if",
    "input_file",
    help="JSON file containing BU search specifications",
    metavar="PATH",
    required=False,
    default=Options.input_file,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--output-file-changes",
    "-ofc",
    "output_file_changes",
    help="JSON file to write change changes to (will replace {date} with --datefmt)",
    metavar="PATH",
    required=False,
    default=Options.output_file_changes,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--output-file-log",
    "-ofl",
    "output_file_log",
    help="JSON File to write assets and the group results to (will replace {date} with --datefmt)",
    metavar="PATH",
    required=False,
    default=Options.output_file_log,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--fields-error/--no-fields-error",
    "-fe/-nfe",
    "fields_error",
    help="Validate the fields supplied in searches",
    is_flag=True,
    default=Options.fields_error,
    required=False,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--fetch-echo/--no-fetch-echo",
    "-fe/-nfe",
    "do_echo",
    default=True,
    help="Print out details during fetch of assets",
    show_envvar=True,
    show_default=True,
    is_flag=True,
    hidden=False,
)
@click.option(
    "--page-progress",
    "page_progress",
    default=asset_callbacks.Base.args_map()["page_progress"],
    help="Print progress every N rows",
    show_envvar=True,
    show_default=True,
    type=click.INT,
    hidden=False,
)
@click.option(
    "--include-defined/--no-include-defined",
    "-id/-nid",
    "include_defined",
    help="Fetch and process assets with --bu-field already defined",
    is_flag=True,
    default=Options.include_defined,
    required=False,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--verbose/--no-verbose",
    "-v/-nv",
    "verbose",
    default=Options.verbose,
    help="Be noisy.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.pass_context
def bu_process(
    ctx,
    url: str,
    key: str,
    secret: str,
    verbose: bool = Options.verbose,
    bu_field_name: str = Options.bu_field_name,
    bu_field_title: str = Options.bu_field_title,
    input_file: str = Options.input_file,
    output_file_changes: str = Options.output_file_changes,
    output_file_log: str = Options.output_file_log,
    include_defined: bool = Options.include_defined,
    datefmt: str = Options.datefmt,
    fields_error: bool = Options.fields_error,
    page_progress: int = Options.page_progress,
    do_echo: bool = Options.do_echo,
):
    """Process business_units assets using regex searches against fields."""
    now = dt_now()
    date = now.strftime(datefmt)

    input_file = get_path(obj=input_file)
    output_file_changes = get_path(obj=output_file_changes.format(date=date))
    output_file_log = get_path(obj=output_file_log.format(date=date))

    Options.verbose = verbose
    Options.bu_field_name = bu_field_name
    Options.bu_field_title = bu_field_title
    Options.input_file = input_file
    Options.output_file_changes = output_file_changes
    Options.output_file_log = output_file_log
    Options.datefmt = datefmt
    Options.fields_error = fields_error
    Options.page_progress = page_progress
    Options.do_echo = do_echo

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    groups = Groups.load(path=input_file, client=client)
    fields = [get_bu_field_name(), *groups.fields]

    if include_defined:
        wiz_entries = None
    else:
        wiz_entries = [{"type": "simple", "value": f"! {get_bu_field_name()} exists"}]

    gen = client.devices.get(
        generator=True,
        fields_manual=fields,
        field_null=True,
        fields_default=False,
        wiz_entries=wiz_entries,
        page_progress=page_progress,
        do_echo=do_echo,
    )

    echo_ok(f"Writing assets and results to '{output_file_log}'")
    output_file_log_fh = output_file_log.open("w")
    echo_ok(f"Writing changes to perform to '{output_file_changes}'")
    output_file_changes_fh = output_file_changes.open("w")

    indent = 2
    prefix = " " * indent
    first = True
    changes = {}
    output_file_log_fh.write("[")
    for asset in gen:
        obj = Asset(asset=asset, client=client, groups=groups)
        pre = "\n" if first else ",\n"
        output_file_log_fh.write(pre)
        first = False
        result = obj.check()
        value = json.dumps(result, indent=indent)
        value = textwrap.indent(value, prefix=prefix)
        output_file_log_fh.write(value)

        change = obj.business_unit_change
        if isinstance(change, str):
            if change not in changes:
                changes[change] = []
            changes[change].append(obj.id)

        del obj
        del asset

    output_file_log_fh.write("\n]")
    output_file_log_fh.close()

    output = {
        "changes": changes,
        "groups": groups.to_list(),
        "bu_field_name": bu_field_name,
        "bu_field_title": bu_field_title,
    }
    json.dump(output, output_file_changes_fh, indent=indent)
    output_file_changes_fh.close()


@click.command(context_settings=CONTEXT_SETTINGS)
@add_options(AUTH)
@click.option(
    "--input-file-changes",
    "-ifc",
    "input_file_changes",
    help="JSON file with changes produced by 'bu-process --output-file-changes'",
    metavar="PATH",
    required=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--verbose/--no-verbose",
    "-v/-nv",
    "verbose",
    default=Options.verbose,
    help="Be noisy.",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.option(
    "--example",
    default=False,
    help="Print out an example bu_specs.json",
    is_flag=True,
    show_envvar=True,
    show_default=True,
)
@click.pass_context
def bu_perform(
    ctx,
    url: str,
    key: str,
    secret: str,
    input_file_changes: str,
    verbose: bool = Options.verbose,
    example: bool = False,
):
    """Perform changes produced by a previous run of bu-process."""
    if example:
        print(EXAMPLE)
        ctx.exit(0)

    input_file_changes = get_path(obj=input_file_changes)

    Options.verbose = verbose
    Options.input_file_changes = input_file_changes

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    changes = Changes.load(path=input_file_changes, client=client)
    changes.run()
    ctx.exit(0)


cli.add_command(bu_process)
cli.add_command(bu_perform)

if __name__ == "__main__":
    cli()
