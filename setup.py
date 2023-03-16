#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

try:
    from pipenv.project import Project
    from pipenv.utils import convert_deps_to_pip

    pfile = Project().parsed_pipfile
    requirements = convert_deps_to_pip(pfile['packages'], r=False)
    test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)
except ImportError:
    # get the requirements from the requirements.txt
    requirements = [line.strip()
                    for line in open('requirements.txt').readlines()
                    if line.strip() and not line.startswith('#')]
    # get the test requirements from the test_requirements.txt
    test_requirements = [line.strip()
                         for line in
                         open('dev-requirements.txt').readlines()
                         if line.strip() and not line.startswith('#')]

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
version = open('.VERSION').read()

setup(
    name='''lastpassreportingcli''',
    version=version,
    description='''A tool to report on state of secret rotation based on a cutoff day, by default the incident of lastpass day.''',
    long_description=readme + '\n\n' + history,
    author='''Costas Tyfoxylos''',
    author_email='''ctyfoxylos@schubergphilis.com''',
    url='''https://github.com/schubergphilis/lastpassreportingcli''',
    packages=find_packages(where='.', exclude=('tests', 'hooks', '_CI*')),
    package_dir={'''lastpassreportingcli''':
                     '''lastpassreportingcli'''},
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    zip_safe=False,
    keywords='''lastpassreportingcli lastpass lastpasslib cutoff incident''',
    entry_points={
        'console_scripts': [
            # enable this to automatically generate a script in /usr/local/bin called myscript that points to your
            #  lastpassreportingcli.lastpassreportingcli:main method
            'lastpass-report = lastpass_report_cli:main'
        ]},
    scripts=['lastpass_report_cli.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.9',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
