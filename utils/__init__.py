# coding: utf-8

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
