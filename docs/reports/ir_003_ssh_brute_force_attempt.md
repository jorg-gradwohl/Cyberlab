# IR-003 — SSH Brute Force Attempt Detected (Linux Auth Logs) – SOA

**Date/Time (UTC):** 22-02-2026 15:10 to 15:15  
**Severity:** Medium 
**Status:** Closed
**Category:** Credential Attack

---

## 1) Trigger
What caused me to start investigating?
- **Source:** ALERT-004 Possible SSH Brute Force (Linux Hosts)
- **Reason it looked suspicious:** spike in failed login attempts

---

## 2) Evidence (Key Artifacts)
Bullet the *minimum* hard evidence I used.
- 2026-02-22T15:14:45.748675+00:00 SOA sshd[902807]: Failed password for root from 192.168.68.117 port 42100 ssh2
- 2026-02-22T15:14:45.748096+00:00 SOA sshd[902808]: Failed password for root from 192.168.68.117 port 42114 ssh2
- 22-02-2026 15:10 to 15:15 - 384 failed login attempts (source: /var/log/auth.log) triggering ALERT-004 Possible SSH Brute Force (Linux Hosts)

---

## 3) Scope
What systems/entities are involved?
- **Primary target:** SOA `192.168.68.112` SSH port 22
- **Other affected assets:** none observed
- **Suspected source:** `192.168.68.117`
- **Time window:** 15:10 / 15:15
- **Volume:** 384 failed ssh login attempts

---

## 4) Triage Analysis
Answer these explicitly:
- **What was attempted?**  
  SSH brute force login attempt at SOA 192.168.68.112 port 22. (High volume attempts)
- **Did it succeed? Why/why not?**  
  Failed. No succesful SSH sessions opened from 15:10 and 15:30
- **Impact:**  
  None observed

---

## 5) Actions Taken
What I actually did during the case (or would do in a real org).
- **Containment:** None (In a real org: temporarily block `192.168.68.117`)
- **Eradication/Hardening:** (In a real org: enforce key-only auth)
- **Recovery:** Not required

---

## 6) Lessons Learned / Improvements
What will I change so the lab gets better next time?
- Learned that Splunk Fast Mode hides manual field extractions, so SSH triage should be done in Smart Mode.

---

## 7) Summary
An SSH brute-force style password guessing burst was observed against SOA (192.168.68.112:22) from 192.168.68.117, generating 384 failed login attempts between 15:10–15:15 UTC. No evidence of a successful SSH session was observed in the window, so the activity is assessed as blocked/failed with no impact.

---

## Evidence Attachments
![Alert Trigger](/assets/ir_003_image_01.png)


![Raw Events](/assets/ir_003_image_02.png)


![Proof of no succesful logins](/assets/ir_003_image_03.png)


----

## Expolit Screenshot

![Hydra SSH bruteforce](/assets/ir_003_image_04.png)
