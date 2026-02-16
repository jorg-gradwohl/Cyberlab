# ALERT-003 Juice Shop — Possible Brute Force (≥10 login requests / 5m)

This alert detects a **burst of authentication attempts** to OWASP Juice Shop by identifying a **high volume of HTTP requests** to `/rest/user/login` within a short time window.

Important: OWASP Juice Shop (and many modern web apps) may return **HTTP 200** even when credentials are wrong (with the failure indicated in the response body). Because Suricata HTTP logs typically **do not include the response body**, this alert is intentionally **status-agnostic** and focuses on **behaviour** (request rate), not confirmed success/failure.

It is designed to be **simple, reproducible, and SOC-actionable**: one `src_ip` generating ≥10 login requests within a 5-minute window.

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
    index=ids sourcetype=suricata:eve event_type=http http.url="/rest/user/login"
    | stats 
        count as attempts 
        earliest(_time) as first 
        latest(_time) as last 
        values(http.status) as statuses
        values(src_port) as src_ports 
        values(http.http_user_agent) as user_agents 
        by src_ip dest_ip dest_port http.url
    | where attempts>=10
    | eval 
        first=strftime(first,"%d/%m/%Y %H:%M:%S"), 
        last=strftime(last,"%d/%m/%Y %H:%M:%S"),
        statuses=mvjoin(statuses,", "),
        src_ports=mvjoin(src_ports,", "),
        user_agents=mvjoin(user_agents," | ")
    | table src_ip dest_ip dest_port http.url attempts first last statuses src_ports user_agents
    | sort - attempts
```

---

## SPL Breakdown (line-by-line)

- `index=ids sourcetype=suricata:eve event_type=http http.url="/rest/user/login"` - Filters Suricata HTTP logs to requests hitting the Juice Shop login endpoint.
- `| stats count as attempts earliest(_time) as first latest(_time) as last values(http.status) as statuses values(src_port) as src_ports values(http.http_user_agent) as user_agents by src_ip dest_ip dest_port http.url`  
  Aggregates into one row per `src_ip` (per dest/URL) and calculates:
  - `attempts`: number of login endpoint requests in the time window
  - `first` / `last`: first and last request timestamps
  - `statuses`: status codes observed (useful for triage, not the primary signal)
  - `src_ports`: list of client source ports observed (often changes during bursts)
  - `user_agents`: UA string(s) observed for fast triage

- `| where attempts>=10` - Detection threshold: trigger only when a single source generates **≥10 login requests** in the window.

- `| eval first=strftime(...), last=strftime(...), statuses=mvjoin(...), src_ports=mvjoin(...), user_agents=mvjoin(...)` - “Prettifies” the output:
  - UK datetime format: `dd/mm/yyyy hh:mm:ss`
  - joins multi-value `statuses`, `src_ports`, and `user_agents` into readable strings

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

- Some web apps (including Juice Shop) can return `200 OK` even when authentication fails (failure indicated in the response body).
- Suricata HTTP logs usually do not capture response bodies, so status codes alone are not a reliable “failure” signal.
- Instead, this alert detects the **behaviour**: repeated login attempts to a single endpoint within a tight time window.

It’s high signal, easy to explain, and gives clear pivots:
- which `src_ip` is doing it,
- how intense the burst is (`attempts`),
- timeframe (`first`/`last`),
- client characteristics (`user_agents`, `src_ports`),
- observed HTTP statuses (`statuses`) for additional context.