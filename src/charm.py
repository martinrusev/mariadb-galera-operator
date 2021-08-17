#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

# from mariadbserver import MariaDB
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
        self.framework.observe(self.on.galera_pebble_ready, self._on_pebble_ready)

        self.container = self.unit.get_container(PEER)

    ##############################################
    #           CHARM HOOKS HANDLERS             #
    ##############################################
    def _on_pebble_ready(self, _):
        self._stored.pebble_ready = True
        # self._update_peers()
        self._configure_pod()

    def _on_config_changed(self, _):
        """Set a new Juju pod specification"""
        # self._update_peers()
        self._configure_pod()

    def _on_update_status(self, _):
        """Set status for all units
        Status may be
        - MariaDB is not ready,
        - MariaDB is not Initialized
        - Unit is active
        """

        if not self.mysql.is_ready():
            status_message = "MariaDB not ready yet"
            self.unit.status = WaitingStatus(status_message)
            return

        if not self._is_mysql_initialized():
            status_message = "MariaDB not initialized"
            self.unit.status = WaitingStatus(status_message)
            return

        self.unit.status = ActiveStatus()

    ##############################################
    #               PROPERTIES                   #
    ##############################################
    @property
    def unit_ip(self) -> str:
        """Returns unit's IP"""
        if bind_address := self.model.get_binding(PEER).network.bind_address:
            return str(bind_address)
        return ""

    ##############################################
    #             UTILITY METHODS                #
    ##############################################
    # def _update_peers(self):
    #     if self.unit.is_leader():
    #         peers_data = self.model.get_relation(PEER).data[self.app]

    #         if not peers_data.get("mysql_root_password"):
    #             peers_data["mysql_root_password"] = self._mysql_root_password()

    def _configure_pod(self):
        """Configure the Pebble layer for MariaDB."""
        if not self._stored.pebble_ready:
            msg = "Waiting for Pod startup to complete"
            logger.debug(msg)
            self.unit.status = MaintenanceStatus(msg)
            return False

        layer = self._build_pebble_layer()

        if not layer["services"][PEER]["environment"].get("MYSQL_ROOT_PASSWORD", False):
            msg = "Awaiting leader node to set mysql_root_password"
            logger.debug(msg)
            self.unit.status = MaintenanceStatus(msg)
            return False

        services = self.container.get_plan().to_dict().get("services", {})

        if (
            not services
            or services[PEER]["environment"] != layer["services"][PEER]["environment"]
        ):
            self.container.add_layer(PEER, layer, combine=True)
            self._restart_service()
            self.unit.status = ActiveStatus()
            return True

    def _build_pebble_layer(self):
        """Construct the pebble layer"""
        logger.debug("Building pebble layer")

        def env_config() -> dict:
            """Return the env_config for pebble layer"""
            config = self.model.config
            env_config = {
                "DEBUG": "True",
                "DB_GALERA_CLUSTER_BOOTSTRAP": "yes",
                "ALLOW_EMPTY_PASSWORD": "yes",
            }

            return env_config

        layer = {
            "summary": "MariaDB layer",
            "description": "Pebble layer configuration for MariaDB",
            "services": {
                PEER: {
                    "override": "replace",
                    "summary": "mariadb service",
                    "command": "/opt/canonical/mariadb-galera/scripts/entrypoint.sh",
                    "startup": "enabled",
                    "environment": env_config(),
                }
            },
        }

        return layer

    def _restart_service(self):
        """Restarts MariaDB Service"""
        try:
            service = self.container.get_service(PEER)
        except ConnectionError:
            logger.debug("Pebble API is not yet ready")
            return False
        except ModelError:
            logger.debug("MariaDB service is not yet ready")
            return False

        if service.is_running():
            self.container.stop(PEER)

        self.container.start(PEER)
        logger.debug("Restarted MariaDB service")
        self.unit.status = ActiveStatus()
        self._stored.mariadb_initialized = True

    def _is_mysql_initialized(self) -> bool:
        return self._stored.mariadb_initialized


if __name__ == "__main__":
    main(MariaDBGaleraOperatorCharm)
