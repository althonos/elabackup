#!/bin/env python
# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import locale
import codecs

from . import App

# Patch STDOUT / STDERR in Python 2.6 to work with `tqdm` (see tqdm/tqdm#127)
if sys.version_info[:2] == (2, 6):
    sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
    sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr)

# Run the app
sys.exit(App.main())
