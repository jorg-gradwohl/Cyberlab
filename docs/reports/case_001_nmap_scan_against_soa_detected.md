# CASE-001 — Nmap Port Scan Against SOA Detected (Suricata + UFW corroboration)

**Date:** 2026-02-02  
**Environment:** Cyberlab  
**Target:** 192.168.68.112 (SOA)  
**Sources observed:** 192.168.68.123 (MacBook), 192.168.68.117 (Kali VM)

---

## 1) Summary
Two hosts in the local network performed Nmap-style port scanning against SOA (192.168.68.112). Suricata generated multiple **ET SCAN** alerts consistent with service probing across several ports within short time windows. UFW telemetry separately shows high-volume blocked multi-port probing from the same scanning source(s), corroborating recon behaviour. This was expected in Cyberlab because the scans were intentional, but it confirms the detections + pipeline are working end-to-end.

---

## 2) What triggered investigation
- **Matched detection:** DET-007 Suricata — Nmap/Port Scan (ET SCAN by unique ports)
- **Corroborating detection:** DET-006 SOA UFW Port Sweep / Multi-Port Probe (Blocks)
- **Alert created:** ALERT-002 Suricata Nmap Scan Detected (scheduled)

---

## 3) Evidence summary (high-signal fields)

### 3.1 Suricata IDS evidence (ET SCAN)
Observed patterns consistent with port/service probing:

- **dest_ip:** 192.168.68.112  
- **src_ip:** 192.168.68.123 and 192.168.68.117  
- **Example signatures observed:**
    - ET SCAN Potential VNC Scan 5800-5820
    - ET SCAN Suspicious inbound to MSSQL port 1433
    - ET SCAN Suspicious inbound to Oracle SQL port 1521
    - ET SCAN Suspicious inbound to PostgreSQL port 5432
    - ET SCAN Suspicious inbound to mySQL port 3306

**Evidence (DET-007):** Short bursts of ET SCAN alerts with multiple destination ports probed in a 5-minute window, consistent with port scanning.

### 3.2 UFW firewall corroboration (blocks)
UFW detection output indicates broad, repeated blocked probing behaviour consistent with scanning:

- **SRC:** 192.168.68.123 and 192.168.68.117
- **dst:** 192.168.68.112 
- **unique_dest_ports:** high (multi-port sweep pattern)
- Confirms that, beyond IDS signatures, the host firewall observed and blocked large volumes of probing attempts.

---

## 4) Timeline (approx, based on 5-minute Splunk bins)
> Note: Times are approximate because DET-007 bins activity into 5-minute windows.

- **15:05–16:55 UTC (approx):** Scan activity observed across multiple 5-minute bins against 192.168.68.112 (SOA) from 192.168.68.123 (MacBook), consistent with Nmap probing (multiple ET SCAN clusters over time).
- **17:55–18:05 UTC (approx):** Additional scan burst against 192.168.68.112 (SOA) from 192.168.68.117 (Kali) producing ET SCAN alerts (multiple clusters across consecutive bins).

---

## 5) Triage notes (what I checked)
- **Data source:** Suricata alert telemetry corroborated by UFW blocks.
- **What happened:** Nmap-style service probing / port scan behavior observed (ET SCAN signatures).
- **Who did it (source):** `192.168.68.123` and `192.168.68.117`.
- **What was targeted:** SOA only in this dataset.
- **How loud / pattern:** Burst-style probing across multiple ports within short windows (consistent with recon, not exploitation).
- **Corroboration:** UFW telemetry shows blocked multi-port probing consistent with the same recon activity.
- **Risk call (lab):** Low–Medium. Recon activity is suspicious by nature; no follow-on exploitation indicators were assessed in this case.

---

## 6) Response (lab note + real-org playbook)
**Lab note:** Authorized test (I initiated the scan). No containment/remediation applied.

**If this was *not* authorized in a real org:**
- **Contain it:** First priority is to slow/stop the scanning. Block or rate-limit the source at the closest point I control (host firewall, network firewall, NAC). If it looks like a compromised machine, isolate it (EDR containment / VLAN quarantine) so it can’t keep probing.
- **Figure out what it was:** If the source looks internal (LAN/VPN/NAC user), pivot from `src_ip` to endpoint evidence (who was logged in, what process ran, shell history, scheduled tasks, etc.). If it’s external, pivot the other way: identify the targeted services/ports, check auth logs/WAF/firewall/EDR for follow-on activity, and enrich the `src_ip` (reputation/geo/ASN) to decide if it’s noise or a real threat.
- **Reduce the risk:** If it wasn’t legit, look at how they got in (Wi-Fi, VPN, exposed services), tighten segmentation so users can’t freely scan server networks, and close down anything on the target that doesn’t need to be exposed.

**Scope check:** Look for similar scan patterns against other internal assets (ET SCAN / firewall multi-port blocks) to confirm whether this was targeted or widespread.

---

## 7) Related artifacts
- **DET-007:** [DET-007 Suricata — Nmap/Port Scan (ET SCAN by unique ports)](../../docs/detections/det_007_suricata_port_scan.md)
- **DET-006:** [DET-006 SOA UFW - Port Sweep / Multi-Port Probe(Blocks)](../../docs/detections/det_006_ufw_port_sweep_blocks.md)
- **ALERT-002:** [ALERT-002 ET SCAN Recon Activity Detected (Port Scan/Probing)](../../docs/alerts/alert_002_port_scan_activity.md)