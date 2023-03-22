#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: validators.py
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
Main code for datamodels.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

import argparse
import logging
import os

from prompt_toolkit.shortcuts import input_dialog

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
LOGGER_BASENAME = '''validators'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def get_user_input_or_quit(variable_name, password=False, title=None):
    user_input = input_dialog(title=title if title else f'Lastpass {variable_name}',
                              text=f'Please type your lastpass {variable_name}:',
                              password=password).run()
    if not user_input:
        raise SystemExit(f'User canceled or provided an empty value for {variable_name}')
    return user_input


def comma_delimited_list_variable(value):
    """Support for environment variables with comma delimited lists of values."""
    return value.split(',')


def default_environment_variable(variable_name):
    """Closure to pass the variable name to the inline custom Action.

    Args:
        variable_name: The variable to look up as environment variable.

    Returns:
        The Action object.

    """

    class DefaultEnvVar(argparse.Action):
        """Default Environment Variable."""

        def __init__(self, *args, **kwargs):
            if variable_name in os.environ:
                kwargs['default'] = os.environ[variable_name]
            if kwargs.get('required') and kwargs.get('default'):
                kwargs['required'] = False
            super().__init__(*args, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values)

    return DefaultEnvVar


def environment_variable_boolean(value):
    """Parses an environment variable as a boolean.

    Args:
        value: The value of the environment variable.

    Returns:
        True if environment variable is one of the supported values, False otherwise.

    """
    if value in [True, 't', 'T', 'true', 'True', 1, '1', 'TRUE']:
        return True
    return False


def is_valid_secret_id(secret_id):
    try:
        int(secret_id)
    except ValueError:
        return False
    return 18 <= len(secret_id) <= 19


def validate_secret_ids(secret_ids):
    problematic_ids = [id_ for id_ in secret_ids if not is_valid_secret_id(id_)]
    if problematic_ids:
        return False, problematic_ids
    return True, secret_ids


def check_args_set(args, arguments):
    return all((hasattr(args, value) for value in arguments))
