#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup


setup(name="python-awd10",
      version='0.2.1',
      description='AWD10 controller module',
      url='https://github.com/RAA80/python-awd10',
      author='Alexey Ryadno',
      author_email='aryadno@mail.ru',
      license='MIT',
      packages=['awd10'],
      scripts=['scripts/awd-console', 'scripts/awd-gui', 'scripts/awd-simulator'],
      install_requires=['pyserial >= 3.2',],
      platforms=['Linux', 'Mac OS X', 'Windows'],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: POSIX',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                  ]
     )
