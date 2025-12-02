# NGINX Setup — Ubuntu

**Host:** ThinkPad (Branch Office Simulation)  
**OS:** Ubuntu 24.04 LTS

---

## 1) Install NGINX (Ubuntu repo)

```bash
sudo apt update && sudo apt install -y nginx
```

Verify installation:

```bash
nginx -v
sudo systemctl status nginx
```

If the service shows **active (running)**, NGINX is working.

Open in browser:

```text
http://<ThinkPad-IP>/
```

---

## 2) Create a Simple Test Page

NGINX creates a default index file. Let's overwrite the default index file:

```bash
sudo nano /var/www/html/index.html
```

Example content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ThinkPad Branch Office - Test Page</title>
</head>
<body>
  <h1>ThinkPad Branch Office - Test Page</h1>
  <p>This is a small internal site served by NGINX on the branch office machine.</p>
</body>
</html>
```

Save and reload NGINX (optional):

```bash
sudo systemctl reload nginx
```

---

## 3) NGINX Log Locations

NGINX writes logs to:

```bash
/var/log/nginx/access.log
/var/log/nginx/error.log
```

Quick check:

```bash
sudo tail -20 /var/log/nginx/access.log
```

You should see requests there.

---

## 4) Synthetic Web Traffic Script (to generate logs)

Create a small script that produces predictable traffic:

```bash
nano ~/synthetic_nginx_hits.sh
```

Paste:

```bash
#!/bin/bash

# Synthetic hits for access.log
curl -s -o /dev/null http://<ThinkPad-IP>/
curl -s -o /dev/null http://<ThinkPad-IP>/no-such-page
```
- _(#!/bin/bash is a shebang line that tells Linux to run the script using the Bash interpreter instead of the default shell.)_
- _(-s → silent mode, -o /dev/null → write output to /dev/null)_

Make it executable:

```bash
chmod +x ~/synthetic_nginx_hits.sh
```

Test once:

```bash
./synthetic_nginx_hits.sh
sudo tail -10 /var/log/nginx/access.log
```

You should see both `/` (200) and `/no-such-page` (404) requests.

---

## 5) Cron Job (runs every 2 minutes)

Open crontab:

```bash
crontab -e
```
(-e → edit)

Add:

```text
*/2 * * * * /home/jorg/synthetic_nginx_hits.sh
```
_(In a cron expression, the five * symbols represent minutes, hours, day-of-month, month, and day-of-week, and together they define when and how often the scheduled job will run. * → means “every”. */2 → means “every 2”)_

This generates:

- A normal **200** hit  
- A **404** hit  
- Both every two minutes

---

## 6) Splunk Forwarding (inputs.conf on ThinkPad UF)

Edit the Splunk Universal Forwarder inputs:

```bash
sudo nano /opt/splunkforwarder/etc/system/local/inputs.conf
```

Add:

```text
[monitor:///var/log/nginx/access.log]
index = branch_office
sourcetype = nginx_access
disabled = false

[monitor:///var/log/nginx/error.log]
index = branch_office
sourcetype = nginx_error
disabled = false
```

Restart the UF:

```bash
sudo /opt/splunkforwarder/bin/splunk restart
```

---

## 7) Verification in Splunk

In Splunk Search:

```text
index=branch_office sourcetype=nginx_access earliest=-30m
```

You should see:

- `GET /` events
- `GET /no-such-page` events
- index = `branch_office`

This confirms:

- NGINX running  
- Synthetic traffic generated regularly  
- Logs forwarded into the `branch_office` index with clear sourcetypes 