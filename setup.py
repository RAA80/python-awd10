#! /usr/bin/env python3

from setuptools import setup

setup(name="python-awd10",
      version="0.3",
      description="AWD10 controllers library",
      url="https://github.com/RAA80/python-awd10",
      author="Alexey Ryadno",
      author_email="aryadno@mail.ru",
      license="MIT",
      packages=["awd10"],
      scripts=["scripts/awd-console", "scripts/awd-gui", "scripts/awd-simulator"],
      install_requires=["pyserial >= 3.4"],
      platforms=["Linux", "Windows"],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Science/Research",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: Microsoft :: Windows",
                   "Operating System :: POSIX :: Linux",
                   "Operating System :: POSIX",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.8",
                   "Programming Language :: Python :: 3.9",
                   "Programming Language :: Python :: 3.10",
                   "Programming Language :: Python :: 3.11",
                  ],
     )
