# Windows Sysmon → Splunk Setup Guide

I installed Sysmon because I wanted **high-fidelity endpoint telemetry** (process creation, network connections, image loads, registry/file activity) that standard Windows logs often don’t capture in enough detail for SOC-style investigations. In short: Sysmon turns my Windows VM into a **realistic endpoint data source** for detections, hunting, and dashboarding in Splunk.

---

## What this setup delivers
- Sysmon running on my Windows 10 telemetry VM, using a hardened community config (Olaf Hartong).
- Sysmon events forwarded into Splunk via **Splunk Universal Forwarder (UF)**.
- Splunk properly parsing Sysmon XML into **useful extracted fields** (Image, CommandLine, ParentImage, Hashes, DestinationIp, etc.).
- Sysmon events stored in a dedicated Splunk index: `sysmon`.

---

## Lab components
- **Windows VM (VMWare Workstation)**: Running on Lenovo Thinkpad / Windows 10.
- **Splunk Enterprise server**: Desktop PC - `SOA` (son-of-anton)
- **Data source:** Windows Event Log channel - `Microsoft-Windows-Sysmon/Operational`

---

## Prerequisites
- Splunk Enterprise running and reachable
- Splunk Universal Forwarder installed on the Windows VM
- Admin rights on the Windows VM
- Sysmon downloaded (Sysinternals) (in my case to - `C:\Tools\Sysmon\`)
- Olaf Hartong Sysmon config XML downloaded (see below)

---

## 1) VMware Workstation networking (important)
I switched the Windows VM network mode to **Bridged** because NAT caused connectivity issues in my environment.    
Bridged made the VM reachable reliably for forwarding and management.

---

## 2) Install Sysmon with the Olaf Hartong config    
I used Olaf Hartong’s Sysmon config because it’s a widely trusted, community-maintained baseline that focuses Sysmon on high-value security telemetry while reducing noise. The XML defines which Sysmon events to log and how (process creation, network connections, hashes, registry/file activity, etc.), so my Windows VM generates SOC-relevant data that’s actually useful for hunting and detections instead of a noisy firehose.

### 2.1 Get the config
**Olaf Hartong’s Sysmon config** (commonly referred to as *sysmon-modular*).    

Download the XML from Olaf’s repo and place it on the Windows VM (example path):

`C:\Tools\Sysmon\sysmonconfig.xml`

### 2.2 Install / apply config
From an elevated CMD/PowerShell in the Sysmon folder:

```bash
sysmon64.exe -accepteula -i C:\Tools\Sysmon\sysmonconfig.xml
```

If Sysmon was already installed and I only wanted to update the config:

```bash
sysmon64.exe -c C:\Tools\Sysmon\sysmonconfig.xml
```

⸻

## 3) Install the Splunk Add-on for Sysmon (Splunk Enterprise side)

I installed Splunk Add-on for Sysmon on my Splunk Enterprise server (via Splunk Web / Splunkbase).

This add-on provides the parsing rules, aliases, and extractions Splunk needs to turn raw Sysmon XML into useful fields.

App name on disk: `Splunk_TA_microsoft_sysmon`

**Note**: Seeing a “big XML blob” in the event body is normal. The real win is having lots of meaningful fields extracted in the left sidebar and usable in SPL.

⸻

## 4) Configure the Universal Forwarder to send Sysmon correctly (the critical part)

### 4.1 Create a dedicated Splunk index (recommended)

On Splunk Enterprise:
- Settings → Indexes → New Index / Index Name: sysmon

### 4.2 Set UF inputs.conf (Windows VM)

On the Windows VM, I configured UF to:
- collect Sysmon Operational channel
- render XML

I set `renderXml=true` so Splunk receives full XML. In my setup, the Splunk Sysmon TA (Technology Add-on) applies field extractions using a props stanza that matches on source, specifically: `[source::XmlWinEventLog:Microsoft-Windows-Sysmon/Operational]`.

That means the important validation check in Splunk is that the events’ source equals `XmlWinEventLog:Microsoft-Windows-Sysmon/Operational`

- route events into the sysmon index:

File:
`C:\Program Files\SplunkUniversalForwarder\etc\system\local\inputs.conf`

Stanza:
```bash
[WinEventLog://Microsoft-Windows-Sysmon/Operational]
disabled=0
renderXml=true
index=sysmon
```

In my setup the events land with sourcetype=xmlwineventlog, and the Sysmon TA still extracts fields because it matches on `source::XmlWinEventLog:Microsoft-Windows-Sysmon/Operational`.


### 4.3 Restart the forwarder service

From an elevated Command Prompt / PowerShell on the Windows VM:
```bash
sc stop SplunkForwarder
sc start SplunkForwarder
sc query SplunkForwarder
```

## 5) Verify UF config is actually loaded (sanity check)

On the Windows VM:
```bash
"C:\Program Files\SplunkUniversalForwarder\bin\splunk.exe" btool inputs list --debug | findstr /i "Microsoft-Windows-Sysmon/Operational"
```
- `btool` - Splunks configuration "truth" tool. Best way to prove what Splunk is actually using.
- `inputs` - the config file type I want btool to inspect: `inputs.conf`
- `list` - tells btool to print out the stanzas and settings from that config type.
- `--debug` - adds extra detail where each setting came from. Crucial to confirm the stanza isn't being overridden elswhere.
- `| findstr /i "Microsoft-Windows-Sysmon/Operational"` - filter the output to what I'm looking for.

I used this to confirm my Sysmon stanza is loaded and that renderXml + index are applied.

```bash
[WinEventLog://Microsoft-Windows-Sysmon/Operational]
renderXml = true
index = sysmon
```
---

## 6) Splunk validation searches (these are my “it works” checks)

### 6.1 Confirm events are landing in the right place
```bash
index=sysmon
| stats count by host source sourcetype
```
### 6.2 Process creation (Sysmon Event ID 1)
```bash
index=sysmon EventCode=1
| table _time host User Image CommandLine ParentImage ParentCommandLine Hashes
| sort - _time
```
### 6.3 Network connections (Sysmon Event ID 3)
```bash
index=sysmon EventCode=3
| table _time host Image User DestinationIp DestinationPort Protocol Initiated SourceIp SourcePort
| sort - _time
```

Success criteria:
- I see events returning.
- The left sidebar shows lots of extracted fields.
- Fields like Image, CommandLine, ParentImage, Hashes, DestinationIp actually populate.

## 7) Troubleshooting

**Problem:** Fields weren’t extracting

The root cause was that Splunk wasn’t applying the Sysmon TA’s field extractions. The fix was making sure the Sysmon TA was installed/enabled on SOA and that the incoming events had renderXml=true so the event source is XmlWinEventLog:Microsoft-Windows-Sysmon/Operational, which is what the TA matches on.

**Fix that worked:**
Ensure UF stanza includes:
```bash
renderXml=true
(optional but recommended) index=sysmon
```

*In my environment the TA extracts fields based on source::XmlWinEventLog:Microsoft-Windows-Sysmon/Operational, even though the sourcetype is xmlwineventlog.*

---

**Problem:** NAT networking issues blocked progress

**Fix that worked:** Switch VM networking to Bridged so the VM could reliably communicate and forward events.

---

## Result

I now have Sysmon endpoint telemetry flowing into Splunk, stored in index=sysmon, and properly parsed into usable fields for hunting, detections, dashboards, and SOC-style analysis.




