"""In-memory repositories for wallet state."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from src.application.dto import BonusReasonBreakdownItemView
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

    def count_positive_balances(self) -> int:
        return sum(1 for account in self._storage.values() if account.balance > 0)

    def total_balance_outstanding(self) -> int:
        return sum(
            account.balance for account in self._storage.values() if account.balance > 0
        )


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

    def list_filtered(
        self,
        *,
        parent_id: str | None = None,
        reason_code: str | None = None,
        operation: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BonusLedgerEntry]:
        entries = list(self._entries)
        if parent_id is not None:
            entries = [entry for entry in entries if entry.parent_id == parent_id]
        if reason_code is not None:
            entries = [entry for entry in entries if entry.reason_code == reason_code]
        if operation is not None:
            entries = [entry for entry in entries if entry.operation.value == operation]
        if date_from is not None:
            entries = [entry for entry in entries if entry.created_at >= date_from]
        if date_to is not None:
            entries = [entry for entry in entries if entry.created_at <= date_to]
        entries = sorted(entries, key=lambda item: item.created_at, reverse=True)
        return entries[offset : offset + limit]

    def summarize(
        self,
        *,
        parent_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, int | datetime | None]:
        entries = self.list_filtered(
            parent_id=parent_id,
            date_from=date_from,
            date_to=date_to,
            limit=max(len(self._entries), 1_000_000),
            offset=0,
        )
        return {
            "entries_count": len(entries),
            "accruals_total": sum(
                entry.delta
                for entry in entries
                if entry.operation == LedgerOperation.ACCRUAL
            ),
            "redeemed_total": sum(
                abs(entry.delta)
                for entry in entries
                if entry.operation == LedgerOperation.REDEEM_COMMIT
            ),
            "reverted_total": sum(
                entry.delta
                for entry in entries
                if entry.operation == LedgerOperation.REDEEM_REVERT
            ),
            "last_activity_at": entries[0].created_at if entries else None,
        }

    def summarize_by_reason(
        self,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BonusReasonBreakdownItemView]:
        entries = self.list_filtered(
            date_from=date_from,
            date_to=date_to,
            limit=max(len(self._entries), 1_000_000),
            offset=0,
        )
        grouped: dict[str, dict[str, int]] = {}
        for entry in entries:
            bucket = grouped.setdefault(
                entry.reason_code,
                {
                    "entries_count": 0,
                    "total_delta": 0,
                    "total_accrued": 0,
                    "total_redeemed": 0,
                    "total_reverted": 0,
                },
            )
            bucket["entries_count"] += 1
            bucket["total_delta"] += entry.delta
            if entry.operation == LedgerOperation.ACCRUAL:
                bucket["total_accrued"] += entry.delta
            elif entry.operation == LedgerOperation.REDEEM_COMMIT:
                bucket["total_redeemed"] += abs(entry.delta)
            elif entry.operation == LedgerOperation.REDEEM_REVERT:
                bucket["total_reverted"] += entry.delta

        items = [
            BonusReasonBreakdownItemView(
                reason_code=reason_code,
                entries_count=payload["entries_count"],
                total_delta=payload["total_delta"],
                total_accrued=payload["total_accrued"],
                total_redeemed=payload["total_redeemed"],
                total_reverted=payload["total_reverted"],
            )
            for reason_code, payload in sorted(
                grouped.items(), key=lambda item: (-item[1]["entries_count"], item[0])
            )
        ]
        return items[offset : offset + limit]


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
