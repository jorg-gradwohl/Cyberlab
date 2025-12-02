# SMB / Samba Setup — Ubuntu

**Host:** ThinkPad (Branch Office Simulation)  
**OS:** Ubuntu 24.04 LTS

This setup creates a simple internal SMB file share for the Cyberlab branch-office simulation.

---

## 1) Verify Samba Installation

Check if Samba is installed:

```bash
smbd --version
```

If it’s not installed:

```bash
sudo apt update && sudo apt install -y samba
```

## 2) Create the Share Directory

```bash
sudo mkdir -p /srv/samba/share
sudo chown user:sambashare /srv/samba/share
sudo chmod 2770 /srv/samba/share
```
- `chown user:sambashare` sets: **Owner:** user, **Group:** sambashare
- `chmod 2770` applies: 
    - `2` → **Setgid bit** (very important): This forces all new files and folders created inside `/srv/samba/share` to **inherit the group sambashare**, instead of the user’s default group.  
    This is what makes collaborative sharing possible.
    - `7` → owner permissions (read/write/execute)
    - `7` → group permissions (read/write/execute)
    - `0` → no permissions for others

Effect:  
All files created inside the share automatically belong to group `sambashare` and are writable by all users in that group — exactly what we want for an SMB team share.

## 3) Configure the SMB Share

```bash
sudo nano /etc/samba/smb.conf
```

Scroll to the bottom and add:

```bash
[BranchShare]
    path = /srv/samba/share
    browsable = yes
    read only = no
    guest ok = no
    create mask = 0660
    directory mask = 2770
    valid users = user
```
Save and exit.
- **guest ok = no** — disables anonymous access; only authenticated users allowed.
- **create mask = 0660** — new files get permissions: rw for owner, rw for group, none for others.
- **directory mask = 2770** — new directories get rwx for owner & group, inherit the group (`2` = setgid).
- **valid users = user** — only this user (and anyone you explicitly add later) can access the share.

## 4) Set Samba User Password

This password is separate from the Linux login password.

```bash
sudo smbpasswd -a user
sudo smbpasswd -e user
```
- **`-a`** — *Add user to Samba’s internal user database.* This creates the Samba account and sets its SMB password (you'll be prompted).
- **`-e`** — *Enable the Samba account.* Without this, the user exists but is disabled and cannot authenticate.

## 5) Restart Samba Services

```bash
sudo systemctl restart smbd
sudo systemctl restart nmbd
```

Check status:

```bash
systemctl status smbd
```
It should show: active (running)

## 6) Test with smbclient (Optional)

Install smbclient if missing:

```bash
sudo apt install -y smbclient
```

Connect:

```bash
smbclient //localhost/BranchShare -U user
```

Inside smbclient:
```bash
ls  
put /etc/hostname hostname.txt
```
Exit
```bash
quit
```

## 7) Connect from client (macOS Finder in my case)

On macOS:
1. In Finder press **⌘ + K** 
2. Enter: ```smb://<ThinkPad-IP>/BranchShare```
3. Log in using:
- **Username:** user
- **Password:** (your Samba password)

The share will mount in Finder under **Locations**.

Verify file transfer works by dragging a small file into the share and checking on Ubuntu:

```bash
ls -l /srv/samba/share
```
You should see the file with group = sambashare

## 8) SMB Heartbeat Cron Job

To generate **regular SMB activity** for Splunk, we create a tiny script that writes a timestamped file into the share every 5 minutes.

### Create script:

```bash
nano ~/smb_heartbeat.sh
```

Paste:

```bash
#!/bin/bash
echo "SMB heartbeat from $(hostname) at $(date)" > /srv/samba/share/heartbeat_$(date +%F_%H-%M-%S).log
```
- #!/bin/bash — shebang; tells Linux this script must be run with the Bash shell.
- echo "SMB heartbeat from $(hostname) at $(date)" — prints a message containing the machine name and the current timestamp.
- > — redirects the output into a file (creates a new file each time).
- /srv/samba/share/heartbeat_$(date +%F_%H-%M-%S).log:
    - heartbeat_... — each file is timestamped using the format YYYY-MM-DD_HH-MM-SS, so every run creates a unique file.
    - This file is written directly into the Samba share, meaning it immediately becomes visible to any SMB client.

Make executable:
```bash
chmod +x ~/smb_heartbeat.sh
```

### Create cron job (runs every 5 minutes):

```bash
crontab -e
```

Add:

```
*/5 * * * * /home/user/smb_heartbeat.sh
```
_(In a cron expression, the five * symbols represent minutes, hours, day-of-month, month, and day-of-week, and together they define when and how often the scheduled job will run. * → means “every”. */5 → means “every 5”)_
This results in:
- A new timestamped log file every 5 minutes inside the SMB share  
- Splunk can ingest these files if we monitor the directory

Verify:

```bash
ls -l /srv/samba/share
```

## 9) Splunk Forwarding (Ingest SMB Heartbeat Logs)

To send SMB heartbeat activity into Splunk, we add a monitor stanza to the Splunk Universal Forwarder configuration on the ThinkPad (where the SMB folder is located).

Edit `inputs.conf`:

```bash
sudo nano /opt/splunkforwarder/etc/system/local/inputs.conf
```

Add the following block:

```text
[monitor:///srv/samba/share]
index = branch_office
sourcetype = smb_heartbeat
whitelist = ^heartbeat_.*\.log$
disabled = false
```
- monitor:///srv/samba/share — tells the UF to watch the SMB share directory.
- whitelist = ^heartbeat_.*\.log$ — only ingest files whose names start with heartbeat_ and end in .log (the cron script output).
- sourcetype = smb_heartbeat — keeps this separate from other logs in Splunk


Save and restart the forwarder:

```bash
sudo /opt/splunkforwarder/bin/splunk restart
```

### Verify in Splunk

In Splunk Search:

```text
index=branch_office sourcetype=smb_heartbeat
```

You should see entries like:

```
SMB heartbeat from thinkpad at Sat Nov 29 15:44:01 GMT 2025
```

This confirms:

- The cron script is working  
- Logs are being forwarded  
- Splunk is receiving and indexing SMB activity  
- Branch-office simulation now includes *file activity telemetry*