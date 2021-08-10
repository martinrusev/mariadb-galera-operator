# Copyright 2020 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from ops.testing import Harness
from ops.model import (
    ActiveStatus,
    WaitingStatus,
)
from charm import MariaDBGaleraOperatorCharm
from unittest.mock import patch


class TestCharm(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = Harness(MariaDBGaleraOperatorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.harness.add_oci_resource("galera-image")

    def test_pebble_layer_is_dict(self):
        self.harness.set_leader(True)
        config = {}
        relation_id = self.harness.add_relation("galera", "galera")
        self.harness.add_relation_unit(relation_id, "galera/1")
        self.harness.update_config(config)
        layer = self.harness.charm._build_pebble_layer()
        self.assertIsInstance(layer["services"]["galera"], dict)

    def test_pebble_layer_with_custom_config(self):
        self.harness.set_leader(True)
        config = {
            "mysql_root_password": "PASS!",
            "mysql_user": "RandomUser",
            "mysql_password": "MYSQLPASS!",
            "mysql_database": "db_galera",
        }
        relation_id = self.harness.add_relation("galera", "galera")
        self.harness.add_relation_unit(relation_id, "galera/1")
        self.harness.update_config(config)
        env = self.harness.charm._build_pebble_layer()["services"]["galera"][
            "environment"
        ]
        self.assertEqual(env["MYSQL_ROOT_PASSWORD"], config["mysql_root_password"])
        self.assertEqual(env["MYSQL_USER"], config["mysql_user"])
        self.assertEqual(env["MYSQL_PASSWORD"], config["mysql_password"])
        self.assertEqual(env["MYSQL_DATABASE"], config["mysql_database"])
