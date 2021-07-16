#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base example for setting up the API client."""
import os
import time

import axonius_api_client as axonapi

client_args = {}
# 10.0.247.233.env

# --- get the URL, API key, API secret, & certwarn from the default ".env" file
client_args.update(axonapi.get_env_connect())

# --- OR override OS env vars with the values from a custom .env file
# client_args.update(axonapi.get_env_connect(ax_env="/path/to/envfile", override=True))

# --- OR supply them here in the script
# client_args["url"] = "10.20.0.94"
# client_args["key"] = ""
# client_args["secret"] = ""

# --- Enable logging
# client_args["log_console"] = True  # enable logging to console
# client_args["log_request_attrs"] = "all"  # log all request attributes
# client_args["log_request_body"] = True  # log all request bodies
# client_args["log_response_attrs"] = "all"  # log all response attributes
# client_args["log_response_body"] = True  # log all response bodies

# create a client using the url, key, and secret from OS env
client = axonapi.Connect(**client_args)

j = client.jdump  # json dump helper

client.start()  # connect to axonius
# client.activity_logs          # get audit logs
# client.adapters               # get adapters and update adapter settings
# client.adapters.cnx           # CRUD for adapter connections
# client.dashboard              # get/start/stop discovery cycles
# client.devices                # get device assets
# client.devices.fields         # get field schemas for device assets
# client.devices.labels         # add/remove/get tags for device assets
# client.devices.saved_queries  # CRUD for saved queries for device assets
# client.enforcements           # CRUD for enforcements
# client.instances              # get instances and instance meta data
# client.meta                   # get product meta data
# client.remote_support         # enable/disable remote support settings
# client.settings_global        # get/update global system settings
# client.settings_gui           # get/update gui system settings
# client.settings_ip            # get/update identity provider system settings
# client.settings_lifecycle     # get/update lifecycle system settings
# client.signup                 # perform initial signup and use password reset tokens
# client.system_roles           # CRUD for system roles
# client.system_users           # CRUD for system users
# client.users                  # get user assets
# client.users.fields           # get field schemas for user assets
# client.users.labels           # add/remove/get tags for user assets
# client.users.saved_queries    # CRUD for saved queries for user assets


def get_agg_raw_data():
    """Workflow for getting aggregated raw data."""
    # -- enable the feature via OS environment variables:
    os.environ["AX_FEATURES"] = "raw_data"
    # -- OR enable it by force:
    axonapi.features.Features.raw_data.force = True
    # -- get aggregated raw data
    fields = ["agg:raw_data"]
    assets = client.devices.get(fields=fields)
    return assets


def get_adapter_raw_data():
    """Workflow for getting adapter specific raw data."""
    # -- enable the feature via OS environment variables:
    os.environ["AX_FEATURES"] = "raw_data"
    # -- OR enable it by force:
    axonapi.features.Features.raw_data.force = True
    # -- get adapter specific raw data
    wiz_entries = "simple active_directory:id exists"
    fields = ["active_directory:raw_data"]
    assets = client.devices.get(fields=fields, wiz_entries=wiz_entries)
    return assets


def get_status():
    """Get the system status safely."""
    try:
        status = client.signup.system_status
        print(status)
        return status.is_ready
    except Exception as exc:
        print(f"API unreachable {exc}")
        return False


def wait_status():
    """Wait for the system status to be ready."""
    ready = get_status()
    while not ready:
        ready = get_status()
        time.sleep(30)


def do_reset():
    """Workflow for performing a factory reset."""
    wait_status()
    # -- enable the reset endpoint
    client.settings_global.configure_destroy(enabled=True, destroy=False, reset=True)
    # -- perform a reset
    client.instances.factory_reset(reset=True)
    # -- wait for the reset to finish
    wait_status()
