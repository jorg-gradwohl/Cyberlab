# Splunk Enterprise Setup

Host: **Desktop PC**
OS: **Ubuntu 24.04 LTS**
Role: **Splunk Enterprise (Indexer + Search Head)**

---

### 1) Enable service and start Splunk

Run once on the Desktop PC:

```bash
sudo /opt/splunk/bin/splunk enable boot-start
sudo /opt/splunk/bin/splunk start
```

### 2) Create the unified index (endpoints)

In Splunk Web:

- Settings → Indexes → New Index
- Name: endpoints → Save


### 3) Turn on the receiver (TCP 9997)

In Splunk Web:

- Settings → Forwarding and receiving → Configure receiving → New Receiving Port
- Port: 9997 → Save


### 4) Monitor the Desktop PC's own OS logs

In Splunk Web:

- Go to: Settings → Data inputs → Files & directories → New Local File & Directory
- Add: /var/log/syslog → Sourcetype: syslog → Index: endpoints
- Add: /var/log/auth.log → Sourcetype: linux_secure → Index: endpoints
- (Optional) /var/log/kern.log → Sourcetype: kernel → Index: endpoints
- Save each


### 5) Quick verify

In Splunk Web Search:

- index=endpoints host=`hostname` | stats count by source
- Confirm you see /var/log/syslog and /var/log/auth.log

## Notes

- Splunk home: /opt/splunk
- Receiver port for forwarders: 9997/TCP (standard practice)
- File monitoring can also be configured later through inputs.conf if a configuration-file approach is preferred. The same log paths and index=endpoints entries should be used.