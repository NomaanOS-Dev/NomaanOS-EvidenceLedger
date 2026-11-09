import json
import os
from ledger import EvidenceLedger


class LedgerIntegrityError(SecurityError if "SecurityError" in globals() else RuntimeError):
    """Raised when on-disk ledger cryptographic verification fails."""
    pass


class PersistentEvidenceLedger(EvidenceLedger):
    def __init__(self, storage_path: str = "evidence_store.jsonl", auto_verify: bool = True):
        super().__init__()
        self.storage_path = os.path.expanduser(storage_path)
        self._load_from_disk()
        if auto_verify and not self.verify_chain():
            self._chain.clear()
            raise LedgerIntegrityError(
                f"[CRITICAL] Ledger integrity invariant violated in '{self.storage_path}'. "
                "Cold storage hash-chain mismatch detected."
            )

    def _load_from_disk(self) -> None:
        if not os.path.exists(self.storage_path):
            return
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    record_dict = json.loads(clean_line)
                    self._chain.append(record_dict)
                except json.JSONDecodeError as err:
                    raise LedgerIntegrityError(
                        f"Malformed JSON at line {line_no} in '{self.storage_path}': {err}"
                    )

    def record_evidence(self, artifact_name: str, payload_hash: str):
        record_dict = super().record_evidence(artifact_name, payload_hash)
        with self._lock:
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record_dict, sort_keys=True) + "\n")
        return record_dict
