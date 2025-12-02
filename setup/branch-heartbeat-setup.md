# Branch Heartbeat Setup – ThinkPad (Branch Office)

The branch heartbeat provides a lightweight “I am alive” signal from the ThinkPad (branch office node). 
It writes a timestamped log entry into a dedicated file under `/var/log/cyberlab`, and Splunk ingests this log for monitoring and dashboards.

---
## 1) Heartbeat Script

```bash
nano ~/branch_heartbeat.sh
```
Paste:
```bash
#!/bin/bash
echo "$(date) - Branch Office heartbeat OK" >> /var/log/cyberlab/branch-heartbeat.log
```
Make executable:
```bash
chmod +x ~/branch_heartbeat.sh
```
## 2) Cron Job (runs every minute)

```bash
crontab -e
```
Add:
```
*/1 * * * * /home/jorg/branch_heartbeat.sh
```
## 3) Splunk Forwarding
Edit:
```bash
sudo nano /opt/splunkforwarder/etc/system/local/inputs.conf
```
Add:
```bash
[monitor:///var/log/cyberlab/branch-heartbeat.log]
index = branch_office
sourcetype = branch_heartbeat
disabled = false
```
Restart forwarder:
```bash
sudo /opt/splunkforwarder/bin/splunk restart
```
## Result:
The ThinkPad now produces predictable heartbeat events available in Splunk under:
```bash
index=branch_office sourcetype=branch_heartbeat
```
These events confirm the branch office node is online and functioning, and they appear alongside SMB and NGINX telemetry in dashboards.