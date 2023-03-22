#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: datamodels.py
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

import json
import logging.config
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

from colorclass import Color
from lastpasslib.datamodels import Folder
from lastpasslib.secrets import Password, SecureNote

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
LOGGER_BASENAME = '''datamodels'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

ERROR_HIGH_PERCENTAGE = 99
ERROR_LOW_PERCENTAGE = 70


@dataclass
class WarningSecret:
    folder_name: str
    secret: Union[Password, SecureNote]

    @property
    def to_json(self):
        return json.dumps({'folder_name': self.folder_name,
                           'name': self.secret.name,
                           'url': self.secret.url,
                           'last_modified_datetime': str(self.secret.last_modified_datetime),
                           'secret_updated_datetime': str(self.secret.secret_updated_datetime),
                           'id': self.secret.id})

    def __str__(self):
        return f"{self.folder_name}: '{self.secret.name}' ({self.secret.url}) last modified " \
               f"'{self.secret.last_modified_datetime}', " \
               f"but secret field last modified '{self.secret.secret_updated_datetime}' (id:'{self.secret.id}')"


@dataclass
class FolderMetrics:
    folder: Folder
    cutoff_date: datetime
    warning_whitelist: list = field(default_factory=list)

    @property
    def name(self):
        return self.folder.name

    @property
    def path(self):
        return self.folder.path

    @property
    def full_path(self):
        return self.folder.full_path

    @property
    def is_in_root(self):
        return self.folder.is_in_root

    @property
    def is_personal(self):
        return self.folder.is_personal

    @property
    def warnings(self):
        return [WarningSecret(self.folder.name, secret) for secret in self.folder.secrets
                if self.is_secret_in_warning(secret)]

    @property
    def number_of_secrets(self):
        return len(self.folder.secrets)

    @property
    def number_of_updated_secrets(self):
        return len([secret for secret in self.folder.secrets if secret.last_modified_datetime > self.cutoff_date])

    @property
    def number_of_secrets_to_update(self):
        return self.number_of_secrets - self.number_of_updated_secrets

    @property
    def number_of_warnings(self):
        return len(self.warnings)

    @property
    def percentage_done(self):
        if self.number_of_secrets:
            percentage = round(self.number_of_updated_secrets / self.number_of_secrets * 100, 2) or 0
            return percentage if percentage < 100 else 100
        return 100

    @property
    def percentage_left(self):
        if self.number_of_secrets:
            percentage = round(100 - self.number_of_updated_secrets / self.number_of_secrets * 100, 2) or 0
            return percentage
        return 0

    def is_secret_in_warning(self, secret):
        return self.check_if_is_secret_in_warning(secret, self.cutoff_date, self.warning_whitelist)

    @staticmethod
    def check_if_is_secret_in_warning(secret, cutoff_date, warning_whitelist):
        if all([secret.last_modified_datetime != secret.secret_updated_datetime,
                secret.secret_updated_datetime < cutoff_date,
                secret.last_modified_datetime > cutoff_date,
                secret.type == 'Password' and secret.password != '',
                secret.id not in warning_whitelist]):
            return True
        return False

    @property
    def is_completed(self):
        return self.percentage_done == 100

    @property
    def is_in_progress(self):
        return self.percentage_done != 100

    @property
    def has_warnings(self):
        return self.number_of_warnings > 0

    @property
    def to_json(self):
        return json.dumps({'path': self.full_path,
                           'percentage_done': self.percentage_done,
                           'number_of_secrets': self.number_of_secrets,
                           'number_of_updated_secrets': self.number_of_updated_secrets,
                           'number_of_secrets_to_update': self.number_of_secrets_to_update,
                           'warnings': self.number_of_warnings})

    def __str__(self):
        return (f'{self.full_path} {self.percentage_done}% rotated. '
                f'({self.number_of_updated_secrets}/{self.number_of_secrets}) {self.number_of_secrets_to_update} left, '
                f'warnings: {self.number_of_warnings}')


@dataclass
class PresentationFolder:
    folder: FolderMetrics

    @property
    def name(self):
        return Color(f'{{blue}}{self.folder.full_path}{{/blue}}') if self.folder.is_in_root else self.folder.full_path

    @property
    def is_personal(self):
        return self.folder.is_personal

    @property
    def warning_color(self):
        return 'autoyellow' if self.folder.number_of_warnings else 'autogreen'

    @property
    def percentage_color(self):
        if self.folder.percentage_done == 100:
            return 'autogreen'
        condition = ERROR_LOW_PERCENTAGE <= self.folder.percentage_done <= ERROR_HIGH_PERCENTAGE
        return 'autoyellow' if condition else 'autored'

    @property
    def presentation_row(self):
        return (self.name,
                Color(f'{{{f"{self.percentage_color}"}}}{self.folder.percentage_done}{{{f"{self.percentage_color}"}}}'),
                f'({self.folder.number_of_updated_secrets}/{self.folder.number_of_secrets}) '
                f'{self.folder.number_of_secrets_to_update} left',
                Color(f'{{{f"{self.warning_color}"}}}{self.folder.number_of_warnings}{{{f"/{self.warning_color}"}}}'))
