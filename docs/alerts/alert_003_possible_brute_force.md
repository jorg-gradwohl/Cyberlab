# ALERT-003 Juice Shop — Possible Brute Force (≥10 failed logins / 5m)

This alert detects a **burst of failed authentication attempts** to OWASP Juice Shop by identifying **HTTP 401 responses** to `/rest/user/login` at a rate consistent with **password guessing / brute force** activity.

It is designed to be **simple, reproducible, and SOC-actionable**: one `src_ip` generating ≥10 failures within a 5-minute window.

---

## Data Source Used in This Alert

Suricata (EVE JSON) on SOA

- Index: `ids`
- Sourcetype: `suricata:eve`
- Event type: `http`
- Key fields used: `src_ip`, `src_port`, `dest_ip`, `dest_port`, `http.url`, `http.status`, `http.http_user_agent`, `_time`

---

## Alert Logic

Trigger behaviour:
- Time window: **Last 5 minutes** (set in the alert UI)
- Schedule: `*/5 * * * *` (runs every 5 minutes)
- Trigger condition: **Number of results > 0**
- Trigger mode: **Once**

Important:
- The **5-minute “bucket”** is created by the **alert Time Range setting**, not inside the SPL

---

## SPL Used
```bash
index=ids sourcetype=suricata:eve event_type=http http.url="/rest/user/login" http.status=401
| stats 
    count as attempts 
    earliest(_time) as first 
    latest(_time) as last 
    values(src_port) as src_ports 
    values(http.http_user_agent) as user_agents 
    by src_ip dest_ip dest_port http.url
| where attempts>=10
| eval 
    first=strftime(first,"%d/%m/%Y %H:%M:%S"), 
    last=strftime(last,"%d/%m/%Y %H:%M:%S"),
    src_ports=mvjoin(src_ports,", "),
    user_agents=mvjoin(user_agents," | ")
| table src_ip dest_ip dest_port http.url attempts first last src_ports user_agents
| sort - attempts
```
---

## SPL Breakdown (line-by-line)

- `index=ids sourcetype=suricata:eve event_type=http http.url="/rest/user/login" http.status=401` - Filters Suricata HTTP logs to **failed Juice Shop login attempts** (401s) on `/rest/user/login`.

- `| stats count as attempts earliest(_time) as first latest(_time) as last values(src_port) as src_ports values(http.http_user_agent) as user_agents by src_ip dest_ip dest_port http.url` - Aggregates into one row per `src_ip` (per dest/URL) and calculates:
  - `attempts`: number of failures in the time window
  - `first` / `last`: first and last failure timestamps
  - `src_ports`: list of client source ports observed (often changes during bursts)
  - `user_agents`: UA string(s) observed for fast triage

- `| where attempts>=10` - Detection threshold: trigger only when a single source generates **≥10 failed logins** in the window.

- `| eval first=strftime(...), last=strftime(...), src_ports=mvjoin(...), user_agents=mvjoin(...)` - “Prettifies” the output:
  - UK datetime format: `dd/mm/yyyy hh:mm:ss`
  - joins multi-value `src_ports` into a single comma-separated string
  - joins multi-value `user_agents` into a single readable string

- `| table ...` - Limits output to the exact fields you want shown when the alert fires.

- `| sort - attempts` - Highest attempt count first.

---

## Alert Configuration (Scheduled Search)

### Key Settings (and why they exist)

- **Alert type**: Scheduled
- **Schedule**: Run on Cron Schedule: `*/5 * * * *` (runs every 5 minutes)
- **Time Range**: Last 5 minutes (this is the actual “bucket” for counting attempts)
- **Trigger alert when**: Number of Results **is greater than** 0. The SPL already enforces `attempts>=10`, so any returned row is alert-worthy.
- **Trigger**: Once - One alert per scheduled run (even if multiple source IPs meet the condition).
- **Throttle**: Probably a good idea when doing a lot of testing
- **Expires**: 24 hours - Keeps the triggered alert visible for review without cluttering the queue forever.
- **Trigger action**: Add to Triggered Alerts (Severity: Medium): This puts it into a SOC-style queue view.

---

## Why this is valuable

This alert demonstrates a practical SOC pattern:

- I cannot rely on Suricata signatures for “password guessing” payloads (often in POST bodies / app logic),
- but I can detect the **behaviour**: repeated auth failures to a login endpoint within a tight time window.

It’s high signal, easy to explain, and gives clear pivots:
- which `src_ip` is doing it,
- how intense the burst is (`attempts`),
- timeframe (`first`/`last`),
- client characteristics (`user_agents`, `src_ports`).