import os

file_path = "routes.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Clean lines - check for the first real code line "from flask..."
# From the log, line 1 had junk prepended to it.
# We want to replace everything from the very beginning until we hit the real data.

new_imports = [
    "from flask import Blueprint, request, jsonify\n",
    "from db import mysql\n",
    "from flask_bcrypt import Bcrypt\n",
    "import random\n",
    "import smtplib\n",
    "from email.mime.text import MIMEText\n",
    "import joblib\n",
    "import numpy as np\n",
    "import config\n",
    "import re\n",
    "\n",
    "routes = Blueprint(\"routes\", __name__)\n",
    "bcrypt = Bcrypt()\n",
    "\n",
    "# ======================\n",
    "# IDENTITY HELPERS\n",
    "# ======================\n",
    "\n"
]

# Find where get_player_id starts
start_idx = -1
for i, line in enumerate(lines):
    if "def get_player_id" in line:
        start_idx = i
        break

if start_idx != -1:
    final_lines = new_imports + lines[start_idx:]
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(final_lines)
    print(f"Successfully fixed routes.py starting from index {start_idx}")
else:
    print("Could not find get_player_id hook!")
