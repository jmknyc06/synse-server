#!/usr/bin/env python
""" Synse Redfish Endpoint Tests

    Author: Morgan Morley Mills, based off IPMI tests by Erick Daniszewski
    Date:   02/06/2017

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest

from synse.tests.test_config import PREFIX
from synse.vapor_common import http


class RedfishScanAllTestCase(unittest.TestCase):
    """ Test scan all with the Redfish emulator running
    """
    def test_01_scan_all(self):
        """ Test the Synse scan all endpoint.
        """
        r = http.get(PREFIX + '/scan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('racks', response)

        racks = response['racks']
        self.assertIsInstance(racks, list)
        self.assertEqual(len(racks), 1)

        rack = racks[0]
        self.assertIsInstance(rack, dict)
        self.assertIn('rack_id', rack)
        self.assertEqual(rack['rack_id'], 'rack_1')
        self.assertIn('boards', rack)

        boards = rack['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '70000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['redfish-emulator'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['redfish-emulator'])
        self.assertIn('devices', board)

        devices = board['devices']
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), 11)

        device_types = [
            'power', 'system', 'led', 'voltage', 'fan_speed', 'temperature', 'power_supply'
        ]

        for device in devices:
            self.assertIsInstance(device, dict)
            self.assertIn('device_type', device)
            self.assertIn('device_id', device)

            dev_type = device['device_type']
            self.assertIn(dev_type.lower(), device_types)

    def test_02_scan_all(self):
        """ Test the Synse force scan endpoint.
        """
        r = http.get(PREFIX + '/scan/force')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('racks', response)

        racks = response['racks']
        self.assertIsInstance(racks, list)
        self.assertEqual(len(racks), 1)

        rack = racks[0]
        self.assertIsInstance(rack, dict)
        self.assertIn('rack_id', rack)
        self.assertEqual(rack['rack_id'], 'rack_1')
        self.assertIn('boards', rack)

        boards = rack['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '70000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['redfish-emulator'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['redfish-emulator'])
        self.assertIn('devices', board)

        devices = board['devices']
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), 11)

        device_types = [
            'power', 'system', 'led', 'voltage', 'fan_speed', 'temperature', 'power_supply'
        ]

        for device in devices:
            self.assertIsInstance(device, dict)
            self.assertIn('device_type', device)
            self.assertIn('device_id', device)

            dev_type = device['device_type']
            self.assertIn(dev_type.lower(), device_types)
