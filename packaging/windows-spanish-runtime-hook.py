"""Default the Spanish Windows executable to Spanish on any system."""

import sys

# An explicit --lang from the caller comes later and takes precedence.
sys.argv.insert(1, "--lang=es")
