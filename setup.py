#!/usr/bin/env python

from setuptools import setup

setup(
    name="Cowrie",
    description="Cowrie SSH/Telnet Honeypot.",
    author="Michel Oosterhof",
    author_email="michel@oosterhof.net",
    maintainer="Michel Oosterhof",
    maintainer_email="michel@oosterhof.net",
    keywords="ssh telnet honeypot",
    url="https://www.cowrie.org/",
    packages=['cowrie', 'twisted'],
    include_package_data=True,
    package_dir={'': 'src'},
    package_data={'': ['*.md']},
    use_incremental=True,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    scripts=[
        'bin/fsctl',
        'bin/asciinema',
        'bin/cowrie',
        'bin/createfs',
        'bin/playlog'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License'
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Security',
        ],
    setup_requires=[
        'incremental',
        'click'
    ],
    install_requires=[
        'twisted>=17.1.0',
        'cryptography>=0.9.1',
        'configparser',
        'pyopenssl',
        'pyparsing',
        'incremental',
        'packaging',
        'appdirs>=1.4.0',
        'python-dateutil',
        'service_identity>=14.0.0'
    ],
    extras_require={
        'csirtg': ['csirtgsdk>=0.0.0a17'],
        'dshield': ['requests'],
        'elasticsearch': ['pyes'],
        'mysql': ['mysqlclient'],
        'mongodb': ['pymongo'],
        'rethinkdblog': ['rethinkdb'],
        's3': ['botocore'],
        'slack': ['slackclient'],
        'splunklegacy': ['splunk-sdk'],
        'influxdb': ['influxdb']
    }
)
