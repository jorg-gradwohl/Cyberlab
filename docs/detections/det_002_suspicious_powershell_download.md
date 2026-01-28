# DET-002 Suspicious PowerShell Download/Exec (Sysmon EID 1)

This detection looks for **PowerShell process creation** where the command line contains common **download-and-execute** patterns (a very common attacker tradecraft style).

It is a **high-signal keyword detection** designed to surface PowerShell executions that are more likely to involve:
- downloading content from the internet
- pulling payloads into memory
- executing strings/scripts directly

---

## Data Source Used in This Detection

Windows VM (Sysmon)

- Index: `sysmon`
- EventCode: `1` (Process Create)
- Key fields used: `Image`, `CommandLine`, `User`, `ParentImage`, `ParentCommandLine`, `Hashes`

---

## SPL Used
```bash
index=sysmon EventCode=1 host=DESKTOP-VE7TDRG (Image="*\\powershell.exe" OR Image="*\\pwsh.exe")
| eval cmd=lower(coalesce(CommandLine,""))
| where
    match(cmd,"(?i)\\biwr\\b")
 OR match(cmd,"(?i)\\binvoke-webrequest\\b")
 OR match(cmd,"(?i)\\binvoke-restmethod\\b")
 OR match(cmd,"(?i)downloadstring")
 OR match(cmd,"(?i)new-object\\s+net\\.webclient")
 OR match(cmd,"(?i)\\biex\\b")
 OR match(cmd,"(?i)\\binvoke-expression\\b")
| table _time host User Image CommandLine ParentImage ParentCommandLine Hashes
| sort - _time
```

---

## SPL Breakdown (line-by-line)

- `index=sysmon EventCode=1 ...`
  Search Sysmon **Process Create** events (EID 1).

- `host=DESKTOP-VE7TDRG`
  Restrict this detection to my Windows telemetry VM host for now.

- `(Image="*\\powershell.exe" OR Image="*\\pwsh.exe")`
  Only include PowerShell executions:
  - `powershell.exe` = Windows PowerShell
  - `pwsh.exe` = PowerShell 7+

- `| eval cmd=lower(coalesce(CommandLine,""))`
  Create a helper field `cmd` from `CommandLine`:
  - `coalesce(CommandLine,"")` ensures `cmd` is never null (empty string if missing)
  - `lower(...)` makes matching consistent regardless of upper/lower case in the command line

- `| where match(cmd, ...) OR match(cmd, ...) ...`
  Keep only events where the command line matches known suspicious patterns.

  Notes:
  - `match()` uses regex matching.
  - `(?i)` makes the regex case-insensitive (so the match still works even if the command line uses different casing).
  - `\\b` means “word boundary”, so `\\biwr\\b` matches `iwr` as a standalone token, not as part of another word.

- Suspicious patterns used (and why):
  - download methods:
    - `iwr`, `Invoke-WebRequest` = web download via PowerShell
    - `Invoke-RestMethod` = common for pulling payloads/data from APIs
    - `DownloadString` = classic “download script as a string”
    - `New-Object Net.WebClient` = older but very common download pattern
  - execution methods:
    - `iex`, `Invoke-Expression` = execute strings directly (often paired with downloads)

- `| table ...`
  Output the key triage fields so you can quickly see:
  - what ran, who ran it, how it was launched, and the full command line

- `| sort - _time`
  Show newest matches first.

---

## Testing / Validation (Reproducible)

Goal:
Generate a safe PowerShell download-style command and confirm the detection returns an event.

Safe test example:

Invoke-WebRequest (“iwr”) to a harmless site:

```bash
powershell -NoProfile -Command "iwr http://example.com -UseBasicParsing | select -First 1"
```
- `-NoProfile` - Tells PowerShell not to load the PowerShell profile scripts (anything in $PROFILE that could change behaviour or add aliases/modules). This makes the command more predictable and repeatable for testing.
- `-Command " ... "` - Runs the quoted text as a PowerShell command and then exits.
- `-UseBasicParsing` - Forces a simpler parsing mode. Doesn’t hurt for a basic test. Not necesseraily needed
- `| select -First 1` - Pipes the web request output into Select-Object and returns only the first item / first object.
In practice: it keeps output small so I'm not dumping a huge response to the terminal.

Expected result:
- Sysmon EID 1 event exists for PowerShell
- CommandLine includes `iwr` or `Invoke-WebRequest`
- Detection returns the event in Splunk with User/Parent context

---

## Evidence (Example)

Screenshot:
![DET-002 Example Result](../../assets/splunk_detection_002.png)

## Why this is valuable

PowerShell is one of the most common tools abused for:
- downloading payloads
- running code directly in memory
- executing attacker-controlled strings/scripts

This detection highlights “download/exec style” PowerShell runs early, and the output provides enough context to quickly pivot into:
- parent/child process chain review
- which user launched it
- follow-on network/DNS activity (via Sysmon EID 3/22 panels)