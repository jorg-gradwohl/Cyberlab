# Cyberlab Generic Incident Response Runbook

## Purpose
A simple incident response runbook for Cyberlab investigations.

## Core Rule
If the activity **does not show up in defender telemetry**, this is **not Incident Response** yet — it becomes **Engineering**:
- fix logging/collection, parsing/field extraction, detection logic, or visibility gaps
- then re-test and re-run triage

---

## 1) Trigger → Start the Case
**Goal:** lock in what I actually observed

Record:
- Trigger source (alert name / dashboard panel / manual observation)
- Time window (first seen / last seen)
- Primary entity (host, user, src_ip, URL, process, file, container/service)
- Initial severity (Low / Medium / High) using the rubric below

**Severity / Priority**
- **Low:** blocked/failed attempt, recon/probing, no impact indicators
- **Medium:** suspicious success indicators, persistence attempt, repeated auth failures, unusual execution
- **High:** confirmed compromise, data exposure, credential theft, lateral movement, service disruption

---

## 2) Validate the Trigger with Raw Evidence
**Goal:** confirm the event is real and understand exactly what was detected:

- Pivot from the summary/visualization into the **raw event(s)**
- Extract only facts (no interpretation yet):
  - timestamp(s)
  - involved systems (src/dest host or account)
  - action/result (allowed/blocked, status code, failure reason)
  - key indicator (URI/process/hash/file path/command line)

---

## 3) Scope the Activity
**Goal:** determine how large this is and what else is involved.

Check:
- Time scope: first/last, bursts, recurring pattern
- Entity scope:
  - other affected hosts/services
  - other source IPs/users
  - related indicators (same user-agent/tooling string, same filename, same command pattern)
- Volume: single event vs repeated attempts

Output:
- A short statement of scope (e.g., “single source → single target over 10 minutes”)

---

## 4) Determine Success vs Failure (Impact Test)
**Goal:** decide whether this is just “attempted activity” or “impact”.

Rule: **do not treat a single metadata signal as proof of success**
- Example: **HTTP 200** does not prove data exposure or **alert fired** does not prove execution occurred

Pivot to the **best source-of-truth** for the question I'm answering:
- **Endpoint truth**: process creation, parent/child, command line, network connections, file writes
- **Application/service truth**: application logs, service logs, authentication logs, error logs
- **Network truth**: connections, requests, protocol metadata, IDS/IPS signatures

Decide one:
- **Blocked/Failed**: clear rejection/denial/errors with no follow-on impact indicators
- **Possible Success**: ambiguous signals that require deeper validation
- **Confirmed Impact**: direct evidence of disclosure/execution/persistence/privilege change

---

## 5) Containment Decision (Minimal + Reversible)
**Goal:** stop the activity without destroying evidence.

Containment options (choose the smallest effective action):
- block source (firewall rule)
- isolate host/VM/network segment
- stop/disable a service temporarily
- disable an account / reset creds (lab equivalent if applicable)
- rate-limit / temporary deny rule (for noisy probes)

Always capture evidence first if practical.

---

## 6) Eradication / Hardening
**Goal:** remove the cause and reduce repeatability.

Examples:
- patch/update vulnerable component
- remove malicious artifact (file/task/user)
- tighten configuration (auth, exposed ports, access controls)
- improve detection fidelity (reduce noise, add correlation, add a new data source)

---

## 7) Recovery
**Goal:** return to normal operations and verify.

- restore service/host to baseline state
- confirm normal telemetry patterns return
- confirm containment controls are removed or made permanent intentionally

---

## 8) Close-Out (Lessons Learned)
**Goal:** every case improves the lab.

Record:
- what worked (telemetry, dashboards, correlation)
- what didn’t (visibility gaps, noisy alerting, missing logs)
- one concrete improvement item:
  - new detection, new dashboard panel, better field extraction, better logging, or tighter config

---

# Evidence Pack (Attach to Every Case/IR Report)
Minimum artifacts:
- Screenshot: initial trigger view (alert/panel/spike)
- Screenshot: one expanded raw event (the “why”)
- Snippet/screenshot: source-of-truth validation (endpoint/app/service logs)
- One-paragraph conclusion:
  - what happened
  - whether it succeeded
  - what I did (or would do in a real org)

---

# Cyberlab Pivot Pattern (Tool-Agnostic)
Pivot logic regardless of tools:
1) Summary view → raw events
2) Raw events → scope (who/what/when/how much)
3) Scope → source-of-truth validation
4) Validation → decision (blocked / possible / confirmed)
5) Decision → containment + hardening + close-out