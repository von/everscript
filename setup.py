#!/usr/bin/env python
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name = "everscript",
    version = "0.1",
    packages = [ "everscript" ],
    scripts = [ 'scripts/evernote.py' ],
    install_requires=['appscript >= 1.0'],

    author = "Von Welch",
    author_email = "von@vwelch.com",
    description = "A python/appscript/AppleScript interface to EverNote",
    license = "Apache2",
)
