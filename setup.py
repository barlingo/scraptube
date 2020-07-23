# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='scraptube',
    version='0.1.0',
    description='Tool to query, download and crop youtube videos.',
    long_description=readme,
    author='Barlingo',
    author_email='',
    url='https://github.com/barlingo/scraptube',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
