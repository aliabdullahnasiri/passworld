#!/usr/bin/env python
"""the passworld module"""

import os

from main import manager

if __name__ == "__main__":
    # Check current OS.
    if os.name != "posix":
        raise OSError("This tool requires a POSIX-compliant operating system.")

    # Call the manager function.
    manager()
