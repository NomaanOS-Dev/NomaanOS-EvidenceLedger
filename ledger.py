import hashlib
import json
from typing import List, Dict, Any

class EvidenceLedger:
    """
    Append-Only Cryptographic Evidence Ledger
    """
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []

    def record_evidence(self, artifact_name: str, payload_hash: str) -> Dict[str, Any]:
        previous_hash = self.chain[-1]["current_hash"] if self.chain else "0" * 64
        record = {
            "index": len(self.chain) + 1,
            "artifact": artifact_name,
            "payload_hash": payload_hash,
            "previous_hash": previous_hash
        }
        # Compute block hash
        block_string = json.dumps(record, sort_keys=True).encode()
        record["current_hash"] = hashlib.sha256(block_string).hexdigest()
        self.chain.append(record)
        return record

if __name__ == "__main__":
    ledger = EvidenceLedger()
    print("Ledger Test Entry:", ledger.record_evidence("kernel_telemetry.log", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"))
