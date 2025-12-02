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
nano ~/smb_activity.sh
```

Paste:

```bash
#!/bin/bash
echo "SMB heartbeat from $(hostname) at $(date)" > /srv/samba/share/smb_activity.log
```
- #!/bin/bash — shebang; tells Linux this script must be run with the Bash shell.
- echo "SMB heartbeat from $(hostname) at $(date)" — writes a simple timestamped message.
- > — overwrites the same file each time (prevents thousands of files building up)
- /srv/samba/share/smb_activity.log - the file lives directly in the Samba share, so each run is a real SMB write.

Make executable:
```bash
chmod +x ~/smb_activity.sh
```

### Create cron job (runs every minute):

```bash
crontab -e
```

Add:

```
*/1 * * * * /home/user/smb_activity.sh
```
_(In a cron expression, the five * symbols represent minutes, hours, day-of-month, month, and day-of-week, and together they define when and how often the scheduled job will run. * → means “every”. */1 → means “every minute”)_
This results in:
- One update to `smb_activity.log` every minute inside the SMB share.
- Continous SMB activity that can be monitored in Splunk.

Verify:

```bash
ls -l /srv/samba/share
```

## 9) Splunk Forwarding (SMB Activity Logs)

To send SMB activity into Splunk, we add a monitor stanza for the `smb_activity.log` file on the Splunk Universal Forwarder running on the ThinkPad.

Edit `inputs.conf`:

```bash
sudo nano /opt/splunkforwarder/etc/system/local/inputs.conf
```

Add the following block:

```text
[monitor:///srv/samba/share/smb_activity.log]
index = branch_office
sourcetype = smb_activity
disabled = false
```
- monitor:///srv/samba/share/smb_activity.log — watches the single SMB activity file.
- sourcetype = smb_heartbeat — keeps this separate from other logs in Splunk


Save and restart the forwarder:

```bash
sudo /opt/splunkforwarder/bin/splunk restart
```

### Verify in Splunk

In Splunk Search:

```text
index=branch_office sourcetype=smb_activity
```

You should see entries like:

```
SMB activity from cyberlab at Sat Nov 29 15:44:01 GMT 2025
```

This confirms:

- The cron script is working  
- Logs are being forwarded  
- Splunk is receiving and indexing SMB activity  
- Branch-office simulation now includes *file activity telemetry*