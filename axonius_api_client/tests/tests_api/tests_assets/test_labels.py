# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.assets."""
import pytest

from axonius_api_client.api import json_api


class LabelsPrivate:
    def test_private_get(self, apiobj):
        labels = apiobj.labels._get()
        assert isinstance(labels, list)
        for x in labels:
            assert isinstance(x, json_api.generic.StrValue)
            assert x.value

    def test_private_add_get_remove(self, apiobj):
        labels = ["badwolf1", "badwolf2"]

        # get a single asset to add a label to
        asset = apiobj.get(max_rows=1)[0]
        asset_id = asset["internal_axon_id"]

        # add the label to the asset
        add_label_result = apiobj.labels._add(labels=labels, ids=[asset_id])
        assert isinstance(add_label_result, json_api.generic.IntValue)
        assert add_label_result.value == 1

        # re-get the asset and check that it has the label
        assets_added = apiobj.get_by_values(values=labels, field="labels", fields="labels")
        assets_added_ids = [x["internal_axon_id"] for x in assets_added]
        assert asset_id in assets_added_ids

        # check the each label has been added
        for x in assets_added:
            for label in labels:
                assert label in x["labels"]

        # check that the label is in all the labels on the system
        all_labels_post_add = apiobj.labels._get()
        assert isinstance(all_labels_post_add, list)

        for label in all_labels_post_add:
            assert isinstance(label, json_api.generic.StrValue)
            assert label.value

        for label in labels:
            assert label in [x.value for x in all_labels_post_add]

        # remove the label from an asset
        remove_label_result = apiobj.labels._remove(labels=labels, ids=assets_added_ids)
        assert isinstance(remove_label_result, json_api.generic.IntValue)
        assert remove_label_result.value >= 1

        # re-get the asset and check that it has the label
        assets_removed = apiobj.get_by_values(values=labels, field="labels", fields="labels")
        assert not assets_removed

        # check that the label is not in all the labels on the system
        all_labels_post_remove = apiobj.labels._get()
        assert isinstance(all_labels_post_remove, list)

        for label in labels:
            assert label not in [x.value for x in all_labels_post_remove]


class LabelsPublic:
    def test_get(self, apiobj):
        fields = apiobj.labels.get()
        assert isinstance(fields, list)
        for x in fields:
            assert isinstance(x, str)

    def test_add_get_remove(self, apiobj):
        labels = ["badwolf1", "badwolf2"]

        # get a single asset to add a label to
        asset = apiobj.get(max_rows=1)[0]
        asset_id = asset["internal_axon_id"]

        # add the label to the asset
        add_label_result = apiobj.labels.add(labels=labels, rows=[asset])
        assert add_label_result == 1

        # re-get the asset and check that it has the label
        assets_added = apiobj.get_by_values(
            values=labels,
            field="labels",
            fields="labels",
        )
        assets_added_ids = [x["internal_axon_id"] for x in assets_added]
        assert asset_id in assets_added_ids

        # check the each label has been added
        for x in assets_added:
            for label in labels:
                assert label in x["labels"]

        # check that the label is in all the labels on the system
        all_labels_post_add = apiobj.labels.get()
        assert isinstance(all_labels_post_add, list)

        for label in all_labels_post_add:
            assert isinstance(label, str)

        for label in labels:
            assert label in all_labels_post_add

        # remove the label from an asset
        remove_label_result = apiobj.labels.remove(labels=labels, rows=assets_added)
        assert remove_label_result >= 1

        # re-get the asset and check that it has the label
        assets_removed = apiobj.get_by_values(values=labels, field="labels", fields="labels")
        assert not assets_removed

        # check that the label is not in all the labels on the system
        all_labels_post_remove = apiobj.labels.get()
        assert isinstance(all_labels_post_remove, list)

        for label in labels:
            assert label not in all_labels_post_remove


class TestLabelsDevicesPrivate(LabelsPrivate):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestLabelsUsersPrivate(LabelsPrivate):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users


class TestLabelsDevicesPublic(LabelsPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_devices):
        return api_devices


class TestLabelsUsersPublic(LabelsPublic):
    @pytest.fixture(scope="class")
    def apiobj(self, api_users):
        return api_users
