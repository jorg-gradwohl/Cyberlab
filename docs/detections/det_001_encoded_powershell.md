# DET-001 Encoded PowerShell (Sysmon EID 1)

This detection identifies **PowerShell executions using base64-encoded command content** (common obfuscation via `-EncodedCommand` / `-enc`).  
It is intended as a **hunt/validation search** (24h view) to quickly review encoded PowerShell activity and pivot into surrounding telemetry (parent process, user context, command line).

---

## Data Source Used in This Detection

Windows VM (Sysmon)

- Index: `sysmon`
- EventCode: `1` (Process Create)
- Key fields used: `Image`, `CommandLine`, `User`, `ParentImage`, `ParentCommandLine`, `Hashes`

---

## SPL Used
```bash
index=sysmon EventCode=1 earliest=-24h
(Image="*\\powershell.exe" OR Image="*\\pwsh.exe")
(CommandLine="*-EncodedCommand*" OR CommandLine="* -enc*" OR CommandLine="* -e *")
User!="NT AUTHORITY\\SYSTEM"
| table _time host User Image CommandLine ParentImage ParentCommandLine Hashes
| sort - _time
```

---

## SPL Breakdown (line-by-line)

- `index=sysmon EventCode=1 earliest=-24h` - Search the `sysmon` index for **Process Create** events (Sysmon Event ID 1) from the **last 24 hours**.
- `(Image="*\\powershell.exe" OR Image="*\\pwsh.exe")` - Limit results to PowerShell process executions:
  - `powershell.exe` = Windows PowerShell
  - `pwsh.exe` = PowerShell 7+
- `(CommandLine="*-EncodedCommand*" OR CommandLine="* -enc*" OR CommandLine="* -e *")` - Only keep PowerShell runs where the command line suggests **encoded execution**, using common flags:
  - `-EncodedCommand`
  - `-enc`
  - `-e` (short form)
- `User!="NT AUTHORITY\\SYSTEM"` - Exclude PowerShell launched as the local SYSTEM account to reduce noise and focus on user-context executions.
- `| table _time host User Image CommandLine ParentImage ParentCommandLine Hashes` - Output the key triage fields so you can quickly see:
  - when it ran, which host, which user, what executed, the full command line,
  - parent process context, and hashes.
- `| sort - _time` - Sort newest matching events first.

---

## Purpose

This search provides a **simple, reproducible view** of encoded PowerShell process creation in the lab so it can be:
- reviewed in bulk over a wider time range (last 24h)
- used for quick pivots into parent/child execution context
- used to confirm Sysmon logging + field extraction are working as expected

---

## Evidence (Example)

Screenshot:
![DET-001 Example Results](../../assets/splunk_detection_001.png)

---

## Related Alert

This detection is also implemented as a scheduled alert:

- [ALERT-001 Encoded PowerShell (Sysmon EID 1)](../../docs/alerts/alert_001_encoded_powershell.md)