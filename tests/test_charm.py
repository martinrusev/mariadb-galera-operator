# Copyright 2021 Minikube
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest
from unittest.mock import Mock

from charm import MariaDBGaleraOperatorCharm
from ops.model import ActiveStatus
from ops.testing import Harness


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(MariaDBGaleraOperatorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_httpbin_pebble_ready(self):
        # Check the initial Pebble plan is empty
        initial_plan = self.harness.get_container_pebble_plan("galera")
        self.assertEqual(initial_plan.to_yaml(), "{}\n")
        # Expected plan after Pebble ready with default config
        expected_plan = {
            "services": {
                "galera": {
                    "override": "replace",
                    "summary": "galera",
                    "command": ".....",
                    "startup": "enabled",
                    "environment": {},
                }
            },
        }
        # Get the httpbin container from the model
        container = self.harness.model.unit.get_container("galera")
        # Emit the PebbleReadyEvent carrying the httpbin container
        self.harness.charm.on.httpbin_pebble_ready.emit(container)
        # Get the plan now we've run PebbleReady
        updated_plan = self.harness.get_container_pebble_plan("galera").to_dict()
        # Check we've got the plan we expected
        self.assertEqual(expected_plan, updated_plan)
        # Check the service was started
        service = self.harness.model.unit.get_container("galera").get_service("galera")
        self.assertTrue(service.is_running())
        # Ensure we set an ActiveStatus with no message
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())
