# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

from axonius_api_client.api import json_api


class DashboardBase:
    """Pass."""


class TestDashboardPrivate(DashboardBase):
    def test_private_lifecycle(self, api_client):
        lifecycle = api_client.dashboard._get()
        assert isinstance(lifecycle, json_api.dashboard.Lifecycle)
        assert lifecycle.status in ["starting", "running", "done"]

    def test_private_start_stop(self, api_client):
        stop = api_client.dashboard._stop()
        assert isinstance(stop, str) and not stop

        lifecycle = api_client.dashboard._get()
        assert isinstance(lifecycle, json_api.dashboard.Lifecycle)
        assert lifecycle.status in ["done", "stopping"]

        start = api_client.dashboard._start()
        assert isinstance(start, str) and not start

        lifecycle = api_client.dashboard._get()
        assert isinstance(lifecycle, json_api.dashboard.Lifecycle)
        assert lifecycle.status in ["starting", "running"]

        re_stop = api_client.dashboard._stop()
        assert isinstance(re_stop, str) and not re_stop

        lifecycle = api_client.dashboard._get()
        assert isinstance(lifecycle, json_api.dashboard.Lifecycle)
        assert lifecycle.status in ["done", "stopping"]


class TestDashboardPublic(DashboardBase):
    def test_get(self, api_client):
        data = api_client.dashboard.get()
        assert isinstance(data, json_api.dashboard.DiscoverData)
        assert isinstance(data.is_running, bool)

        within_minutes = data.next_run_within_minutes(value="900000")
        assert within_minutes is True

        assert str(data)
        assert repr(data)

        str_progress = data.to_str_progress()
        assert isinstance(str_progress, list)
        for x in str_progress:
            assert isinstance(x, str)

        str_properties = data.to_str_properties()
        assert isinstance(str_properties, list)
        for x in str_properties:
            assert isinstance(x, str)

        str_phases = data.to_str_phases()
        assert isinstance(str_phases, list)
        for x in str_phases:
            assert isinstance(x, str)

        dict_data = data.to_dict()
        for x in data._properties:
            assert x in dict_data

        current_run_duration = data.current_run_duration_in_minutes
        assert isinstance(current_run_duration, (float, type(None)))

        assert isinstance(data.phases, list)
        for phase in data.phases:
            assert isinstance(phase, json_api.dashboard.DiscoverPhase)
            assert phase.status in ["n/a", "done", "pending", "running"]

            assert str(phase)
            assert repr(phase)

            str_props = phase.to_str_properties()
            assert isinstance(str_props, list)
            assert [isinstance(x, str) for x in str_props]

            str_progress = phase.to_str_progress()
            assert isinstance(str_progress, list)
            for x in str_progress:
                assert isinstance(x, str)

            dict_phase = phase.to_dict()
            assert isinstance(dict_phase, dict)

            assert isinstance(data.last_run_finish_date, (datetime.datetime, type(None)))
            assert isinstance(data.last_run_start_date, (datetime.datetime, type(None)))
            assert isinstance(data.current_run_duration_in_minutes, (float, type(None)))

            for x in phase._properties:
                assert x in dict_phase

            assert isinstance(phase.name, str)
            assert isinstance(phase.human_name, str)
            assert isinstance(phase.is_done, bool)
            assert isinstance(phase.progress, dict)
            assert isinstance(phase.name_map, dict)

    def test_is_running(self, api_client):
        data = api_client.dashboard.is_running
        assert isinstance(data, bool)

    def test_start_stop(self, api_client):
        if api_client.dashboard.is_running:
            stopped = api_client.dashboard.stop()
            assert isinstance(stopped, json_api.dashboard.DiscoverData)
            assert not stopped.is_running
            # assert not stopped["status"] == "done"

        started = api_client.dashboard.start()
        assert isinstance(started, json_api.dashboard.DiscoverData)
        assert started.is_running
        # assert started["status"] in ["starting", "running"]

        re_stopped = api_client.dashboard.stop()
        assert isinstance(re_stopped, json_api.dashboard.DiscoverData)
        assert not re_stopped.is_running
        # assert re_stopped["status"] == "done"
