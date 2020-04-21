# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
import re

from ...api.parsers.tables import tablize
from ...tools import json_dump
from ..context import CONTEXT_SETTINGS, click
from ..options import AUTH, add_options

OPTIONS = [
    *AUTH,
    click.option(
        "--adapter-re",
        "-ar",
        "adapter_re",
        default=".*",
        help="Only fetch fields for adapters matching this regex",
        metavar="REGEX",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--field-re",
        "-fr",
        "field_re",
        default=".*",
        help="Only fetch fields matching this regex",
        metavar="REGEX",
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--field-key",
        "-fk",
        "field_key",
        default="name_qual",
        help="Which field key to match against for --field-re",
        type=click.Choice(
            ["name_qual", "name", "name_base", "column_title", "column_name"]
        ),
        show_envvar=True,
        show_default=True,
    ),
    click.option(
        "--export-format",
        "-xf",
        "export_format",
        type=click.Choice(["json-full", "json", "str", "table"]),
        help="Control how much schema information to return",
        default="str",
        show_envvar=True,
        show_default=True,
    ),
]


@click.command(name="get-fields", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(
    ctx,
    url,
    key,
    secret,
    adapter_re,
    field_re,
    field_key,
    export_format,
    help_detailed=None,
    **kwargs
):
    """Get the available fields (columns) for assets."""
    p_grp = ctx.parent.command.name

    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    apiobj = getattr(client, p_grp)

    are = re.compile(adapter_re, re.I)
    fre = re.compile(field_re, re.I)

    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        rows = apiobj.fields.get()

    matches = []

    for adapter, schemas in rows.items():
        if not are.search(adapter):
            continue

        for schema in schemas:
            if not fre.search(schema[field_key]):
                continue

            matches.append(schema)

    if export_format == "json-full":
        click.secho(json_dump(matches))
        ctx.exit(0)

    if export_format == "json":
        keys = {
            "adapter_name": "Adapter",
            "column_name": "Name",
            "column_title": "Title",
            "is_complex": "Is complex",
            "is_root": "Is root",
            "type_norm": "Normalized Type",
            "name_qual": "Fully Qualified Name",
        }
        matches = [{k: v for k, v in x.items() if k in keys} for x in matches]
        click.secho(json_dump(matches))
        ctx.exit(0)

    if export_format == "str":
        for x in matches:
            click.secho(x["column_name"])
        ctx.exit(0)

    if export_format == "table":
        keys = {
            "adapter_name": "Adapter",
            "column_name": "Name",
            "column_title": "Title",
            "type_norm": "Normalized Type",
        }
        matches = [{keys[k]: v for k, v in x.items() if k in keys} for x in matches]
        click.secho(tablize(value=matches, err=None, fmt="simple", footer=True))
        ctx.exit(0)
