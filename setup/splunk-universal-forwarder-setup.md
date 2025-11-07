# Splunk Universal Forwarder Setup

Hosts: **Lenovo ThinkPad** (Ubuntu + Windows 10 Pro), **MacBook Pro** (Sequoia)
Role: **Log forwarding to Desktop PC (Splunk Enterprise Indexer)**
Destination: **`Splunk_Enterprise_IP`:9997** (Example `192.168.68.112:997`)
Index used: **endpoints**

---

## 1) Windows 10 Pro (ThinkPad)

### Install
- Run the Splunk Universal Forwarder `.msi` installer.  
- Accept the license → choose **Local System Account**.  
- Leave Deployment Server blank.  
- Receiving Indexer Host: **`Splunk_Enterprise_IP`** Port: **9997**.  
- Finish the installer.

### Configure Windows Event Logs
- Edit this file:
C:\Program Files\SplunkUniversalForwarder\etc\apps\SplunkUniversalForwarder\local\inputs.conf

- Add:
```
[WinEventLog://Application]
index = endpoints
disabled = 0

[WinEventLog://Security]
index = endpoints
disabled = 0

[WinEventLog://System]
index = endpoints
disabled = 0
```
- Restart the Splunk Forwarder service (Services → SplunkForwarder → Restart).

### Verify in Splunk Web

Search:
index=endpoints host=`hostname` | stats count by sourcetype


## 2) Ubuntu (ThinkPad)

### Configure log monitors
Edit or create:
/opt/splunkforwarder/etc/apps/search/local/inputs.conf

Add:
```
[monitor:///var/log/syslog]
index = endpoints
disabled = false

[monitor:///var/log/auth.log]
index = endpoints
disabled = false

[monitor:///var/log/kern.log]
index = endpoints
disabled = false
```

### Point forwarder to Desktop PC and restart
```
sudo /opt/splunkforwarder/bin/splunk add forward-server `Splunk_Enterprise_IP`:9997
sudo systemctl restart SplunkForwarder.service
```

### Verify
index=endpoints host=`hostname` | stats count by source


## 3) macOS (MacBook Pro)

### Configure log monitors
Edit or create:
/Applications/SplunkForwarder/etc/system/local/inputs.conf

Add:
```
[monitor:///var/log/system.log]
sourcetype = macos_system
index = endpoints

[monitor:///var/log/install.log]
sourcetype = macos_install
index = endpoints
```

### Point forwarder to Desktop PC and restart
```
sudo /Applications/SplunkForwarder/bin/splunk add forward-server `Splunk_Enterprise_IP`:9997
sudo /Applications/SplunkForwarder/bin/splunk restart
```


## 4) Verify
index=endpoints (source="/var/log/system.log" OR source="/var/log/install.log") | stats count by host,source

## Notes
- All endpoints send to Desktop PC `Splunk_Enterprise_IP` (192.168.68.112) on port 9997/TCP.
- Logs are written to the unified endpoints index.
- File monitoring on macOS and Ubuntu uses configuration-file edits; Windows setup is handled through the installer GUI.
- Each forwarder runs automatically on system startup.
