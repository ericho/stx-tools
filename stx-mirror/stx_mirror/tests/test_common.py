#
# SPDX-License-Identifier: Apache-2.0
#

import unittest
import logging

class StxTest(unittest.TestCase):
    """
    Base class for testing.

    Created to disable/enable logging on unittest runtime.
    """
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)
