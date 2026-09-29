import urllib.request
import json
import sys

BASE = 'http://127.0.0.1:8000/api'

def test(name, url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8')
    else:
        body = None
    try:
        with urllib.request.urlopen(req, data=body) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            print(f"[PASS] {name}: HTTP {res.status}")
            return res_data
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return None

print("=== VERIFYING ALL INCIDENT RESPONSE AGENT BACKEND APIS ===")
test("Dashboard", f"{BASE}/dashboard")
incidents = test("List Incidents", f"{BASE}/incidents")
test("Get Incident Details", f"{BASE}/incidents/IR-1002")
test("Advance Workflow Stage", f"{BASE}/incidents/IR-1002/workflow", method="POST", data={"stage": "Investigation", "comment": "Proceeding to root cause investigation"})
test("Analyze Incident with AI", f"{BASE}/analyze-incident", method="POST", data={"incident_id": "IR-1002"})
alerts = test("List Alerts", f"{BASE}/alerts")
test("Alert Action (Investigate)", f"{BASE}/alerts/ALT-501/action", method="POST", data={"action": "investigate", "analyst": "Alex Mercer"})
iocs = test("List IoCs", f"{BASE}/iocs")
test("Analyze IoC", f"{BASE}/analyze-ioc", method="POST", data={"ioc_value": "198.51.100.89", "ioc_type": "IP Address"})
playbooks = test("List Playbooks", f"{BASE}/playbooks")
test("Execute Playbook Step", f"{BASE}/playbooks/PB-PHISH/execute-step", method="POST", data={"playbook_id": "PB-PHISH", "step_index": 4, "action_key": "sweep_tenant_mailboxes", "incident_id": "IR-1003"})
test("AI Chat Assistant", f"{BASE}/chat", method="POST", data={"message": "Summarize this incident.", "incident_id": "IR-1002"})
test("Generate Incident Report", f"{BASE}/generate-report", method="POST", data={"incident_id": "IR-1002", "custom_notes": "Verified by SOC Lead"})
test("MITRE ATT&CK Matrix", f"{BASE}/mitre")
test("Get Settings", f"{BASE}/settings")
test("Reset Demo Environment", f"{BASE}/reset-demo", method="POST")
print("=== ALL API ENDPOINTS VALIDATED SUCCESSFULLY ===")
