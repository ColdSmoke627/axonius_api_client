# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.assets."""
import copy
import datetime
import json

import pytest
from axonius_api_client.api import json_api
from axonius_api_client.constants.api import GUI_PAGE_SIZES
from axonius_api_client.constants.general import SIMPLE
from axonius_api_client.exceptions import (
    AlreadyExists,
    ApiAttributeTypeError,
    ApiError,
    GuiQueryWizardWarning,
    SavedQueryNotFoundError,
)

from ...utils import get_schema, random_string


class FixtureData:

    name = "badwolf torked"
    fields = [
        "adapters",
        "last_seen",
        "id",
    ]
    sort_desc = False
    gui_page_size = GUI_PAGE_SIZES[-1]
    tags = ["badwolf1", "badwolf2"]
    description = "badwolf torked"
    query = 'not ("specific_data.data.last_seen" >= date("NOW - 1d"))'
    wiz_name = "badwolf torked wiz"
    wiz_entries = "simple !last_seen last_days 1"


class SavedQueryPrivate:
    def test_get(self, apiobj):
        result = apiobj.saved_query._get()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, json_api.saved_queries.SavedQuery)
            validate_sq(item.to_dict())

    def test_add(self, apiobj):
        name = "badwolfvvv"
        view = {
            "query": {
                "filter": "",
                "expressions": [],
                "search": None,
                "meta": {"enforcementFilter": None, "uniqueAdapters": False},
            },
            "sort": {"desc": True, "field": ""},
            "fields": [
                "adapters",
                "labels",
            ],
            "pageSize": 20,
        }

        try:
            apiobj.saved_query.delete_by_name(value=name)
        except Exception:
            pass

        result = apiobj.saved_query._add(name=name, view=view)
        assert isinstance(result, json_api.saved_queries.SavedQuery)
        assert result.name == name
        assert result.view == view
        assert result.fields == view["fields"]

        result.set_name(value="xxx")
        assert result.name == "xxx"

        with pytest.raises(ApiAttributeTypeError):
            result.set_name("")

        with pytest.raises(ApiAttributeTypeError):
            result.set_name(1111)

        with pytest.raises(ApiAttributeTypeError):
            result.set_description(1111)

        with pytest.raises(ApiAttributeTypeError):
            result.set_tags(1111)

        with pytest.raises(ApiAttributeTypeError):
            result.sort_field = 1111

        with pytest.raises(ApiAttributeTypeError):
            result.fields = 1111

        with pytest.raises(ApiAttributeTypeError):
            result.reindex_expressions(["x"])

        with pytest.raises(ApiAttributeTypeError):
            result.expressions = ["x"]

        table = result.to_tablize()
        assert isinstance(table, dict)

        try:
            apiobj.saved_query.delete_by_name(value=name)
        except Exception:
            pass


