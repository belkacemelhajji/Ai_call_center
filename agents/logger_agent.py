import json
import os
import uuid
from datetime import datetime

ARTIFACTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "artifacts"
)

class LoggerAgent:
    def __init__(self):
        self.call_id = f"CALL-{str(uuid.uuid4())[:8].upper()}"
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logs = []

    def log(self, event_type: str, data: dict):
        """Log any event"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event_type,
            "data": data
        }
        self.logs.append(entry)
        print(f"📁 Logger: [{event_type}] logged")

    def save_artifact(self, customer_info: dict = None, escalated: bool = False):
        """Save full call artifact to file"""
        artifact = {
            "call_id": self.call_id,
            "start_time": self.start_time,
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "customer": customer_info,
            "escalated": escalated,
            "total_events": len(self.logs),
            "logs": self.logs
        }

        # Create artifacts folder if needed
        os.makedirs(ARTIFACTS_PATH, exist_ok=True)
        filepath = os.path.join(ARTIFACTS_PATH, f"{self.call_id}.json")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(artifact, f, ensure_ascii=False, indent=2)

        print(f"✅ Logger: Artifact saved → {filepath}")
        return filepath

if __name__ == "__main__":
    logger = LoggerAgent()
    logger.log("call_started", {"channel": "voice"})
    logger.log("intent_detected", {"intent": "lookup_customer"})
    logger.log("tool_called", {"tool": "lookup_customer", "result": "success"})
    logger.save_artifact(
        customer_info={"name": "Ahmed Benali", "id": "C001"},
        escalated=False
    )