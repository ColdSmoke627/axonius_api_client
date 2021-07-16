# -*- coding: utf-8 -*-
"""API for working with dashboards and discovery lifecycle."""
from .. import json_api
from ..api_endpoints import ApiEndpoints
from ..models import ApiModel


class Dashboard(ApiModel):
    """API for working with dashboards and discovery lifecycle.

    Examples:
        * Get discover lifecycle metadata: :meth:`get`
        * See if a lifecycle is currently running: :meth:`is_running`
        * Start a discover lifecycle: :meth:`start`
        * Stop a discover lifecycle: :meth:`stop`

    """

    def get(self) -> json_api.dashboard.DiscoverData:
        """Get lifecycle metadata.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.get()
            >>> data.next_run_starts_in_minutes
            551
            >>> data.is_running
            False
        """
        return json_api.dashboard.DiscoverData(
            raw=self._get().to_dict(), adapters=self.CLIENT.adapters.get(get_clients=False)
        )

    @property
    def is_running(self) -> bool:
        """Check if discovery cycle is running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.is_running
            False
        """
        return self.get().is_running

    def start(self) -> json_api.dashboard.DiscoverData:
        """Start a discovery cycle if one is not running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.start()
            >>> data.is_running
            True
            >>> j(data['phases_pending'])
            [
              "Fetch_Devices",
              "Fetch_Scanners",
              "Clean_Devices",
              "Pre_Correlation",
              "Run_Correlations",
              "Post_Correlation",
              "Run_Queries",
              "Save_Historical"
            ]
            >>> j(data['phases_done'])
            []

        """
        if not self.is_running:
            self._start()
        return self.get()

    def stop(self) -> json_api.dashboard.DiscoverData:
        """Stop a discovery cycle if one is running.

        Examples:
            Create a ``client`` using :obj:`axonius_api_client.connect.Connect`

            >>> data = client.dashboard.start()
            >>> data.is_running
            True
        """
        if self.is_running:
            self._stop()
        return self.get()

    def _get(self) -> json_api.dashboard.Lifecycle:
        """Direct API method to get discovery cycle metadata."""
        api_endpoint = ApiEndpoints.dashboard.get
        return api_endpoint.perform_request(client=self.CLIENT)

    def _start(self) -> str:
        """Direct API method to start a discovery cycle."""
        api_endpoint = ApiEndpoints.dashboard.start
        return api_endpoint.perform_request(client=self.CLIENT)

    def _stop(self) -> str:
        """Direct API method to stop a discovery cycle."""
        api_endpoint = ApiEndpoints.dashboard.stop
        return api_endpoint.perform_request(client=self.CLIENT)
