#!/usr/bin/env python
from setuptools import setup
import glob

scripts = glob.glob("scripts/*")

setup(name='pycda',
      packages=['pycda'],
      version='0.1.0',
      description='Python Interface to the Chandra Data Archive',
      author='John ZuHone',
      author_email='jzuhone@gmail.com',
      url='http://github.com/jzuhone/pycda',
      download_url='https://github.com/jzuhone/pycda/tarball/0.1.0',
      install_requires=["requests","astropy"],
      scripts=scripts,
      classifiers=[
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Scientific/Engineering :: Visualization',
      ],
      )
