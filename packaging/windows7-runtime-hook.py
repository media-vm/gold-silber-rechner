"""Provide Python 3.9's zoneinfo import for the Windows 7 / Python 3.8 build."""
import sys

if sys.version_info < (3, 9):
    import backports.zoneinfo

    sys.modules['zoneinfo'] = backports.zoneinfo
