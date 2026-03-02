import json
from datetime import datetime

def log_case(patient_id, output):
    with open("audit_log.jsonl", "a") as f:
        f.write(json.dumps({
            "timestamp": str(datetime.utcnow()),
            "patient_id": patient_id,
            "output": output
        }) + "\n")