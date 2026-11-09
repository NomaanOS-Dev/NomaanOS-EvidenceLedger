import os
import hashlib
import pytest
from ledger import EvidenceLedger
from ledger_persistent import PersistentEvidenceLedger, LedgerIntegrityError


def dummy_hash(val: str) -> str:
    return hashlib.sha256(val.encode("utf-8")).hexdigest()


def test_in_memory_chain():
    ledger = EvidenceLedger()
    r1 = ledger.record_evidence("boot.log", dummy_hash("kernel_init"))
    r2 = ledger.record_evidence("sys.log", dummy_hash("network_up"))
    
    assert r1["index"] == 1
    assert r2["index"] == 2
    assert r2["previous_hash"] == r1["current_hash"]
    assert ledger.verify_chain() is True


def test_invalid_hash_format():
    ledger = EvidenceLedger()
    with pytest.raises(ValueError, match="64-character SHA-256"):
        ledger.record_evidence("bad.log", "invalid_hash_string")


def test_persistent_ledger_startup_and_tamper(tmp_path):
    db_file = str(tmp_path / "audit.jsonl")
    
    # 1. Initialize and write
    ledger = PersistentEvidenceLedger(db_file)
    h1 = dummy_hash("data_1")
    ledger.record_evidence("audit_01", h1)
    h2 = dummy_hash("data_2")
    ledger.record_evidence("audit_02", h2)
    assert ledger.verify_chain() is True
    
    # 2. Reload valid
    reloaded = PersistentEvidenceLedger(db_file)
    assert reloaded.verify_chain() is True
    assert len(reloaded.chain) == 2
    
    # 3. Corrupt file on disk (actual hash replace karke tamper)
    with open(db_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert h1 in lines[0]
    lines[0] = lines[0].replace(h1[:8], "deadbeef")
    with open(db_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    # 4. Fail-closed assertion on load
    with pytest.raises(LedgerIntegrityError):
        PersistentEvidenceLedger(db_file)
