#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: cli.py
#
# Copyright 2023 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for cli.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

import logging
import os
from datetime import datetime

from colorclass import Windows
from yaspin import yaspin

from lastpassreportingcli.lastpassreportingcli import (get_arguments,
                                                       setup_logging,
                                                       authenticate_lastpass,
                                                       export_secret_state,
                                                       get_folder_metrics,
                                                       create_report)

__author__ = '''Costas Tyfoxylos <ctyfoxylos@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''10-03-2023'''
__copyright__ = '''Copyright 2023, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<ctyfoxylos@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''cli'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def main():
    """
    Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    args = get_arguments()
    setup_logging(args.log_level, args.logger_config)
    os.system('CLS' if os.name == 'nt' else 'clear')
    Windows.enable(auto_colors=True, reset_atexit=True)  # Configures colors on Windows, does nothing if not on Windows.
    cutoff_date = datetime.fromisoformat('2022-09-22')
    lastpass = authenticate_lastpass(args.username, args.password, args.mfa)
    with yaspin(text='Please wait while retrieving and decrypting secrets from Lastpass...',
                color='yellow') as spinner:
        _ = lastpass.get_secrets()
    spinner.ok("✅")
    if hasattr(args, 'filename'):
        return export_secret_state(lastpass, args.filename, cutoff_date, args.warning_whitelist)
    folder_metrics = get_folder_metrics(lastpass.get_secrets(),
                                        lastpass.folders,
                                        cutoff_date,
                                        args.warning_whitelist,
                                        args.details,
                                        args.filter_folders)
    return create_report(folder_metrics, args.report_on, args.sort_on, args.reverse_sort)


if __name__ == '__main__':
    raise SystemExit(main())
