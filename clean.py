"run this through shell to format code and lint for errors"

import os

os.system("black --exclude venv .")
os.system("flake8 --exclude=venv --ignore=E501 .")
