"""In-memory repositories for wallet state."""

from __future__ import annotations

from dataclasses import replace

from src.domain.wallet.entity import BonusAccount, BonusLedgerEntry, LedgerOperation
from src.domain.wallet.rule import BonusRule


class InMemoryBonusAccountRepository:
    """Simple dict-backed account repository."""

    def __init__(self, storage: dict[str, BonusAccount]) -> None:
        self._storage = storage

    def get(self, parent_id: str) -> BonusAccount | None:
        account = self._storage.get(parent_id)
        return replace(account) if account is not None else None

    def save(self, account: BonusAccount) -> None:
        self._storage[account.parent_id] = replace(account)


class InMemoryBonusLedgerRepository:
    """Simple dict-backed ledger repository with idempotency indexes."""

    def __init__(
        self,
        entries: list[BonusLedgerEntry],
        by_idempotency: dict[tuple[str, LedgerOperation, str], BonusLedgerEntry],
        by_reference: dict[tuple[str, LedgerOperation, str], BonusLedgerEntry],
    ) -> None:
        self._entries = entries
        self._by_idempotency = by_idempotency
        self._by_reference = by_reference

    def append(self, entry: BonusLedgerEntry) -> None:
        self._entries.append(entry)
        if entry.idempotency_key:
            self._by_idempotency[
                (entry.parent_id, entry.operation, entry.idempotency_key)
            ] = entry
        if entry.reference_id:
            key = (entry.parent_id, entry.operation, entry.reference_id)
            self._by_reference[key] = entry

    def get_by_idempotency(
        self,
        *,
        parent_id: str,
        operation: LedgerOperation,
        idempotency_key: str,
    ) -> BonusLedgerEntry | None:
        return self._by_idempotency.get((parent_id, operation, idempotency_key))

    def get_by_reference(
        self,
        *,
        parent_id: str,
        operation: LedgerOperation,
        reference_id: str,
    ) -> BonusLedgerEntry | None:
        return self._by_reference.get((parent_id, operation, reference_id))

    def list_by_parent(self, *, parent_id: str) -> list[BonusLedgerEntry]:
        entries = [entry for entry in self._entries if entry.parent_id == parent_id]
        return sorted(entries, key=lambda item: item.created_at, reverse=True)


class InMemoryBonusRuleRepository:
    """Simple dict-backed bonus rules repository."""

    def __init__(self, storage: dict[str, BonusRule]) -> None:
        self._storage = storage

    def get(self, rule_id: str) -> BonusRule | None:
        rule = self._storage.get(rule_id)
        return replace(rule) if rule is not None else None

    def save(self, rule: BonusRule) -> None:
        self._storage[rule.rule_id] = replace(rule)

    def list(self, *, active_only: bool) -> list[BonusRule]:
        rules = [replace(rule) for rule in self._storage.values()]
        if active_only:
            rules = [rule for rule in rules if rule.is_active]
        return sorted(rules, key=lambda item: item.rule_id)
