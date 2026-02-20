# IR-002 — Suricata Web Alert Burst – Juice Shop (SOA:3000)

**Date/Time (UTC):** 20-02-2026 15:43 to 15:44  
**Severity:** Low 
**Status:** Closed
**Category:** Recon/Probe, Exploit Attempt

**Executive Summary:** A short burst of encoded traversal attempts targeted Juice Shop (SOA:3000) from 192.168.68.117 and was blocked/failed with no impact observed.

---

## 1) Trigger
What caused me to start investigating?
- **Source:** Splunk dashboard: Network Security - Suricata IDS - Juice Shop Tab
- **Reason it looked suspicious:** big spike at 15:43 and many Suricata signatures triggered including `ET WEB_SERVER /etc/passwd Detected in URI`. Also observed URL encoded requests like `%2f%25%32%66%2e.%2f%2e.%25%32f..%%32%66%2e.%%32%66%2e.%2f%2e%2e%2f..%%32%66%2e.%252%66..%25%32%66.%2e/%62o%6ft.%69n%69`

---

## 2) Evidence (Key Artifacts)
Bullet the *minimum* hard evidence I used.
- Raw event (Suricata alert): 2026-02-20 15:43:23.268Z — `ET WEB_SERVER /etc/passwd Detected in URI` (category=Attempted Information Leak, action=allowed) from src_ip=192.168.68.117:49742 → dest_ip=192.168.68.112:3000 (http_method=GET, status=400, http.hostname=192.168.68.112, ua=Mozilla/5.0 ... Chrome/74.0.3729.169 ..., url=`%2fn%65%74%67%65t?sid=%75se%72&%6dsg=%33%300&%66%69le=../%2e.%2f..%2f%2e%2e%2f%2e%2e%2f../%2e%2e/.%2e/%2e.%2f.%2e%2fe%74c/%70%61s%73%77d`)
- Raw event (Suricata alert): 2026-02-20 15:43:04.996Z — `ET INFO Dotted Quad Host TGZ Request` (category=Potentially Bad Traffic, action=allowed) from src_ip=192.168.68.117:32772 → dest_ip=192.168.68.112:3000 (http_method=GET, status=400, http.hostname=192.168.68.112, url=%2f19%32.%31%368.tgz)
- Source-of-truth (Juice Shop Docker log): 2026-02-20 15:43:25.230Z — `URIError: Failed to decode param` (stderr) while processing a heavily URL-encoded/traversal-style parameter (target host=SOA, sourcetype=docker:json, index=docker)

---

## 3) Scope
What systems/entities are involved?
- **Primary target:** SOA (Son-of-Anton) — Juice Shop service (TCP 3000) 192.168.68.112:3000
- **Other affected assets:** none observed
- **Suspected source:** 192.168.68.117
- **Time window:** 15:43 to 15:44
- **Volume:** 711 Suricata http events

---

## 4) Triage Analysis
Answer these explicitly:
- **What was attempted?**  
  Encoded path traversal / local file disclosure attempts against OWASP Juice Shop (192.168.68.112:3000) from 192.168.68.117, including requests targeting sensitive files (e.g., /etc/passwd, boot.ini) and traversal sequences (../, URL-encoded variants)
- **Did it succeed? Why/why not?**  
  Blocked/Failed. Suricata HTTP telemetry shows 400 responses for traversal/LFI-style requests, and the Juice Shop container logs show URIError: Failed to decode param during the same window, indicating the application rejected the encoded payload rather than returning file contents.
- **Impact:**  
  None observed

---

## 5) Actions Taken
What I actually did during the case (or would do in a real org).
- **Containment:** None (known internal lab source. Activity stopped after testing)
- **Eradication/Hardening:** None during this case
- **Recovery:** Not required

---

## 6) Lessons Learned / Improvements
What will I change so the lab gets better next time?
- Added a Top Signatures — Juice Shop (3000) panel to the Suricata IDS dashboard to speed up triage by immediately showing the most frequent alert signatures for the target service during spikes.

---

## 7) Summary
A burst of Suricata web alerts was observed against OWASP Juice Shop (SOA 192.168.68.112:3000) from 192.168.68.117 within a 1 minute window, including encoded traversal attempts targeting sensitive files (e.g., /etc/passwd). Triage indicates the activity was blocked/failed (HTTP 400 responses and Juice Shop URIError: Failed to decode param), with no impact observed.

---

## Evidence Attachments
Trigger view Suricata Dashboard

![Trigger view](/assets/ir_002_image1.png)

Expanded raw event

![Raw Event](/assets/ir_002_image_02.png)

Source-of-truth validation

![Source of truth](/assets/ir_002_image_03.png)

Decoded URL

![Decoded URL](/assets/ir_002_image_04.png)


----

Attacker activity

![Nikto](/assets/ir_002_image_05.png)