# DET-004 CertUtil Suspicious Usage (Sysmon EID 1)

This detection looks for **certutil.exe process creation** where the command line suggests **download or encode/decode behaviour**. CertUtil is a legitimate Windows utility mainly used to work with certificates and cryptography, but attackers commonly abuse it as a built-in “living off the land” tool to:
- download files (`-urlcache`, `-split`, `-f`)
- decode or encode payloads (`-decode`, `-encode`)
- pull content directly from URLs (`http://`, `https://`)

This detection looks for **CertUtil process creation** where the command line suggests **download** or **encode/decode** activity.

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
| eval img=lower(coalesce(Image,"")), cmd=lower(coalesce(CommandLine,""))
| where like(img,"%\\certutil.exe")
  AND (
    like(cmd,"% -urlcache %") OR like(cmd,"% -split %") OR like(cmd,"% -f %")
    OR like(cmd,"% -decode %") OR like(cmd,"% -encode %")
    OR like(cmd,"%http://%") OR like(cmd,"%https://%")
  )
| table _time host User Image CommandLine ParentImage ParentCommandLine Hashes
| sort - _time
```

---

## SPL Breakdown (line-by-line)

- `index=sysmon EventCode=1 earliest=-24h`
  Search Sysmon **Process Create** events (EID 1) from the last 24 hours.

- `| eval img=lower(coalesce(Image,"")), cmd=lower(coalesce(CommandLine,""))`
  Create two helper fields for consistent matching:
  - `coalesce(...,"")` ensures the fields never become null (empty string if missing)
  - `lower(...)` makes matching case-insensitive without needing extra flags

- `| where like(img,"%\\certutil.exe")` - Keep only process creations where the executed binary is `certutil.exe`.

- `AND ( ... )` - Further restrict to CertUtil executions that include suspicious keywords/flags commonly seen in attacker tradecraft:

  - Download-related options:
    - `-urlcache`, `-split`, `-f`

  - Encoding/decoding options:
    - `-decode`, `-encode`

  - URL indicators:
    - `http://`, `https://`

  This reduces noise by ignoring “normal” CertUtil usage that does not look like file transfer or payload handling.

- `| table _time host User Image CommandLine ParentImage ParentCommandLine Hashes`
  Output the key triage fields so you can quickly see:
  - what ran and the exact command line
  - which user and host ran it
  - how it was launched (parent process context)
  - hashes for binary identification

- `| sort - _time`
  Show newest matches first.

---

## Testing / Validation (Reproducible)

Safe offline certutil test (Encode + Decode)

This test generates harmless certutil activity that still matches the detection (because the SPL also flags `-encode` / `-decode`), without using URL download features that can be blocked by Defender.

Command(s):

1) `echo cyberlab_test> "%TEMP%\certutil_in.txt"`
    - `echo cyberlab_test` - Creates a tiny, harmless test string.
    - `>` - Redirects that output into a file (creates/overwrites the file).
    - `"%TEMP%\certutil_in.txt"` - Writes the file into your Temp directory (for your user).
    - `%TEMP%` expands to something like: `C:\Users\win10telemetry\AppData\Local\Temp`

2) `certutil.exe -encode "%TEMP%\certutil_in.txt" "%TEMP%\certutil_out.b64"`
    - `certutil.exe` - Built-in Windows certificate utility (often abused as a LOLBin).
    - `-encode` - Converts the input file into Base64 text (writes a .b64 output file). Attackers sometimes use this to wrap data/payloads in Base64.
    - `"%TEMP%\certutil_in.txt"` - Input file to encode (the harmless text I created).
    - `"%TEMP%\certutil_out.b64"` - Output Base64 file written to Temp.

3) `certutil.exe -decode "%TEMP%\certutil_out.b64" "%TEMP%\certutil_out_decoded.txt"`
    - `-decode` - Converts Base64 content back into the original raw file content.
    - `"%TEMP%\certutil_out.b64"` - Input Base64 file to decode.
    - `"%TEMP%\certutil_out_decoded.txt"` - Output decoded file written to Temp.

4) `type "%TEMP%\certutil_out_decoded.txt"`
    - `type` - Prints the file contents to confirm the decode worked.
    - Expected output should include: `cyberlab_test`

Expected result in Splunk:
- Sysmon EID 1 shows `Image=...\\certutil.exe`
- CommandLine contains `-encode` and/or `-decode`
- The detection returns the event with User/Parent context

---

## Evidence (Example)

Screenshot:
![DET-004 Example Result](/assets/splunk_detection_004.png)

---

## Why this is valuable

CertUtil is frequently abused because it’s:
- built into Windows (trusted, always present)
- often allowed where third-party tools are blocked
- capable of downloading content and transforming data (encode/decode)

This detection gives you quick visibility into certutil executions that resemble “download/transform” activity, with enough context to quickly review:
- parent/child process chain (how it was launched)
- user context (who ran it)
- related network and DNS activity in the Sysmon dashboard (EID 3 / 22), if I need extra surrounding telemetry