import hashlib
import json
import re
from threading import RLock
from typing import Any, Dict, List, Tuple

_HEX_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


class EvidenceLedger:
    """In-memory hash-linked evidence ledger with chain verification.

    Persistence, authenticated checkpoints, and key management are deployment
    responsibilities; this class does not by itself establish legal admissibility.
    """

    def __init__(self) -> None:
        self._chain: List[Dict[str, Any]] = []
        self._lock = RLock()

    @property
    def chain(self) -> Tuple[Dict[str, Any], ...]:
        with self._lock:
            return tuple(dict(record) for record in self._chain)

    def record_evidence(self, artifact_name: str, payload_hash: str) -> Dict[str, Any]:
        if not isinstance(artifact_name, str) or not artifact_name.strip():
            raise ValueError("artifact_name must be a non-empty string")
        if not _HEX_SHA256.fullmatch(payload_hash or ""):
            raise ValueError("payload_hash must be a 64-character SHA-256 hex digest")

        with self._lock:
            previous_hash = self._chain[-1]["current_hash"] if self._chain else "0" * 64
            record: Dict[str, Any] = {
                "index": len(self._chain) + 1,
                "artifact": artifact_name,
                "payload_hash": payload_hash.lower(),
                "previous_hash": previous_hash,
            }
            record["current_hash"] = self._hash_record(record)
            self._chain.append(record)
            return dict(record)

    def verify_chain(self) -> bool:
        with self._lock:
            previous_hash = "0" * 64
            for expected_index, record in enumerate(self._chain, start=1):
                if record.get("index") != expected_index:
                    return False
                if record.get("previous_hash") != previous_hash:
                    return False
                current_hash = record.get("current_hash")
                unsigned = {k: v for k, v in record.items() if k != "current_hash"}
                if current_hash != self._hash_record(unsigned):
                    return False
                previous_hash = current_hash
            return True

    @staticmethod
    def _hash_record(record: Dict[str, Any]) -> str:
        data = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    ledger = EvidenceLedger()
    record = ledger.record_evidence(
        "kernel_telemetry.log",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    print("Ledger Test Entry:", record)
    print("Chain valid:", ledger.verify_chain())
