#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    MaintenanceStatus,
    ModelError,
    WaitingStatus,
)


logger = logging.getLogger(__name__)

PEER = "galera"
MYSQL_PORT = 3306


class MariaDBGaleraOperatorCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self._stored.set_default(
            mysql_initialized=False,
            pebble_ready=False,
        )
        self.framework.observe(self.on.mysql_pebble_ready, self._on_pebble_ready)
        self._provide_mysql()
        self.container = self.unit.get_container(PEER)

    ##############################################
    #           CHARM HOOKS HANDLERS             #
    ##############################################
    def _on_pebble_ready(self, _):
        self._stored.pebble_ready = True
        self._update_peers()
        self._configure_pod()

    def _on_config_changed(self, _):
        """Set a new Juju pod specification"""
        self._update_peers()
        self._configure_pod()

    def _on_update_status(self, _):
        """Set status for all units
        Status may be
        - MySQL is not ready,
        - MySQL is not Initialized
        - Unit is active
        """

        if not self.mysql.is_ready():
            status_message = "MySQL not ready yet"
            self.unit.status = WaitingStatus(status_message)
            return

        if not self._is_mysql_initialized():
            status_message = "MySQL not initialized"
            self.unit.status = WaitingStatus(status_message)
            return

        self.unit.status = ActiveStatus()

    ##############################################
    #               PROPERTIES                   #
    ##############################################
    @property
    def mysql(self) -> MySQL:
        """Returns MySQL object"""
        peers_data = self.model.get_relation(PEER).data[self.app]
        mysql_config = {
            "app_name": self.model.app.name,
            "host": self.unit_ip,
            "port": MYSQL_PORT,
            "user_name": "root",
            "mysql_root_password": peers_data["mysql_root_password"],
        }
        return MySQL(mysql_config)

    @property
    def unit_ip(self) -> str:
        """Returns unit's IP"""
        if bind_address := self.model.get_binding(PEER).network.bind_address:
            return str(bind_address)
        return ""

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
