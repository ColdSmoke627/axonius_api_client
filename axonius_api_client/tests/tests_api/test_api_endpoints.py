# -*- coding: utf-8 -*-
"""Test suite for """
from axonius_api_client.api import ApiEndpoints
from axonius_api_client.api.models import DataModel, DataSchema, DataSchemaJson
from axonius_api_client.tools import get_subcls


class TestApiEndpoints:
    def test_data_models_used(self):
        cls_all = get_subcls(DataModel)
        cls_used = ApiEndpoints.get_data_models_used()
        bases = [DataModel]

        for x in cls_all:
            if x not in cls_used and x not in bases:
                raise Exception(f"Unused DataModel: {x}")

    def test_data_schemeas_used(self):
        cls_all = get_subcls(DataSchema)
        cls_used = ApiEndpoints.get_data_schemas_used()
        bases = [DataSchema, DataSchemaJson]
        for x in cls_all:
            if x not in cls_used and x not in bases:
                raise Exception(f"Unused DataSchema: {x}")
