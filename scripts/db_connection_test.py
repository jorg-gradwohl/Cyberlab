# --------------------------------------------------------
# db_connection_test.py
# --------------------------------------------------------
# Purpose:
#   - Connect to the CyberLab MariaDB container using credentials stored safely in a .env file.
#   - Query the devices table for a specific hostname.
#   - Print out the device_id, hostname, and IP address if found.
#
# Notes:
#   - Keeps secrets out of the script by loading environment variables.
#   - Uses mysql-connector to handle the DB connection.
#   - Uses dictionary=True so query results come back with column names.
# --------------------------------------------------------

import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

# --------------------------------------------------------
# Load environment variables from the .env file located one directory above this script, at project root.
# This provides DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS.
# --------------------------------------------------------

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

# --------------------------------------------------------
# Database connection settings pulled in from environment variables so no secrets are hardcoded.
# --------------------------------------------------------

DB = {
    "host": os.environ["CYBERLAB_DB_HOST"],        # MariaDB container IP
    "port": int(os.environ["CYBERLAB_DB_PORT"]),   # Default MariaDB port (3306)
    "database": os.environ["CYBERLAB_DB_NAME"],    # Database name (e.g., cyberlab)
    "user": os.environ["CYBERLAB_DB_USER"],        # DB username
    "password": os.environ["CYBERLAB_DB_PASS"],    # DB password
}

# --------------------------------------------------------
# Establish connection to the database
# --------------------------------------------------------

conn = mysql.connector.connect(**DB)

# --------------------------------------------------------
# Create a cursor object to send queries to the DB. "dictionary=True" means results will be returned as dicts
# --------------------------------------------------------

cur = conn.cursor(dictionary=True)

# --------------------------------------------------------
# Define which device we want to look up. (later this will be parameterized or automated)
# --------------------------------------------------------

hostname = "thinkpad"

# --------------------------------------------------------
# Execute the SQL query safely using placeholders (%s). 
# This prevents SQL injection and ensures correct parameter substitution.
# --------------------------------------------------------

cur.execute(
    "SELECT device_id, hostname, ip_address FROM devices WHERE hostname=%s",
    (hostname,),
)

# --------------------------------------------------------
# Fetch the first row of the result
# --------------------------------------------------------

row = cur.fetchone()

if row is None:
    # If no row found for this hostname
    print("Not found")
else:
    # Print the results nicely
    print("device_id:", row["device_id"])
    print("hostname :", row["hostname"])
    print("ip_addr  :", row["ip_address"])

# --------------------------------------------------------
# Close cursor and connection after use
# --------------------------------------------------------

cur.close()
conn.close()