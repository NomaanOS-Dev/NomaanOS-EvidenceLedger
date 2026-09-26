# NomaanOS-EvidenceLedger

A small append-only, hash-linked evidence ledger for integrity metadata.

## Current guarantees

- Validates SHA-256 payload digests.
- Links records with a previous hash.
- Provides `verify_chain()` for detecting in-memory tampering.
- Returns copies/snapshots rather than exposing the mutable internal list.
- Thread-safe operations (RLock).

## Important limitations

The current implementation is in-memory only. It does not provide:
- Durable storage
- Authenticated checkpoints
- Key management
- Trusted timestamps
- Legal admissibility

The structure is a cryptographic **hash chain**, not a Merkle tree. Production deployments should add atomic persistence, access control, signed checkpoints, and an independently reviewed custody procedure.

## Run

```bash
python ledger.py
