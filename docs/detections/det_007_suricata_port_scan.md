# DET-007 Suricata — Nmap/Port Scan (ET SCAN by unique ports)

This detection identifies **scan-style behaviour** against "Son-Of-Anton" Desktop PC by looking for **ET SCAN** alerts where a single source probes **many different destination ports** (or generates a high alert volume) within a **short time window**.

It is intended as a **hunt/validation search** to confirm that Suricata scan signatures are firing and that port-scanning activity is visible in Splunk.

---

## Data Source Used in This Detection

SOA (Desktop PC / Ubuntu Server) — Suricata IDS alert telemetry (EVE JSON)

- Index: `ids`
- Sourcetype: `suricata:eve`
- Host: `SOA` (Suricata sensor)
- Key fields used: `event_type`, `alert.signature`, `dest_port`, `src_ip`, `dest_ip`

---

## SPL Used
```bash
index=ids sourcetype=suricata:eve event_type=alert alert.signature="ET SCAN*"
| bin _time span=5m
| stats count as hits dc(dest_port) as unique_ports dc(alert.signature) as sig_count values(dest_port) as ports values(alert.signature) as signatures by _time src_ip dest_ip
| where unique_ports >= 8 OR hits >= 25 OR sig_count >= 3
| sort - _time
```
---

## SPL Breakdown (line-by-line)

- `index=ids sourcetype=suricata:eve event_type=alert alert.signature="ET SCAN*"` - Search Suricata **alert** events where the signature begins with **ET SCAN** (scan-related signatures).
- `| bin _time span=5m` - Bucket events into **5-minute windows** so we can detect bursts of scan behaviour.
- `| stats ... by _time src_ip dest_ip` - Aggregate activity **per time window, per source, per target**:
  - `count as hits` = total ET SCAN alerts in the time window
  - `dc(dest_port) as unique_ports` = number of **distinct destination ports** hit (dc = distinct count)
  - `dc(alert.signature) as sig_count` = number of distinct scan signatures observed
  - `values(dest_port) as ports` = list of destination ports observed
  - `values(alert.signature) as signatures` = list of ET SCAN signatures observed
- `| where unique_ports >= 8 OR hits >= 25 OR sig_count >= 3` - Keep only results that look “scan-like”:
  - many unique ports in a short time, OR
  - lots of scan alerts, OR
  - multiple scan signatures firing
- `| sort - _time` - Show newest activity first.

---

## Purpose

This search provides a **simple, reproducible view** of Nmap-style scanning against SOA by highlighting:
- which **source IP** performed the scan
- which **target IP** was scanned
- how many **ports** were probed in short windows
- which **ET SCAN signatures** fired (quick triage context)

---

## Alert Created From This Detection

This detection was also turned into a scheduled Splunk alert:

- [ALERT-002 ET SCAN Recon Activity Detected (Port Scan/Probing)](../../docs/alerts/alert_002_port_scan_activity.md)

---

## Evidence (Example)

Screenshot:
![DET-007 Example Results](../../assets/splunk_detection_007.png)