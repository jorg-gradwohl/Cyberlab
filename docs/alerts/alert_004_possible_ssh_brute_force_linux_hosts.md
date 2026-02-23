# ALERT-004 Possible SSH Brute Force (Linux Hosts) (≥5 failed logins / 5m)

This alert detects **possible SSH brute force / password guessing** activity against **Linux hosts** in Cyberlab by identifying a **high rate of failed SSH logins** from the same `src_ip` within a short time window.

It is designed to be **simple, reproducible, and SOC-actionable**: one `src_ip` generating **≥5 failed SSH logins** against a Linux host/user within **5 minutes**.

---

## Data Source Used in This Alert

Linux authentication logs (auth.log) forwarded into Splunk

- Index: `endpoints`
- Sourcetype: `auth`
- Source: `/var/log/auth.log` (per host)
- Key fields used:
  - `host` (Splunk host field = target Linux host)
  - `src_ip` (extracted from auth log line)
  - `dest_user` (extracted from auth log line; username being targeted)
  - `_time` (event timestamp)

**Note:**
- This alert relies on my custom field extractions for `src_ip` and `dest_user` from the auth log format (e.g., “Failed password for <user> from <ip> ...”).

---

## Alert Logic

Trigger behaviour:
- Time window: **Last 5 minutes** (set in the alert UI)
- Schedule: `*/5 * * * *` (runs every 5 minutes)
- Trigger condition: **Number of results > 0**
- Trigger mode: **Once** (one alert per run if anything matches)

Important:
- The **5-minute “bucket”** is created by the alert **Time Range** setting and the SPL `bin _time span=5m`
- Threshold logic is enforced in SPL (`failed_logins >= 5`)

---

## SPL Used
```bash
index=endpoints sourcetype=auth *Failed* "*ssh*"
| eval dest_host=host
| bin _time span=5m
| stats count as failed_logins by _time src_ip dest_host dest_user
| where failed_logins >= 5
| sort 0 -failed_logins
```

---

## SPL Breakdown

- `index=endpoints sourcetype=auth *Failed* "*ssh*"` - Filters to Linux auth events (`sourcetype=auth`) that contain:
  - `Failed` (failed authentication)
  - `ssh` (SSH-related events)

- `| eval dest_host=host` - Creates an explicit `dest_host` field so it’s unambiguous that `host` is the **target** system (not the attacker).

- `| bin _time span=5m` - Buckets events into **5-minute windows** so I can count failed logins per attacker/target/user in each window.

- `| stats count as failed_logins by _time src_ip dest_host dest_user`  
  Aggregates into one row per:
  - time bucket (`_time`)
  - attacker (`src_ip`)
  - target host (`dest_host`)
  - targeted username (`dest_user`)  
  Produces `failed_logins` = number of failures for that combination in the window.

- `| where failed_logins >= 5`  
  Detection threshold: only keep rows that meet the brute-force-style rate (≥5 failures per 5 minutes).

- `| sort 0 -failed_logins`  
  Sorts by highest failure count first (`0` = no result truncation).

---

## Alert Configuration (Scheduled Search)

### Key Settings (and why they exist)

- Alert type: Scheduled
- Schedule: Run on Cron Schedule: `*/5 * * * *` (runs every 5 minutes)
- Time Range: Last 5 minutes (keeps the search tightly scoped and reduces noise)
- Trigger alert when: Number of Results is greater than 0  
  (The SPL already enforces `failed_logins >= 5`, so any returned row is alert-worthy.)
- Trigger: Once  
  One alert per scheduled run, even if multiple rows match (multiple attacker/host/user combinations).
- Expires: 24 hours  
  Keeps the triggered alert visible for review without cluttering the queue forever.

### Trigger Actions

- Add to Triggered Alerts (Severity: Medium)  
  Puts the alert into a SOC-style queue view for triage.
- Log Event  
  Writes a summary event when the alert fires (useful for correlation and audit trail).

---

## Why this is valuable

This alert is intended to demonstrate a realistic SOC pattern:

- SSH password guessing is common lateral-movement / initial-access behaviour.
- Auth logs are the source-of-truth for authentication outcomes.
- The output gives clear triage pivots:
  - which source is attacking (`src_ip`)
  - which host is targeted (`dest_host`)
  - which account is being guessed (`dest_user`)
  - how intense the burst was (`failed_logins`)
  - when it happened (`_time`)

![ALERT_004](/assets/alert_004.png)