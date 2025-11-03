# 📓 Cyberlab Progress Log

This file tracks the evolution of the Cyberlab project over time.  
Entries are added as new components are installed, tested, or refined.  

---
## 2025-11-03 (cleanup)
- Archived `db_connection_test.py` and associated `.env.sample` into `archive_scripts/db_connection_test/`.
- Committed and pushed the archive changes to GitHub.
- Rationale: preserve learning artifacts while keeping the public repo focused on active Cyber Security projects.


## 2025-09-04
- Deployed a new container running a full Bitcoin node to validate the blockchain.
- Deployed an additional container with **SatoshiTop**, a dashboard similar to htop but for Bitcoin node monitoring.
- Updated the network diagram accordingly.
- Not directly cybersecurity related so won't go into too much detail here. Just something I'm personally interested in.


## 2025-08-30 (archived / legacy)

- **Goal:**  
  Python script runs in the background, scans all devices for open ports, and updates the SQL database accordingly.

- **Progress:**  
  - Created a SQL database in the MariaDB container with 2 tables: one for inventory and one for open ports logging.  
  - Manually populated the inventory DB with IP, MAC address, name, OS, and last seen.  
  - Added Python test script `db_connection_test.py` to the `scripts/` folder.  
  - Purpose: establish a connection to the MariaDB container and confirm I can query the `devices` table using values from `.env`.  
  - Verified that `.env` loading works automatically via `python-dotenv`, so no need to manually `source` environment variables.  
  - Queried device by hostname ("thinkpad") and successfully retrieved details (`device_id`, `hostname`, `ip_address`).  
  - This script is only a first test to prove database connectivity before moving on to the real port-scanning and updating database.  


## 2025-08-25
- Created initial **Cyberlab network diagram** and added to `diagrams/`.  
- Segmented IoT devices to their own SSID outside Cyberlab scope.  

## 2025-08-22
- Installed Ubuntu and **Docker** on Desktop PC (simulated branch office).  
- Deployed **MariaDB 10.11 container** to store small home inventory dataset.

## 2025-07-25
- Completed setup of **Lenovo ThinkPad T480** with Ubuntu, Windows 10 Pro, and Kali in VirtualBox.  
- Configured Virgin Hub in **modem-only mode**.  
- Deployed TP-Link Deco mesh as main router/AP. 