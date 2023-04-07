=====
Usage
=====


To develop on lastpassreportingcli:

.. code-block:: bash

    # The following commands require pipenv as a dependency

    # To lint the project
    _CI/scripts/lint.py

    # To execute the testing
    _CI/scripts/test.py

    # To create a graph of the package and dependency tree
    _CI/scripts/graph.py

    # To build a package of the project under the directory "dist/"
    _CI/scripts/build.py

    # To see the package version
    _CI/scripts/tag.py

    # To bump semantic versioning [--major|--minor|--patch]
    _CI/scripts/tag.py --major|--minor|--patch

    # To upload the project to a pypi repo if user and password are properly provided
    _CI/scripts/upload.py

    # To build the documentation of the project
    _CI/scripts/document.py


To use lastpassreportingcli:

.. code-block:: bash

    lastpass-report --help
    usage: lastpass-report [-h] [--log-config LOGGER_CONFIG] [--log-level {debug,info,warning,error,critical}]
                           [--username USERNAME] [--password PASSWORD] [--mfa MFA]
                           [--warning-whitelist WARNING_WHITELIST]
                           {report,export} ...

    A tool to report on state of secret rotation based on a cutoff day, by default the incident of lastpass day.

    positional arguments:
      {report,export}       Supported functions for this program.
        report              Arguments for reporting on the current state of secret rotation.
        export              Arguments for export all secret rotation state for processing.

    optional arguments:
      -h, --help            show this help message and exit
      --log-config LOGGER_CONFIG, -l LOGGER_CONFIG
                            The location of the logging config json file
      --log-level {debug,info,warning,error,critical}, -L {debug,info,warning,error,critical}
                            Provide the log level. Defaults to info.
      --username USERNAME, -u USERNAME
                            The username of the user we are connecting to lastpass as. Environment variable
                            "LASTPASS_USERNAME" can be set. If environment variable is not set and argument not provided
                            value will be interactively requested by the user.
      --password PASSWORD, -p PASSWORD
                            The password of the user we are connecting to lastpass as. Environment variable
                            "LASTPASS_PASSWORD" can be set. If environment variable is not set and argument not provided
                            value will be interactively requested by the user.
      --mfa MFA, -m MFA     The MFA of the user we are connecting to lastpass as. Environment variable "LASTPASS_MFA"
                            can be set. If environment variable is not set and argument not provided value will be
                            interactively requested by the user.
      --warning-whitelist WARNING_WHITELIST, -w WARNING_WHITELIST
                            A comma delimited list of secret IDs that will be disregarded from the reports. Environment
                            variable "LASTPASS_WARNING_WHITELIST" can be set.

.. code-block:: bash

    lastpass-report report --help
    usage: lastpass-report report [-h] [--report-on {all,personal,shared}] [--sort-on {name,percentage}]
                                  [--reverse-sort] [--details] [--filter-folders FILTER_FOLDERS]

    optional arguments:
      -h, --help            show this help message and exit
      --report-on {all,personal,shared}, -r {all,personal,shared}
                            Which categories of secrets to report on, personal, shared or all. Default is all.
                            Environment variable "LASTPASS_REPORT_ON" can be used to set this.
      --sort-on {name,percentage}, -s {name,percentage}
                            Sorts the report data based on either folder name or percentage done.Defaults to folder
                            Environment variable "LASTPASS_SORT_ON" can be used to set this.
      --reverse-sort, -rs   Changes the sorting order on the key chosen.Environment variable "LASTPASS_SORT_REVERSE" can
                            be used to set this.
      --details, -d         Shows a detailed view of the folder report.Environment variable "LASTPASS_REPORT_DETAIL" can
                            be used to set this.
      --filter-folders FILTER_FOLDERS, -f FILTER_FOLDERS
                            Filters based on comma delimited folder names.Environment variable
                            "LASTPASS_REPORT_FILTER_FOLDERS" can be used to set this.

.. code-block:: bash

    lastpass-report export --help
    usage: lastpass-report export [-h] --filename FILENAME

    optional arguments:
      -h, --help            show this help message and exit
      --filename FILENAME, -f FILENAME
                            The filename to export the secret status report on.Environment variable
                            "LASTPASS_EXPORT_FILENAME" can be used to set this.
