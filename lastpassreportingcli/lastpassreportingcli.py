#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: lastpassreportingcli.py
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
Main code for lastpassreportingcli.

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html

"""

import argparse
import csv
import json
import logging
import logging.config
import os
from datetime import datetime

import coloredlogs
from colorclass import Windows
from lastpasslib import Lastpass
from lastpasslib.datamodels import Folder
from lastpasslib.lastpasslibexceptions import UnknownUsername, InvalidPassword, InvalidMfa, MfaRequired
from terminaltables import SingleTable
from yaspin import yaspin

from lib.datamodels import FolderMetrics, PresentationFolder
from lib.validators import default_environment_variable, environment_variable_boolean, get_user_input_or_quit, \
    character_delimited_list_variable, validate_secret_ids

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
LOGGER_BASENAME = '''lastpassreportingcli'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())

REPORT_ON_CHOICES = ['all', 'personal', 'shared']
SORT_ON_CHOICES = ['name', 'percentage']


def get_arguments():
    """
    Gets us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description='''A tool to report on state of secret rotation based on a cutoff day,
        by default the incident of lastpass day.''')
    parser.add_argument('--log-config',
                        '-l',
                        action='store',
                        dest='logger_config',
                        help='The location of the logging config json file',
                        default='')
    parser.add_argument('--log-level',
                        '-L',
                        help='Provide the log level. Defaults to info.',
                        dest='log_level',
                        action=default_environment_variable('LASTPASS_LOG_LEVEL'),
                        default='info',
                        choices=['debug',
                                 'info',
                                 'warning',
                                 'error',
                                 'critical'])
    parser.add_argument('--username',
                        '-u',
                        action=default_environment_variable('LASTPASS_USERNAME'),
                        help='The username of the user we are connecting to lastpass as. Environment variable '
                             '"LASTPASS_USERNAME" can be set. If environment variable is not set and argument not '
                             'provided value will be interactively requested by the user.')
    parser.add_argument('--password',
                        '-p',
                        action=default_environment_variable('LASTPASS_PASSWORD'),
                        help='The password of the user we are connecting to lastpass as. Environment variable '
                             '"LASTPASS_PASSWORD" can be set. If environment variable is not set and argument not '
                             'provided value will be interactively requested by the user.')
    parser.add_argument('--mfa',
                        '-m',
                        action=default_environment_variable('LASTPASS_MFA'),
                        help='The MFA of the user we are connecting to lastpass as. Environment variable '
                             '"LASTPASS_MFA" can be set. If environment variable is not set and argument not '
                             'provided value will be interactively requested by the user.')
    parser.add_argument('--warning-whitelist',
                        '-w',
                        default=os.environ.get('LASTPASS_WARNING_WHITELIST', []),
                        type=character_delimited_list_variable,
                        help='A comma delimited list of secret IDs that will be disregarded from the reports. '
                             'Environment variable "LASTPASS_WARNING_WHITELIST" can be set.')
    subparsers = parser.add_subparsers(help='Supported functions for this program.')
    report = subparsers.add_parser('report', help='Arguments for reporting on the current state of secret rotation.')
    export = subparsers.add_parser('export', help='Arguments for export all secret rotation state for processing.')
    report.add_argument('--report-on',
                        '-r',
                        help='Which categories of secrets to report on, personal, shared or all. Default is all. '
                             'Environment variable "LASTPASS_REPORT_ON" can be used to set this.',
                        action=default_environment_variable('LASTPASS_REPORT_ON'),
                        default='all',
                        choices=REPORT_ON_CHOICES)
    report.add_argument('--sort-on',
                        '-s',
                        help='Sorts the report data based on either folder name or percentage done.Defaults to folder '
                             'Environment variable "LASTPASS_SORT_ON" can be used to set this.',
                        action=default_environment_variable('LASTPASS_SORT_ON'),
                        default='name',
                        choices=SORT_ON_CHOICES)
    report.add_argument('--reverse-sort',
                        '-rs',
                        help='Changes the sorting order on the key chosen.'
                             'Environment variable "LASTPASS_SORT_REVERSE" can be used to set this.',
                        action='store_true',
                        default=environment_variable_boolean(os.environ.get('LASTPASS_SORT_REVERSE', False)))
    export.add_argument('--filename',
                        '-f',
                        help='The filename to export the secret status report on.'
                             'Environment variable "LASTPASS_EXPORT_FILENAME" can be used to set this.',
                        action=default_environment_variable('LASTPASS_EXPORT_FILENAME'),
                        required=True)
    args = parser.parse_args()
    are_valid, warning_whitelist = validate_secret_ids(args.warning_whitelist)
    if not are_valid:
        parser.error(f'{warning_whitelist} are not valid ids.')
    if not any((all((hasattr(args, value) for value in ('report_on', 'sort_on', 'reverse_sort'))),
                all((hasattr(args, value) for value in ('filename',))))):
        parser.error('Please specify on of "report" or "export" as the first argument.')
    if all((hasattr(args, value) for value in ('report_on', 'sort_on', 'reverse_sort'))):
        if args.report_on not in REPORT_ON_CHOICES:
            parser.error(f'Only {REPORT_ON_CHOICES} are valid choices for "LASTPASS_REPORT_ON" variable.')
        if args.sort_on not in SORT_ON_CHOICES:
            parser.error(f'Only {SORT_ON_CHOICES} are valid choices for "LASTPASS_SORT_ON" variable.')
    return args


