# DET-003 BITSAdmin Transfer (Sysmon EID 1)

This detection looks for **BITSAdmin process creation** where the command line contains common **BITS job / transfer actions**.

BITSAdmin is a Windows **LOLBIN** that can be abused to download files using the Background Intelligent Transfer Service (BITS). Even though BITS itself is legitimate, **interactive use of bitsadmin.exe** is unusual in normal environments and is a common tradecraft pattern.

---

## Data Source Used in This Detection

Windows VM (Sysmon)

- Index: `sysmon`
- EventCode: `1` (Process Create)
- Key fields used: `Image`, `CommandLine`, `User`, `ParentImage`, `ParentCommandLine`, `Hashes`

---

## SPL Used
```bash
index=sysmon EventCode=1 Image="*\\bitsadmin.exe"
| eval cmd=lower(coalesce(CommandLine,""))
| where like(cmd,"%/transfer%")
   OR like(cmd,"%/addfile%")
   OR like(cmd,"%/create%")
   OR like(cmd,"%/resume%")
   OR like(cmd,"%/setnotifycmdline%")
   OR like(cmd,"%/setcredentials%")
| table _time host User Image CommandLine ParentImage ParentCommandLine Hashes
| sort - _time
```

---

## SPL Breakdown (line-by-line)

- `index=sysmon EventCode=1 Image="*\\bitsadmin.exe"`
  Search Sysmon **Process Create** events (EID 1) where the executed image is `bitsadmin.exe`.

- `| eval cmd=lower(coalesce(CommandLine,""))`
  Create a helper field `cmd` from `CommandLine`:
  - `coalesce(CommandLine,"")` ensures `cmd` is never null (empty string if missing)
  - `lower(...)` makes matching consistent regardless of upper/lower case in the command line

- `| where like(cmd, ...) OR like(cmd, ...) ...` - Keep only BITSAdmin executions where the command line contains common **job/transfer-related actions**.

  Notes:
  - `like()` is a wildcard match function.
  - `%` means “anything before/after”, so the keyword can appear anywhere in the command line.

  Suspicious actions used (and why):
  - `/transfer` = create and run a transfer job in one step (very common in “download a file” abuse)
  - `/addfile` = add a file to a job (building the transfer job)
  - `/create` = create a new job
  - `/resume` = start/resume a job (often the step that actually begins transfer)
  - `/setnotifycmdline` = run a command when the job completes (higher-signal abuse pattern)
  - `/setcredentials` = use alternate credentials for a job (can be abused in some scenarios)

- `| table ...`
  Output the key triage fields so you can quickly see:
  - what ran, who ran it, how it was launched, and the full command line

- `| sort - _time`
  Show newest matches first.

---

## Testing / Validation (Reproducible)

Goal:
Generate a safe BITSAdmin execution and confirm the detection returns a Sysmon EID 1 event.

Safe test example (downloads a harmless page):
```bash
bitsadmin /transfer CYBERLAB_BITS_TEST /download /priority normal http://example.com "%USERPROFILE%\Downloads\cyberlab_bitsadmin_test.html"
```

- `/transfer` - Creates a new BITS transfer job and starts it immediately (one-shot style).
- `CYBERLAB_BITS_TEST` - The job name (an arbitrary label I chose). It helps identify this transfer in logs.
- `/download` - Tells BITS this is a download job (from a remote URL to a local file).
- `/priority normal` - Sets the job priority to normal (BITS supports priorities; normal is the default, “non-special” setting).
- `http://example.com/` - The source URL to download from (harmless test site in this case).
- `"%USERPROFILE%\Downloads\cyberlab_bitsadmin_test.html"`
  The destination file path on the local machine.
  - %USERPROFILE% expands to the current user’s profile directory (e.g. C:\Users\win10telemetry).
  - Quotes ensure the full path is treated as a single argument.

Expected result:
- Sysmon EID 1 event exists for `C:\Windows\System32\bitsadmin.exe`
- CommandLine contains `/transfer` (and the URL + destination path)
- Detection returns the event in Splunk with User/Parent context

Note:
If BITSAdmin fails to actually download (network restriction / policy / auth), I can still get the Sysmon EID 1 process creation event, which is enough to validate this detection.

---

## Evidence (Example)

Screenshot:
![DET-003 Example Result](/assets/splunk_detection_003.png)

---

## Why this is valuable

BITSAdmin is a well-known LOLBIN used to:
- download payloads without adding third-party tools
- blend into “legitimate Windows” tooling
- stage files before execution

This detection highlights BITSAdmin transfer-style usage early, and the output provides enough context to quickly pivot into:
- parent/child process chain review
- which user launched it
- any follow-on activity from the downloaded file (if it was executed)