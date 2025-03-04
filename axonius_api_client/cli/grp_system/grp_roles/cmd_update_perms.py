# -*- coding: utf-8 -*-
"""Command line interface for Axonius API Client."""
from ...context import CONTEXT_SETTINGS, click
from ...options import AUTH, add_options
from .grp_common import EXPORT, PERMS, ROLE_NAME, handle_export

GRANT = click.option(
    "--allow/--deny",
    "-a/-d",
    "grant",
    help="Permissions supplied should be granted or denied",
    required=False,
    default=True,
    show_envvar=True,
    show_default=True,
)


OPTIONS = [
    *AUTH,
    EXPORT,
    ROLE_NAME,
    PERMS,
    GRANT,
]


@click.command(name="update-perms", context_settings=CONTEXT_SETTINGS)
@add_options(OPTIONS)
@click.pass_context
def cmd(ctx, url, key, secret, export_format, name, grant, perms, **kwargs):
    """Update a roles permissions."""
    perms = dict(perms)
    client = ctx.obj.start_client(url=url, key=key, secret=secret)
    with ctx.obj.exc_wrap(wraperror=ctx.obj.wraperror):
        data = client.system_roles.set_perms(name=name, grant=grant, **perms)
        ctx.obj.echo_ok(f"Updated role permissions for {name!r}")

    handle_export(ctx=ctx, data=data, export_format=export_format, **kwargs)
