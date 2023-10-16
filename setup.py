#!/usr/bin/env python
import poco
import sys
import platform
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

requires = ['PyYAML==6.0.1', 'pyaml==21.10.1', 'gitpython==3.1.30', 'svn==1.0.1', 'docopt==0.6.2',
            'pygithub==1.55', 'python-gitlab==3.9.0', 'packaging==21.3']
test_requires = ['pytest==7.1.3', 'pytest-cov==3.0.0']

# MacOS
if platform.system() == "Darwin" and sys.version_info[0] == 3:
    requires.append("certifi>=2022.9.14")
    requires.append("Scrapy>=2.6.2")


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
      'console_scripts': ['poco=poco.poco:main']
    },
    license="Apache License 2.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)

setup(**setup_options)
