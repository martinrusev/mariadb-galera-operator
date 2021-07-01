#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class MariaDBGaleraOperatorCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.galera_pebble_ready, self._on_galera_pebble_ready)

    def _on_galera_pebble_ready(self, event):
        container = event.workload
        pebble_layer = {
            "summary": "galera layer",
            "description": "pebble config layer for galera",
            "services": {
                "galera": {
                    "override": "replace",
                    "summary": "galera",
                    "command": "......",
                    "startup": "enabled",
                    "environment": {},
                }
            },
        }

        container.add_layer("galera", pebble_layer, combine=True)
        container.autostart()
        self.unit.status = ActiveStatus()



if __name__ == "__main__":
    main(MariaDBGaleraOperatorCharm)