class SavedQueryPublic:
    def test__check_name_exists(self, apiobj, sq_fixture):
        with pytest.raises(AlreadyExists):
            apiobj.saved_query._check_name_exists(value=sq_fixture["name"])

    def test__check_asset_scope_enabled(self, apiobj):
        assert apiobj.saved_query._check_asset_scope_enabled(value=False) is None
        flags = apiobj.instances._feature_flags()
        if not flags.asset_scopes_enabled:
            with pytest.raises(ApiError):
                apiobj.saved_query._check_asset_scope_enabled(value=True)
        else:
            assert apiobj.saved_query._check_asset_scope_enabled(value=True) is None

    def test_get_no_generator(self, apiobj):
        rows = apiobj.saved_query.get(generator=False)
        assert not rows.__class__.__name__ == "generator"
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_generator(self, apiobj):
        gen = apiobj.saved_query.get(generator=True)
        assert gen.__class__.__name__ == "generator"
        assert not isinstance(gen, list)

        rows = [x for x in gen]
        for row in rows:
            assert isinstance(row, dict)
            validate_sq(row)

    def test_get_tags(self, apiobj):
        tags = apiobj.saved_query.get_tags()
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)

    def test_get_by_name(self, apiobj):
        sq = apiobj.saved_query.get()[0]
        value = sq["name"]
        row = apiobj.saved_query.get_by_name(value=value)
        assert isinstance(row, dict)
        assert row["name"] == value

    def test_get_by_name_error(self, apiobj):
        value = "badwolf_yyyyyyyyyyyy"
        with pytest.raises(SavedQueryNotFoundError):
            apiobj.saved_query.get_by_name(value=value)

    def test_get_by_uuid(self, apiobj):
        sq = apiobj.saved_query.get()[0]
        value = sq["uuid"]
        row = apiobj.saved_query.get_by_uuid(value=value)
        assert isinstance(row, dict)
        assert row["uuid"] == value

    def test_get_by_uuid_error(self, apiobj):
        value = "badwolf_xxxxxxxxxxxxx"
        with pytest.raises(SavedQueryNotFoundError):
            apiobj.saved_query.get_by_uuid(value=value)

    def test_get_by_tags(self, apiobj):
        tags = [y for x in apiobj.saved_query.get() for y in x.get("tags", [])]
        value = tags[0]
        rows = apiobj.saved_query.get_by_tags(value=value)
        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, dict)
            assert value in row["tags"]

    def test_get_by_tags_error(self, apiobj):
        value = "badwolf_wwwwwwww"
        with pytest.raises(SavedQueryNotFoundError):
            apiobj.saved_query.get_by_tags(value=value)

    def test_update_name(self, apiobj, sq_fixture):
        add = random_string(6)
        old_value = sq_fixture["name"]
        new_value = f"{old_value} {add}"
        updated = apiobj.saved_query.update_name(sq=sq_fixture, value=new_value)
        assert updated["name"] == new_value

    def test_update_always_cached(self, apiobj, sq_fixture):
        old_value = sq_fixture["always_cached"]
        new_value = not old_value
        updated = apiobj.saved_query.update_always_cached(sq=sq_fixture, value=new_value)
        assert updated["always_cached"] == new_value

    def test_update_private(self, apiobj, sq_fixture):
        old_value = sq_fixture["private"]
        new_value = not old_value
        updated = apiobj.saved_query.update_private(sq=sq_fixture, value=new_value)
        assert updated["private"] == new_value

    def test_update_description(self, apiobj, sq_fixture):
        add = random_string(6)
        old_value = sq_fixture["description"]
        new_value = f"{old_value} {add}"
        updated = apiobj.saved_query.update_description(sq=sq_fixture, value=new_value)
        assert updated["description"] == new_value

    def test_update_page_size(self, apiobj, sq_fixture):
        new_value = GUI_PAGE_SIZES[0]
        updated = apiobj.saved_query.update_page_size(sq=sq_fixture, value=new_value)
        assert updated["view"]["pageSize"] == new_value

    def test_update_tags_badtype(self, apiobj):
        with pytest.raises(ApiError):
            apiobj.saved_query.update_tags(sq=None, value=1)

    def test_update_tags(self, apiobj, sq_fixture):
        value_set = ["badwolf1_set", "badwolf2_set", "badwolf3_set"]
        updated_set = apiobj.saved_query.update_tags(
            sq=sq_fixture, value=value_set, append=False, remove=False, as_dataclass=True
        )
        assert updated_set.tags == value_set

        value_remove = [value_set[0], "badwolf4_ignore"]
        value_remove_exp = value_set[1:]
        updated_remove = apiobj.saved_query.update_tags(
            sq=sq_fixture, value=value_remove, append=False, remove=True, as_dataclass=True
        )
        assert updated_remove.tags == value_remove_exp

        value_append = ["badwolf3_append"]
        value_append_exp = value_remove_exp + value_append
        updated_append = apiobj.saved_query.update_tags(
            sq=sq_fixture, value=value_append, append=True, remove=False, as_dataclass=True
        )
        assert updated_append.tags == value_append_exp

        updated_wipe = apiobj.saved_query.update_tags(
            sq=sq_fixture, value=[], append=False, remove=False, as_dataclass=True
        )
        assert updated_wipe.tags == []

    def test_update_fields(self, apiobj, sq_fixture):
        value_set = apiobj.fields_default
        updated_set = apiobj.saved_query.update_fields(
            sq=sq_fixture, fields=value_set, append=False, remove=False, as_dataclass=True
        )
        assert updated_set.fields == value_set

        value_remove = [apiobj.FIELD_LAST_SEEN]
        value_remove_exp = [x for x in value_set if x != apiobj.FIELD_LAST_SEEN]
        updated_remove = apiobj.saved_query.update_fields(
            sq=sq_fixture, fields=value_remove, append=False, remove=True, as_dataclass=True
        )
        assert updated_remove.fields == value_remove_exp

        value_append = value_remove
        value_append_exp = value_remove_exp + value_remove
        updated_append = apiobj.saved_query.update_fields(
            sq=sq_fixture, fields=value_append, append=True, remove=False, as_dataclass=True
        )
        assert updated_append.fields == value_append_exp

    def test_update_query_empty_expressions_append(self, apiobj, sq_fixture):
        wiz_entries = f"simple {apiobj.FIELD_SIMPLE} contains a"
        wiz_parsed = apiobj.get_wiz_entries(wiz_entries=wiz_entries)

        with pytest.warns(GuiQueryWizardWarning):
            apiobj.saved_query.update_query(sq=sq_fixture, query=wiz_parsed["query"], append=True)

    def test_update_query_empty_query_append(self, apiobj, sq_fixture):
        with pytest.raises(ApiError):
            apiobj.saved_query.update_query(sq=sq_fixture, query=None, append=True)

    def test_update_query(self, apiobj, sq_fixture):
        wiz_set_entries = f"simple {apiobj.FIELD_SIMPLE} contains a"
        wiz_set = apiobj.get_wiz_entries(wiz_entries=wiz_set_entries)
        with pytest.warns(GuiQueryWizardWarning):
            updated_set = apiobj.saved_query.update_query(
                sq=FixtureData.name,
                query=wiz_set["query"],
                append=False,
                append_and_flag=False,
                append_not_flag=False,
                as_dataclass=True,
            )
        assert updated_set.query == wiz_set["query"]
        assert updated_set.expressions == []

        updated_set_wiz = apiobj.saved_query.update_query(
            sq=FixtureData.name,
            wiz_entries=wiz_set_entries,
            append=False,
            append_and_flag=False,
            append_not_flag=False,
            as_dataclass=True,
        )
        assert updated_set_wiz.query == wiz_set["query"]
        assert updated_set_wiz.expressions == wiz_set["expressions"]

        wiz_append_entries = f"simple {apiobj.FIELD_SIMPLE} contains b"
        wiz_append = apiobj.get_wiz_entries(wiz_entries=wiz_append_entries)
        wiz_append_exp_query = f'{wiz_set["query"]} or {wiz_append["query"]}'
        updated_append = apiobj.saved_query.update_query(
            sq=FixtureData.name,
            wiz_entries=wiz_append_entries,
            append=True,
            append_and_flag=False,
            append_not_flag=False,
            as_dataclass=True,
        )
        assert updated_append.query == wiz_append_exp_query

        wiz_append_and_entries = f"simple {apiobj.FIELD_LAST_SEEN} last_days 30"
        wiz_append_and = apiobj.get_wiz_entries(wiz_entries=wiz_append_and_entries)
        wiz_append_and_exp_query = f"{wiz_append_exp_query} and {wiz_append_and['query']}"
        updated_append_and = apiobj.saved_query.update_query(
            sq=FixtureData.name,
            wiz_entries=wiz_append_and_entries,
            append=True,
            append_and_flag=True,
            append_not_flag=False,
            as_dataclass=True,
        )
        assert updated_append_and.query == wiz_append_and_exp_query

        wiz_append_and_not_entries = f"simple {apiobj.FIELD_LAST_SEEN} last_days 90"
        wiz_append_and_not = apiobj.get_wiz_entries(wiz_entries=wiz_append_and_not_entries)
        wiz_append_and_not_exp_query = (
            f"{wiz_append_and_exp_query} and not {wiz_append_and_not['query']}"
        )
        updated_append_and_not = apiobj.saved_query.update_query(
            sq=FixtureData.name,
            wiz_entries=wiz_append_and_not_entries,
            append=True,
            append_and_flag=True,
            append_not_flag=True,
            as_dataclass=True,
        )
        assert updated_append_and_not.query == wiz_append_and_not_exp_query

    def test_update_sort(self, apiobj, sq_fixture):
        field = "specific_data.data.last_seen"
        get_schema(apiobj=apiobj, field=field)

        updated = apiobj.saved_query.update_sort(sq=sq_fixture, field=field, descending=False)
        assert updated["view"]["sort"]["field"] == field
        assert updated["view"]["sort"]["desc"] is False

    def test_update_sort_empty(self, apiobj, sq_fixture):
        updated = apiobj.saved_query.update_sort(sq=sq_fixture, field="", descending=True)
        assert updated["view"]["sort"]["field"] == ""
        assert updated["view"]["sort"]["desc"] is True

    def test_update_copy(self, apiobj, sq_fixture):
        add = random_string(6)
        new_value = f"{FixtureData.name} {add}"
        updated = apiobj.saved_query.copy(
            sq=FixtureData.name, name=new_value, private=True, asset_scope=False, as_dataclass=True
        )
        assert updated.name == new_value
        assert updated.private is True
        apiobj.saved_query.delete_by_name(value=updated.name)

    def test_get_by_multi_not_found(self, apiobj, sq_fixture):
        with pytest.raises(SavedQueryNotFoundError):
            apiobj.saved_query.get_by_multi(sq="i do not exist, therefore i am not")

    def test_get_by_multi_bad_type(self, apiobj, sq_fixture):
        with pytest.raises(ApiError):
            apiobj.saved_query.get_by_multi(sq=222222222)

    def test_get_by_multi(self, apiobj, sq_fixture):
        sqs = apiobj.saved_query.get(as_dataclass=True)
        by_name_str = apiobj.saved_query.get_by_multi(
            sq=sq_fixture["name"], sqs=sqs, as_dataclass=True
        )
        assert by_name_str.uuid == sq_fixture["uuid"]

        by_uuid_str = apiobj.saved_query.get_by_multi(
            sq=sq_fixture["uuid"], sqs=sqs, as_dataclass=True
        )
        assert by_uuid_str.uuid == sq_fixture["uuid"]

        by_dict = apiobj.saved_query.get_by_multi(sq=sq_fixture, sqs=sqs, as_dataclass=True)
        assert by_dict.uuid == sq_fixture["uuid"]

        by_dataclass = apiobj.saved_query.get_by_multi(sq=by_dict, sqs=sqs, as_dataclass=True)
        assert by_dataclass.uuid == sq_fixture["uuid"]

    def test_delete_not_found(self, apiobj):
        with pytest.raises(SavedQueryNotFoundError):
            apiobj.saved_query.delete(rows="i do not exist, therefore i am not")

    def test_delete_not_found_no_errors(self, apiobj):
        ret = apiobj.saved_query.delete(rows="i do not exist, therefore i am not", errors=False)
        assert ret == []

    def test_delete(self, apiobj, sq_fixture_wiz):
        sq_fixture_wiz.document_meta = {}
        ret = apiobj.saved_query.delete(
            rows=[sq_fixture_wiz, sq_fixture_wiz.name], as_dataclass=True
        )
        for x in ret:
            x.document_meta = {}
        assert isinstance(ret, list) and len(ret) == 1
        assert ret[0] == sq_fixture_wiz

    @pytest.fixture(scope="function")
    def sq_fixture_wiz(self, apiobj):
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")

        try:
            apiobj.saved_query.delete_by_name(value=FixtureData.wiz_name)
        except SavedQueryNotFoundError:
            pass

        row = apiobj.saved_query.add(
            name=FixtureData.wiz_name,
            fields=FixtureData.fields + [apiobj.FIELD_SIMPLE],
            sort_field=apiobj.FIELD_SIMPLE,
            sort_descending=FixtureData.sort_desc,
            gui_page_size=FixtureData.gui_page_size,
            tags=FixtureData.tags,
            description=FixtureData.description,
            wiz_entries=FixtureData.wiz_entries,
            as_dataclass=True,
        )

        assert row.name == FixtureData.wiz_name
        assert row.tags == FixtureData.tags
        assert row.description == FixtureData.description
        assert row.private is False
        assert row.query == FixtureData.query
        assert row.query_expr == FixtureData.query
        assert row.expressions
        assert row.page_size == FixtureData.gui_page_size
        assert row.sort_field == apiobj.FIELD_SIMPLE
        assert row.sort_descending == FixtureData.sort_desc

        yield row

        try:
            apiobj.saved_query._delete(uuid=row.uuid)
        except Exception:
            pass

    @pytest.fixture(scope="function")
    def sq_fixture(self, apiobj):
        get_schema(apiobj=apiobj, field="specific_data.data.last_seen")

        try:
            apiobj.saved_query.delete_by_name(value=FixtureData.name)
        except SavedQueryNotFoundError:
            pass

        row = apiobj.saved_query.add(
            name=FixtureData.name,
            fields=FixtureData.fields + [apiobj.FIELD_SIMPLE],
            sort_field=apiobj.FIELD_SIMPLE,
            sort_descending=FixtureData.sort_desc,
            gui_page_size=FixtureData.gui_page_size,
            tags=FixtureData.tags,
            description=FixtureData.description,
            query=FixtureData.query,
        )

        uuid = row["uuid"]
        validate_sq(row)

        assert row["name"] == FixtureData.name
        assert row["query_type"] == "saved"
        assert row["tags"] == FixtureData.tags
        assert row["description"] == FixtureData.description
        assert row["private"] is False
        assert row["view"]["query"]["filter"] == FixtureData.query
        assert row["view"]["query"]["onlyExpressionsFilter"] == FixtureData.query
        assert row["view"]["query"]["expressions"] == []
        assert row["view"]["pageSize"] == FixtureData.gui_page_size
        assert row["view"]["sort"]["field"] == apiobj.FIELD_SIMPLE
        assert row["view"]["sort"]["desc"] == FixtureData.sort_desc

        yield row

        try:
            apiobj.saved_query._delete(uuid=uuid)
        except Exception:
            pass

    def test_add_remove(self, apiobj, sq_fixture):
        row = apiobj.saved_query.delete_by_name(value=sq_fixture["name"])
        assert isinstance(row, dict)
        assert row["uuid"] == sq_fixture["uuid"]

        with pytest.raises(SavedQueryNotFoundError):
            apiobj.saved_query.get_by_name(value=sq_fixture["name"])

    def test_add_error_no_fields(self, apiobj):
        name = "badwolf_nnnnnnnnnnnnn"
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields_default=False)

    def test_add_error_bad_sort_field(self, apiobj):
        name = "badwolf_sssssssssssss"
        fields = "last_seen"
        sort_field = "badwolf"
        with pytest.raises(ApiError):
            apiobj.saved_query.add(name=name, fields=fields, sort_field=sort_field)


