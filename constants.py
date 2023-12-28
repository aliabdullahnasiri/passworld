#!/usr/bin/env python
import os
from typing import Union

# Database constants
USERNAME: Union[None, str] = os.environ.get("USER")
PASSWORD_TBL: str = "passwords"
PATH: str = f"/home/{USERNAME}/.local/share/passworld"
DB_PATH: str = f"{PATH}/database"
DB_FILE_NAME: str = "database.db"
