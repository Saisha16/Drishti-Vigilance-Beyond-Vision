"""
Blockchain-Backed Tamper-Proof Audit Trail
Uses SHA-256 hash chain to create an immutable sequence of audit events.
Each block contains the hash of the previous block, making any tampering
mathematically detectable by re-computing the chain.

How it works:
1. Each audit event is serialized to canonical JSON
2. SHA-256 hash is computed: hash(event_data + previous_hash + timestamp + nonce)
3. The resulting hash is stored as the block's fingerprint
4. To verify integrity, re-compute all hashes from genesis — any mismatch = TAMPERED

This is NOT a full cryptocurrency blockchain. It's a lightweight, zero-dependency
cryptographic hash chain specifically designed for audit log integrity.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class AuditBlock:
    """A single block in the audit chain"""
    index: int
    timestamp: str
    action: str
    user_id: str
    details: Dict[str, Any]
    previous_hash: str
    nonce: int = 0
    block_hash: str = ""

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of block contents"""
        # Canonical serialization: sorted keys, no whitespace
        block_data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "action": self.action,
            "user_id": self.user_id,
            "details": self.details,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(block_data.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "action": self.action,
            "user_id": self.user_id,
            "details": self.details,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "block_hash": self.block_hash,
        }


class BlockchainAuditTrail:
    """
    Manages a tamper-proof audit log using a SHA-256 hash chain.
    
    Every audit event is chained to the previous one via cryptographic hashing.
    If any past block is modified, all subsequent hashes become invalid,
    making tampering instantly detectable.
    
    Integration with Database:
    - Blocks are persisted in the `blockchain_blocks` table
    - The chain can be verified at any time via verify_chain()
    - Each block references the previous block's hash
    """

    def __init__(self, db=None):
        """
        Initialize the blockchain audit trail.
        
        Args:
            db: Database instance for persistence. If None, operates in-memory only.
        """
        self.db = db
        self.chain: List[AuditBlock] = []
        self._load_chain()

    def _load_chain(self):
        """Load existing chain from database"""
        if self.db is None:
            # In-memory mode: create genesis block
            if not self.chain:
                self._create_genesis_block()
            return

        try:
            blocks = self.db.fetch_blockchain_blocks()
            if not blocks:
                self._create_genesis_block()
            else:
                self.chain = []
                for block_data in blocks:
                    block = AuditBlock(
                        index=block_data["index"],
                        timestamp=block_data["timestamp"],
                        action=block_data["action"],
                        user_id=block_data["user_id"],
                        details=block_data["details"],
                        previous_hash=block_data["previous_hash"],
                        nonce=block_data["nonce"],
                        block_hash=block_data["block_hash"],
                    )
                    self.chain.append(block)
        except Exception:
            # Table might not exist yet
            self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the first block in the chain (index 0)"""
        genesis = AuditBlock(
            index=0,
            timestamp=datetime.utcnow().isoformat() + "Z",
            action="genesis",
            user_id="system",
            details={"message": "Drishti Blockchain Audit Trail initialized"},
            previous_hash="0" * 64,
            nonce=0,
        )
        genesis.block_hash = genesis.compute_hash()
        self.chain = [genesis]

        if self.db is not None:
            try:
                self.db.save_blockchain_block(genesis)
            except Exception:
                pass  # Table may not be initialized yet

    def add_event(self, action: str, user_id: str, details: Dict[str, Any]) -> AuditBlock:
        """
        Add an audit event to the chain.
        
        Args:
            action: Type of action (e.g., "login_attempt", "data_access", "config_change")
            user_id: ID of the user who performed the action
            details: Additional details about the event
            
        Returns:
            The newly created AuditBlock
        """
        previous_block = self.chain[-1]

        new_block = AuditBlock(
            index=len(self.chain),
            timestamp=datetime.utcnow().isoformat() + "Z",
            action=action,
            user_id=user_id,
            details=details,
            previous_hash=previous_block.block_hash,
            nonce=0,
        )
        new_block.block_hash = new_block.compute_hash()
        self.chain.append(new_block)

        # Persist to database
        if self.db is not None:
            try:
                self.db.save_blockchain_block(new_block)
            except Exception:
                pass

        return new_block

    def verify_chain(self) -> Tuple[bool, List[Dict]]:
        """
        Verify the integrity of the entire audit chain.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
            - is_valid: True if the entire chain is intact
            - issues: List of dicts describing any integrity violations found
        """
        issues = []

        if not self.chain:
            return False, [{"block": -1, "issue": "Chain is empty"}]

        # Verify genesis block
        genesis = self.chain[0]
        if genesis.previous_hash != "0" * 64:
            issues.append({
                "block": 0,
                "issue": "Genesis block has invalid previous_hash",
                "expected": "0" * 64,
                "actual": genesis.previous_hash,
            })

        recomputed_hash = genesis.compute_hash()
        if recomputed_hash != genesis.block_hash:
            issues.append({
                "block": 0,
                "issue": "Genesis block hash mismatch — DATA TAMPERED",
                "expected": recomputed_hash,
                "actual": genesis.block_hash,
            })

        # Verify each subsequent block
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Check that current block's previous_hash matches actual previous block hash
            if current.previous_hash != previous.block_hash:
                issues.append({
                    "block": i,
                    "issue": f"Block {i} previous_hash doesn't match block {i-1} hash — CHAIN BROKEN",
                    "expected": previous.block_hash,
                    "actual": current.previous_hash,
                })

            # Recompute hash and compare
            recomputed = current.compute_hash()
            if recomputed != current.block_hash:
                issues.append({
                    "block": i,
                    "issue": f"Block {i} hash mismatch — DATA TAMPERED",
                    "expected": recomputed,
                    "actual": current.block_hash,
                })

        is_valid = len(issues) == 0
        return is_valid, issues

    def get_chain_summary(self) -> Dict:
        """Get a summary of the blockchain state"""
        is_valid, issues = self.verify_chain()

        # Count events by action type
        action_counts: Dict[str, int] = {}
        for block in self.chain:
            action_counts[block.action] = action_counts.get(block.action, 0) + 1

        return {
            "total_blocks": len(self.chain),
            "is_valid": is_valid,
            "integrity_issues": len(issues),
            "issues": issues[:10],  # Limit to first 10 issues
            "latest_block_hash": self.chain[-1].block_hash if self.chain else None,
            "genesis_hash": self.chain[0].block_hash if self.chain else None,
            "action_counts": action_counts,
            "last_event_time": self.chain[-1].timestamp if self.chain else None,
        }

    def get_recent_blocks(self, count: int = 50) -> List[Dict]:
        """Get the most recent N blocks"""
        recent = self.chain[-count:] if len(self.chain) >= count else self.chain
        return [block.to_dict() for block in reversed(recent)]

    def get_block_by_index(self, index: int) -> Optional[Dict]:
        """Get a specific block by index"""
        if 0 <= index < len(self.chain):
            return self.chain[index].to_dict()
        return None
