# Suricata IDS Setup - Ubuntu (Desktop PC / Server)

**Host:** Desktop PC / Server  
**OS:** Ubuntu 24.04 LTS  
**Role:** IDS (Intrusion Detection System)   
**Splunk Index used:** ids   

---

## 1) Install and Prepare Suricata

Install from the standard repository:
```bash
sudo apt update && sudo apt install suricata -y
```
Temporarily stop and disable the default service to perform manual configuration and fixes:
```bash
sudo systemctl stop suricata
sudo systemctl disable suricata
```

---

## 2) Configuration Fixes (suricata.yaml)

Open the configuration file to correct the interface and network settings:

```bash
sudo nano /etc/suricata/suricata.yaml
```
**Change Interface:**   
Search for the af-packet section. The default is often eth1, which caused the service to fail. Update it to match your hardware:
```YAML
af-packet:
  - interface: eno1
```
(Look for other entries with eth1 and change to eno1)

**Fix Subnet (HOME_NET):**      
Update the address group to match your local network range:

```YAML
vars:
  address-groups:
    HOME_NET: "[192.168.68.0/22]"
```

**Enable Community ID:**   
Enable flow hashing for easier correlation in Splunk:
```bash
sudo nano /etc/suricata/suricata.yaml
```
```YAML
community-id: true
community-id-seed: 0
```

---

## 3) Splunk Ingestion (inputs.conf)

Configure the local Splunk instance to monitor the Suricata JSON output:

```bash
sudo nano /opt/splunk/etc/system/local/inputs.conf
```

Add:

```bash
[monitor:///var/log/suricata/eve.json]
index = ids
sourcetype = suricata:eve
disabled = 0
```

---

## 4) Data Filtering & License Management

To save license quota of the free splunk enterprise, apply a filter to drop low-value events (like flow or stats) and only keep high-value security logs:    

**props.conf**   
The props.conf file is used by Splunk to define how incoming data should be interpreted and processed before it is indexed.
```bash
sudo nano /opt/splunk/etc/system/local/props.conf
```

```plaintext
[suricata:eve]
KV_MODE = json
TRANSFORMS-drop_low_value = suricata_drop_low_value
```
The last line links the suricata:eve sourcetype to the suricata_drop_low_value transform defined in transforms.conf.   
The transform drops low-value events (such as flow and stats) by sending them to nullQueue, while allowing only high-value security events (alerts, HTTP, TLS, DNS, SSH) to be indexed.   
Because this filtering happens before indexing, dropped events do not count toward license usage, and overall storage and search performance are improved.

---

**transforms.conf**
```bash
sudo nano /opt/splunk/etc/system/local/transforms.conf
```

```plaintext
[suricata_drop_low_value]
REGEX = \"event_type\":\"(?!alert|http|tls|dns|ssh)[^\"]+\"
DEST_KEY = queue
FORMAT = nullQueue
```

This configuration defines the suricata_drop_low_value transform used to filter Suricata events.   
The REGEX matches any Suricata event whose event_type is not alert, http, tls, dns, or ssh.   
Events matching this pattern are considered low-value (such as flow or stats events).    
DEST_KEY = queue and FORMAT = nullQueue instruct Splunk to discard these matched events before they are indexed.   
   
As a result, only high-value security-relevant events are ingested, reducing license usage while keeping the dataset focused and SOC-relevant.

---

## 5) Start Service and Verify

Update signatures and start the service:
```bash
sudo suricata-update
sudo systemctl enable suricata
sudo systemctl start suricata
```

Verify status:
```bash
sudo systemctl status suricata
```

---

## 6) Validation (nmap Testing)

Verify that alerts are being generated and indexed correctly in Splunk.
   
**Trigger Alert**

Run a port scan against the Desktop PC / Sever from another machine:

```bash
nmap -sS -p- -Pn 192.168.68.X
```
**-sS** - Performs a TCP SYN (stealth) scan. Sends SYN packets without completing the TCP handshake, making the scan faster and more evasive while still revealing open ports.   
**-p-** - Scans all 65,535 TCP ports instead of only the most common ones, ensuring no exposed services are missed.   
**-Pn** - Disables host discovery and assumes the target is online, allowing the scan to proceed even if ICMP or ping requests are blocked.
   
This command performs a full, aggressive reconnaissance scan that closely resembles real attacker behavior and is likely to trigger IDS alerts.   

**Search Verification:**

Confirm the activity appears in the ids index:   
```Code snippet
index=ids event_type=alert | stats count by alert.signature, src_ip
```

---

## Notes

**Critical Fix:** The interface must be set correctly (eno1 in my case) in suricata.yaml; if it reverts to eth1, the IDS will fail to capture packets.   
**Log Location:** /var/log/suricata/eve.json
**Filtering:** Only alert, http, tls, dns, and ssh events are currently indexed.   
**Rules:** Use `suricata-update` periodically to keep signatures current