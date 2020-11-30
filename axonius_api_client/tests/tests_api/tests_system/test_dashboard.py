# -*- coding: utf-8 -*-
"""Test suite."""
import datetime

import pytest
from axonius_api_client.api.system.dashboard import DiscoverData, DiscoverPhase


class DashboardBase:
    @pytest.fixture(scope="class")
    def apiobj(self, api_dashboard):
        return api_dashboard


class TestDashboardPrivate(DashboardBase):
    def test_private_lifecycle(self, apiobj):
        lifecycle = apiobj._get()
        assert isinstance(lifecycle, dict)
        assert "status" in lifecycle
        assert lifecycle["status"] in ["starting", "running", "done"]

    def test_private_start_stop(self, apiobj):
        stop = apiobj._stop()
        assert not stop

        lifecycle = apiobj._get()
        assert lifecycle["status"] in ["done", "stopping"]

        start = apiobj._start()
        assert not start

        lifecycle = apiobj._get()
        assert lifecycle["status"] in ["starting", "running"]

        re_stop = apiobj._stop()
        assert not re_stop

        lifecycle = apiobj._get()
        assert lifecycle["status"] in ["done", "stopping"]


class TestDashboardPublic(DashboardBase):
    def test_get(self, apiobj):
        data = apiobj.get()
        assert isinstance(data, DiscoverData)
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
            assert isinstance(phase, DiscoverPhase)
            assert phase.status in ["n/a", "done", "Pending", "running"]

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

    def test_is_running(self, apiobj):
        data = apiobj.is_running
        assert isinstance(data, bool)

    def test_start_stop(self, apiobj):
        if apiobj.is_running:
            stopped = apiobj.stop()
            assert isinstance(stopped, DiscoverData)
            assert not stopped.is_running
            # assert not stopped["status"] == "done"

        started = apiobj.start()
        assert isinstance(started, DiscoverData)
        assert started.is_running
        # assert started["status"] in ["starting", "running"]

        re_stopped = apiobj.stop()
        assert isinstance(re_stopped, DiscoverData)
        assert not re_stopped.is_running
        # assert re_stopped["status"] == "done"
