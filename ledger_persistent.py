import json
import os
from ledger import EvidenceLedger

class PersistentEvidenceLedger(EvidenceLedger):
    def __init__(self, storage_path="evidence_store.jsonl"):
        super().__init__()
        self.storage_path = os.path.expanduser(storage_path)
        self._load_from_disk()

    def _load_from_disk(self):
        if not os.path.exists(self.storage_path):
            return
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    record_dict = json.loads(line)
                    # Existing internal chain list me dict append karein
                    self._chain.append(record_dict)

    def record_evidence(self, evidence_type: str, payload_hash: str):
        record_dict = super().record_evidence(evidence_type, payload_hash)
        with self._lock:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record_dict) + "\n")
        return record_dict

if __name__ == "__main__":
    test_file = "test_evidence.jsonl"
    if os.path.exists(test_file):
        os.remove(test_file)

    # 1. First run - record entry
    db = PersistentEvidenceLedger(test_file)
    rec = db.record_evidence("boot_event", "a" * 64)
    print(f"[+] Persisted Record #{rec['index']} with hash {rec['current_hash'][:16]}...")
    
    # 2. Second instance - reload from disk & verify
    db_reloaded = PersistentEvidenceLedger(test_file)
    print(f"[+] Reloaded Chain Length: {len(db_reloaded._chain)}")
    valid = db_reloaded.verify_chain()
    print(f"[+] Verification on Reloaded Disk Data: {'PASSED ✅' if valid else 'FAILED ❌'}")

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
