#!/usr/bin/env python
import poco
import sys
import platform
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

requires = ['pyaml==16.12.2', 'svn==0.3.44', 'gitpython>=2.1.8', 'docopt==0.6.2', 'docker-compose>=1.11.2',
            'pygithub==1.39', 'python-gitlab>=1.3.0']
test_requires = ['pytest==3.1.2', 'pytest-cov==2.5.1']

if sys.version_info[0] < 3:
    test_requires.append('SystemIO>=1.1')
    test_requires.append('mock')

if platform.system() == "Darwin" and sys.version_info[0] == 3:
    requires.append("certifi>=2017.4.17")
    requires.append("Scrapy >= 1.4.0")


class PyTestCommand(TestCommand):
    """ Command to run unit py.test unit tests
    """
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--verbose', '--cov', 'poco']
        self.test_suite = True

    def run(self):
        import pytest
        rcode = pytest.main(self.test_args)
        sys.exit(rcode)

setup_options = dict(
    name='poco',
    version=poco.__version__,
    description='poco lets you catalogue and manage your Docker projects using simple YAML files to shorten the route '
                'from finding your project to initialising it in your environment.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Shiwaforce.com',
    url='https://www.shiwaforce.com',
    packages=find_packages(exclude=['tests*']),
    package_data={'': ['poco.yml',
                       'docker-compose.yml',
                       'command-hierarchy.yml',
                       'config']},
    include_package_data=True,
    install_requires=requires,
    tests_require=test_requires,
    cmdclass={'test': PyTestCommand},
    entry_points={
      'console_scripts': ['poco=poco.poco:main'],
    },
    license="Apache License 2.0",
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
)

setup(**setup_options)