def setup_logging(level, config_file=None):
    """
    Sets up the logging.

    Needs the args to get the log level supplied

    Args:
        level: At which level do we log
        config_file: Configuration to use

    """
    # This will configure the logging, if the user has set a config file.
    # If there's no config file, logging will default to stdout.
    if config_file:
        # Get the config for the logger. Of course this needs exception
        # catching in case the file is not there and everything. Proper IO
        # handling is not shown here.
        try:
            with open(config_file, encoding='utf-8') as conf_file:
                configuration = json.loads(conf_file.read())
                # Configure the logger
                logging.config.dictConfig(configuration)
        except ValueError:
            print(f'File "{config_file}" is not valid json, cannot continue.')
            raise SystemExit(1) from None
    else:
        coloredlogs.install(level=level.upper())


def get_folder_metrics(secrets, folders, cutoff_date, warning_whitelist):
    shared_secrets = [secret for secret in secrets if secret.shared_folder]
    personal_secrets = [secret for secret in secrets if not secret.shared_folder]
    aggregate_root_folders = {folder.name: Folder(folder.name, folder.path, is_personal=folder.is_personal)
                              for folder in folders if folder.is_in_root}
    for secret in shared_secrets:
        aggregate_root_folders[secret.shared_folder.shared_name].add_secret(secret)
    aggregate_root_folders['\\'].add_secrets(personal_secrets)
    aggregate_metrics = [FolderMetrics(folder, cutoff_date, warning_whitelist)
                         for folder in aggregate_root_folders.values()]
    return aggregate_metrics


def final_report_data(folder_metrics):
    total_secrets = sum(folder.number_of_secrets for folder in folder_metrics)
    total_updated_secrets = sum(folder.number_of_updated_secrets for folder in folder_metrics)
    total_left_to_update = total_secrets - total_updated_secrets
    percent_done = total_updated_secrets / total_secrets * 100
    percent_left = 100 - percent_done
    return (f'There are {total_secrets} artifacts in {len(folder_metrics)} folders. '
            f'{total_updated_secrets} ({percent_done:0.2f}%) artifacts have been updated and {total_left_to_update} '
            f'({percent_left:0.2f}%) still need attention')


def create_report(folder_metrics, report_on, sort_on, reverse_sort):
    headers = ('Name', 'Percentage Done', '(Updated/Total) Still left', 'Warnings')

    def sort_criteria(secret):
        return secret.name if sort_on == 'name' else secret.percentage_done

    tables = ['personal', 'shared'] if report_on == 'all' else [report_on]
    output = []
    for table in tables:
        table_data = [headers]
        metrics_data = [folder for folder in folder_metrics
                        if (folder.is_personal if table == 'personal' else not folder.is_personal)]
        metrics_data.sort(key=sort_criteria, reverse=reverse_sort)
        data = [PresentationFolder(folder).presentation_row for folder in metrics_data]
        table_data.extend(data)
        result = SingleTable(table_data, title=f'Lastpass secret rotation progress - {table.title()}')
        result.inner_heading_row_border = False
        output.append(result)
    for entry in output:
        print()
        print(entry.table)
        print()
    metrics = folder_metrics if report_on == 'all' else metrics_data
    print(final_report_data(metrics))
    return True


def authenticate_lastpass(username, password, mfa):
    username = username or get_user_input_or_quit('username')
    password = password or get_user_input_or_quit('password', password=True)
    mfa = mfa or get_user_input_or_quit('MFA')
    error_title = '{} is not correct, please try again.'
    authenticated = False
    while not authenticated:
        try:
            lastpass = Lastpass(username, password, mfa)
            authenticated = True
        except UnknownUsername:
            username = get_user_input_or_quit('username',
                                              title=error_title.format('Username'))
        except InvalidPassword:
            password = get_user_input_or_quit('password',
                                              password=True,
                                              title=error_title.format('Password'))
        except (InvalidMfa, MfaRequired):
            mfa = get_user_input_or_quit('MFA', title=error_title.format('MFA'))
        except Exception as exc:
            LOGGER.debug(exc)
            raise SystemExit('Unable to authenticate to backend.') from None
    return lastpass


def export_secret_state(lastpass, filename, cutoff_date, warning_whitelist):
    headers = ('full_path', 'id', 'name', 'url', 'username', 'last_modified', 'last_touched', 'last_password_modified',
               'status', 'warning')
    rows = []
    for folder in lastpass.folders:
        for secret in folder.secrets:
            rows.append((folder.full_path,
                         secret.id,
                         secret.name,
                         secret.url,
                         secret.username if hasattr(secret, 'username') else secret.type,
                         secret.last_modified_datetime,
                         secret.last_touch_datetime,
                         secret.last_password_change_datetime,
                         'NOT_OK' if secret.secret_updated_datetime < cutoff_date else 'OK',
                         FolderMetrics.check_if_is_secret_in_warning(secret,
                                                                     cutoff_date,
                                                                     warning_whitelist)))
    with open(filename, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', dialect=csv.excel)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
    raise SystemExit(f'Exported secret data to {filename}.')


def main():
    """
    Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    args = get_arguments()
    print(args)
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
    all_folder_metrics = get_folder_metrics(lastpass.get_secrets(),
                                            lastpass.folders,
                                            cutoff_date,
                                            args.warning_whitelist)
    return create_report(all_folder_metrics, args.report_on, args.sort_on, args.reverse_sort)


if __name__ == '__main__':
    raise SystemExit(main())