class TestSavedQueryDevicesPrivate(SavedQueryPrivate):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestSavedQueryDevicesPublic(SavedQueryPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestSavedQueryUsersPrivate(SavedQueryPrivate):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users


class TestSavedQueryUsersPublic(SavedQueryPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users


def validate_qexpr(qexpr, asset):
    assert isinstance(qexpr, dict)

    compop = qexpr.pop("compOp")
    assert isinstance(compop, str)

    field = qexpr.pop("field")
    assert isinstance(field, str)

    idx = qexpr.pop("i", 0)
    assert isinstance(idx, int)

    leftbracket = qexpr.pop("leftBracket", 0)
    assert isinstance(leftbracket, (int, bool))

    rightbracket = qexpr.pop("rightBracket", 0)
    assert isinstance(rightbracket, (int, bool))

    logicop = qexpr.pop("logicOp")
    assert isinstance(logicop, str)

    notflag = qexpr.pop("not")
    assert isinstance(notflag, bool)

    value = qexpr.pop("value")
    assert isinstance(value, SIMPLE) or value is None

    obj = qexpr.pop("obj", False)
    assert isinstance(obj, bool)

    nesteds = qexpr.pop("nested", [])
    assert isinstance(nesteds, list)

    fieldtype = qexpr.pop("fieldType", "")
    assert isinstance(fieldtype, str)

    children = qexpr.pop("children", [])  # new in 2.15
    assert isinstance(children, list)  # new in 2.15

    filtered_adapters = qexpr.pop("filteredAdapters", {})
    assert isinstance(filtered_adapters, dict) or filtered_adapters is None

    context = qexpr.pop("context", "")  # new in 2.15
    assert isinstance(context, str)

    timestamp = qexpr.pop("timestamp", "")
    assert isinstance(timestamp, str)

    brackweight = qexpr.pop("bracketWeight", 0)
    assert isinstance(brackweight, int)

    qfilter = qexpr.pop("filter", "")
    assert isinstance(qfilter, str)

    # 4.5 2022/02/25
    module = qexpr.pop("module", "")
    assert isinstance(module, str)

    for nested in nesteds:
        validate_nested(nested, asset)

    for child in children:
        validate_nested(child, asset)

    assert not qexpr, list(qexpr)


def validate_nested(nested, asset):
    assert isinstance(nested, dict)

    nfiltered_adapters = nested.pop("filteredAdapters", {})
    assert isinstance(nfiltered_adapters, dict) or nfiltered_adapters is None

    ncondition = nested.pop("condition")
    assert isinstance(ncondition, str)

    nexpr = nested.pop("expression")
    assert isinstance(nexpr, dict)

    nidx = nested.pop("i")
    assert isinstance(nidx, int)

    assert not nested, list(nested)


def validate_sq(asset):
    asset = copy.deepcopy(asset)
    assert isinstance(asset, dict)

    original = copy.deepcopy(asset)
    assert original == asset

    assert asset["query_type"] in ["saved"]

    date_fetched = asset.pop("date_fetched")
    assert isinstance(date_fetched, str)

    last_updated = asset.pop("last_updated", None)
    assert isinstance(last_updated, (str, datetime.datetime, type(None)))

    name = asset.pop("name")
    assert isinstance(name, str)

    query_type = asset.pop("query_type")
    assert isinstance(query_type, str)

    user_id = asset.pop("user_id")
    assert isinstance(user_id, str)

    uuid = asset.pop("uuid")
    assert isinstance(uuid, str)

    description = asset.pop("description")
    assert isinstance(description, str) or description is None

    timestamp = asset.pop("timestamp", "")
    assert isinstance(timestamp, (str, type(None)))

    archived = asset.pop("archived", False)  # added in 2.15
    assert isinstance(archived, bool)

    updated_by_str = asset.pop("updated_by")
    assert isinstance(updated_by_str, str)

    updated_by = json.loads(updated_by_str)
    assert isinstance(updated_by, dict)

    updated_by_deleted = updated_by.pop("deleted")
    assert isinstance(updated_by_deleted, bool)

    # 4.5
    updated_by_is_first_login = updated_by.pop("is_first_login", False)
    assert isinstance(updated_by_is_first_login, bool)

    # 4.5
    updated_by_permanent = updated_by.pop("permanent", False)
    assert isinstance(updated_by_permanent, bool)

    updated_str_keys_req = [
        "first_name",
        "last_name",
        "source",
        "user_name",
    ]
    for updated_str_key in updated_str_keys_req:
        val = updated_by.pop(updated_str_key)
        assert isinstance(val, (str, int, float)) or val is None

    updated_str_keys_opt = [
        "_id",
        "last_updated",
        "password",
        "pic_name",
        "role_id",
        "salt",
    ]
    for updated_str_key in updated_str_keys_opt:
        val = updated_by.pop(updated_str_key, None)
        assert isinstance(val, (str, int, float)) or val is None

    assert not updated_by

    tags = asset.pop("tags", [])
    assert isinstance(tags, list)
    for tag in tags:
        assert isinstance(tag, str)

    predefined = asset.pop("predefined", False)
    assert isinstance(predefined, bool)

    private = asset.pop("private", False)
    assert isinstance(private, bool)

    view = asset.pop("view")
    assert isinstance(view, dict)

    colsizes = view.pop("coloumnSizes", [])
    assert isinstance(colsizes, list)

    for x in colsizes:
        assert isinstance(x, int)

    page = view.pop("page", 0)
    assert isinstance(page, int)

    pagesize = view.pop("pageSize", 0)
    assert isinstance(pagesize, int)

    # in 4.6 SQ 'New devices seen in the last day' has no sort key
    if "sort" in view:
        sort = view.pop("sort")
        assert isinstance(sort, dict)

        sort_desc = sort.pop("desc")
        assert isinstance(sort_desc, bool)

        sort_field = sort.pop("field")
        assert isinstance(sort_field, str)
        assert not sort

    # in 4.6 SQ 'New devices seen in the last day' has no fields key
    if "fields" in view:
        fields = view.pop("fields")
        assert isinstance(fields, list)

        for x in fields:
            assert isinstance(x, str)

    query = view.pop("query")
    assert isinstance(query, dict)

    """ changed in 4.5
    colfilters = view.pop("colFilters", {})
    assert isinstance(colfilters, dict)
    for k, v in colfilters.items():
        assert isinstance(k, str)
        assert isinstance(v, str)
    """

    # 4.5
    """ structure:
    [
        {
            "columnFilter": {
                "aqlExpression": '("specific_data.data.name" == ' 'regexMatch("a", "i"))',
                "arrayFields": [],
                "complexNestedFields": [],
                "complexParentToUnwind": None,
                "fieldPath": "specific_data.data.name",
                "fieldType": "string",
                "filterExpressions": [
                    {
                        "bracketWeight": 0,
                        "children": [],
                        "compOp": "columnFilterContains",
                        "field": "specific_data.data.name",
                        "fieldType": "axonius",
                        "filter": '("specific_data.data.name" ' '== regexMatch("a", "i"))',
                        "leftBracket": 0,
                        "logicOp": "",
                        "not": False,
                        "rightBracket": 0,
                        "value": "a",
                    }
                ],
                "isComplexField": False,
                "isComplexNestedField": False,
                "nestedFilteredFields": [],
            },
            "fieldPath": "specific_data.data.name",
        }
    ]
    """
    colfilters = view.pop("colFilters", [])
    assert isinstance(colfilters, list)
    for colfilter in colfilters:
        assert isinstance(colfilter, dict)

    qfilter = query.pop("filter")
    assert isinstance(qfilter, str) or qfilter is None

    qexprs = query.pop("expressions", [])
    assert isinstance(qexprs, list)

    qmeta = query.pop("meta", {})
    assert isinstance(qmeta, dict)

    qonlyexprfilter = query.pop("onlyExpressionsFilter", "")
    assert isinstance(qonlyexprfilter, str)

    qsearch = query.pop("search", None)
    assert qsearch is None or isinstance(qsearch, str)

    historical = view.pop("historical", None)
    assert historical is None or isinstance(historical, SIMPLE)

    """ changed in 4.5
    # 3.6+
    excluded_adapters = view.pop("colExcludedAdapters", {})
    assert isinstance(excluded_adapters, dict)
    """
    # 4.5
    """ structure
    [{"exclude": ["chef_adapter"], "fieldPath": "specific_data.data.name"}]
    """
    excluded_adapters = view.pop("colExcludedAdapters", [])
    assert isinstance(excluded_adapters, list)
    for excluded_adapter in excluded_adapters:
        assert isinstance(excluded_adapter, dict)

    # 4.0
    always_cached = asset.pop("always_cached")
    assert isinstance(always_cached, bool)
    asset_scope = asset.pop("asset_scope")
    assert isinstance(asset_scope, bool)
    is_asset_scope_query_ready = asset.pop("is_asset_scope_query_ready")
    assert isinstance(is_asset_scope_query_ready, bool)
    is_referenced = asset.pop("is_referenced")
    assert isinstance(is_referenced, bool)
    _id = asset.pop("id")
    assert isinstance(_id, str) and _id

    for qexpr in qexprs:
        validate_qexpr(qexpr, asset)

    # 4.5: 2022/02/07
    assetConditionExpressions = view.pop("assetConditionExpressions", [])
    assert isinstance(assetConditionExpressions, list)
    assetExcludeAdapters = view.pop("assetExcludeAdapters", [])
    assert isinstance(assetExcludeAdapters, list)

    assert not query, list(query)
    assert not view, list(view)

    document_meta = asset.pop("document_meta", {})
    assert isinstance(document_meta, dict)

    assert not asset, list(asset)
