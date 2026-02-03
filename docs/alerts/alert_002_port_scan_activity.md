# ALERT-002 ET SCAN Recon Activity Detected (Port Scan/Probing)

This alert is the **scheduled version of DET-007**.  
It runs automatically and creates a Triggered Alert when Suricata generates **ET SCAN** activity consistent with Nmap-style port scanning against SOA.

---

## Based On

- Detection: [DET-007 Suricata — Nmap/Port Scan (ET SCAN by unique ports)](../../docs/detections/det_007_suricata_port_scan.md)

The detection logic (SPL + thresholds) is documented in DET-007.  
This alert doc only captures the **alert configuration** used.

---

## Data Source Used in This Alert

Suricata IDS alert telemetry (EVE JSON) on SOA

- Index: `ids`
- Sourcetype: `suricata:eve`
- Host: `SOA`
- Key fields: `event_type`, `alert.signature`, `src_ip`, `dest_ip`, `dest_port`

---

## Alert Configuration

### Schedule
- Alert type: **Scheduled**
- Frequency: **Hourly**
- Runs: **At 0 minutes past the hour**

### Trigger condition
- Trigger alert when: **Number of results > 0**
- Trigger mode: **Once** (per scheduled run)

### Throttle / suppression
- Throttle: **Enabled**
- Suppress triggering for: **30 minutes**
- Expires: **24 hours**

### Actions
- **Add to Triggered Alerts** (as configured in Splunk)

---

## What to Review When It Fires

Expected high-signal fields from the alert results:
- `src_ip` (scanning host)
- `dest_ip` (target host)
- `ports` (destination ports probed in the time window)
- `signatures` (which ET SCAN signatures fired)
- `unique_ports`, `hits`, `sig_count` (burst indicators from the DET-007 aggregation)

---

