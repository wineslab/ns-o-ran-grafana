import os
import re
from setuptools import find_packages, setup


setup(
    name='statsd-telegraf',
    version='3.2.1-1',
    description='A fork of pystatsd package with Telegraf-compatible tag support.',
    long_description=open('README.rst').read(),
    author='Bernardas Ališauskas',
    author_email='bernardas.alisauskas@gmail.com',
    url='https://github.com/Granitosaurus/statsd-telegraf',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['README.rst']},
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
