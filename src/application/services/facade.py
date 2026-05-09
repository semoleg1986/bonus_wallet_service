"""Application facade for bonus wallet use-cases."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.application.dto import (
    AccrualView,
    AccrueBonusCommand,
    BalanceView,
    BonusRuleView,
    CommitRedeemCommand,
    CreateBonusRuleCommand,
    DeactivateBonusRuleCommand,
    GetBalanceQuery,
    ListBonusRulesQuery,
    RedeemQuoteQuery,
    RedeemQuoteView,
    RedemptionView,
    RevertRedeemCommand,
)
from src.application.ports.unit_of_work import UnitOfWorkFactory
from src.domain.errors import InvariantViolationError, NotFoundError, ValidationError
from src.domain.wallet.entity import BonusAccount, BonusLedgerEntry, LedgerOperation
from src.domain.wallet.rule import BonusRule


@dataclass(slots=True)
class BonusWalletFacade:
    """Entry point for bonus wallet application use-cases."""

    uow_factory: UnitOfWorkFactory

    def get_balance(self, query: GetBalanceQuery) -> BalanceView:
        """Return current balance, creating zero-balance view if absent."""

        if not query.parent_id.strip():
            raise ValidationError("parent_id обязателен.")
        with self.uow_factory() as uow:
            account = uow.accounts.get(query.parent_id)
        if account is None:
            return BalanceView(parent_id=query.parent_id, balance=0)
        return BalanceView(parent_id=account.parent_id, balance=account.balance)

    def accrue(self, command: AccrueBonusCommand) -> AccrualView:
        """Credit bonus balance in a replay-safe way."""

        with self.uow_factory() as uow:
            if command.idempotency_key:
                existing = uow.ledger.get_by_idempotency(
                    parent_id=command.parent_id,
                    operation=LedgerOperation.ACCRUAL,
                    idempotency_key=command.idempotency_key,
                )
                if existing is not None:
                    return self._to_accrual_view(existing)

            account = self._get_or_create_account(uow.accounts, command.parent_id)
            balance_after = account.accrue(command.amount)
            entry = BonusLedgerEntry.create(
                entry_id=self._new_id(),
                parent_id=command.parent_id,
                operation=LedgerOperation.ACCRUAL,
                delta=command.amount,
                balance_after=balance_after,
                reason_code=command.reason_code,
                reference_id=command.reference_id,
                idempotency_key=command.idempotency_key,
            )
            uow.accounts.save(account)
            uow.ledger.append(entry)
            uow.commit()
        return self._to_accrual_view(entry)

    def quote_redeem(self, query: RedeemQuoteQuery) -> RedeemQuoteView:
        """Calculate allowed redeem amount without mutation."""

        if query.requested_amount <= 0:
            raise ValidationError("requested_amount должен быть > 0.")
        with self.uow_factory() as uow:
            account = uow.accounts.get(query.parent_id)
        available = account.balance if account is not None else 0
        allowed = min(query.requested_amount, available)
        return RedeemQuoteView(
            parent_id=query.parent_id,
            requested_amount=query.requested_amount,
            available_balance=available,
            allowed_amount=allowed,
            payment_intent_id=query.payment_intent_id,
        )

    def create_rule(self, command: CreateBonusRuleCommand) -> BonusRuleView:
        """Create a new configurable bonus accrual rule."""

        rule = BonusRule.create(
            rule_id=self._new_id(),
            trigger_type=command.trigger_type,
            threshold=command.threshold,
            points=command.points,
        )
        with self.uow_factory() as uow:
            uow.rules.save(rule)
            uow.commit()
        return self._to_rule_view(rule)

    def deactivate_rule(self, command: DeactivateBonusRuleCommand) -> BonusRuleView:
        """Deactivate an existing rule."""

        with self.uow_factory() as uow:
            rule = uow.rules.get(command.rule_id)
            if rule is None:
                raise NotFoundError("BonusRule не найден.")
            rule.deactivate()
            uow.rules.save(rule)
            uow.commit()
        return self._to_rule_view(rule)

    def list_rules(self, query: ListBonusRulesQuery) -> list[BonusRuleView]:
        """Return configured rules."""

        with self.uow_factory() as uow:
            rules = uow.rules.list(active_only=query.active_only)
        return [self._to_rule_view(rule) for rule in rules]

    def commit_redeem(self, command: CommitRedeemCommand) -> RedemptionView:
        """Consume balance for a payment in a replay-safe way."""

        with self.uow_factory() as uow:
            if command.idempotency_key:
                existing = uow.ledger.get_by_idempotency(
                    parent_id=command.parent_id,
                    operation=LedgerOperation.REDEEM_COMMIT,
                    idempotency_key=command.idempotency_key,
                )
                if existing is not None:
                    return self._to_redemption_view(existing)

            existing_by_payment = uow.ledger.get_by_reference(
                parent_id=command.parent_id,
                operation=LedgerOperation.REDEEM_COMMIT,
                reference_id=command.payment_intent_id,
            )
            if existing_by_payment is not None:
                if abs(existing_by_payment.delta) != command.amount:
                    raise InvariantViolationError(
                        "Для payment_intent уже есть redemption с другим amount."
                    )
                return self._to_redemption_view(existing_by_payment)

            account = self._get_or_create_account(uow.accounts, command.parent_id)
            balance_after = account.redeem(command.amount)
            entry = BonusLedgerEntry.create(
                entry_id=self._new_id(),
                parent_id=command.parent_id,
                operation=LedgerOperation.REDEEM_COMMIT,
                delta=-command.amount,
                balance_after=balance_after,
                reason_code="payment_redeem_commit",
                reference_id=command.payment_intent_id,
                idempotency_key=command.idempotency_key,
            )
            uow.accounts.save(account)
            uow.ledger.append(entry)
            uow.commit()
        return self._to_redemption_view(entry)

    def revert_redeem(self, command: RevertRedeemCommand) -> RedemptionView:
        """Restore balance for a previously committed payment redemption."""

        with self.uow_factory() as uow:
            if command.idempotency_key:
                existing = uow.ledger.get_by_idempotency(
                    parent_id=command.parent_id,
                    operation=LedgerOperation.REDEEM_REVERT,
                    idempotency_key=command.idempotency_key,
                )
                if existing is not None:
                    return self._to_redemption_view(existing)

            existing_revert = uow.ledger.get_by_reference(
                parent_id=command.parent_id,
                operation=LedgerOperation.REDEEM_REVERT,
                reference_id=command.payment_intent_id,
            )
            if existing_revert is not None:
                if abs(existing_revert.delta) != command.amount:
                    raise InvariantViolationError(
                        "Для payment_intent уже есть revert с другим amount."
                    )
                return self._to_redemption_view(existing_revert)

            commit_entry = uow.ledger.get_by_reference(
                parent_id=command.parent_id,
                operation=LedgerOperation.REDEEM_COMMIT,
                reference_id=command.payment_intent_id,
            )
            if commit_entry is None:
                raise NotFoundError("Redeem commit для payment_intent не найден.")
            if abs(commit_entry.delta) != command.amount:
                raise InvariantViolationError(
                    "revert amount должен совпадать с исходным commit amount."
                )

            account = self._get_or_create_account(uow.accounts, command.parent_id)
            balance_after = account.accrue(command.amount)
            entry = BonusLedgerEntry.create(
                entry_id=self._new_id(),
                parent_id=command.parent_id,
                operation=LedgerOperation.REDEEM_REVERT,
                delta=command.amount,
                balance_after=balance_after,
                reason_code="payment_redeem_revert",
                reference_id=command.payment_intent_id,
                idempotency_key=command.idempotency_key,
            )
            uow.accounts.save(account)
            uow.ledger.append(entry)
            uow.commit()
        return self._to_redemption_view(entry)

    @staticmethod
    def _get_or_create_account(accounts, parent_id: str) -> BonusAccount:
        account = accounts.get(parent_id)
        if account is None:
            account = BonusAccount.create(parent_id=parent_id)
        return account

    @staticmethod
    def _to_accrual_view(entry: BonusLedgerEntry) -> AccrualView:
        return AccrualView(
            entry_id=entry.entry_id,
            parent_id=entry.parent_id,
            amount=entry.delta,
            balance_after=entry.balance_after,
            reason_code=entry.reason_code,
            reference_id=entry.reference_id,
            idempotency_key=entry.idempotency_key,
            operation=entry.operation.value,
        )

    @staticmethod
    def _to_redemption_view(entry: BonusLedgerEntry) -> RedemptionView:
        return RedemptionView(
            entry_id=entry.entry_id,
            parent_id=entry.parent_id,
            amount=abs(entry.delta),
            balance_after=entry.balance_after,
            payment_intent_id=entry.reference_id or "",
            idempotency_key=entry.idempotency_key,
            operation=entry.operation.value,
        )

    @staticmethod
    def _to_rule_view(rule: BonusRule) -> BonusRuleView:
        return BonusRuleView(
            rule_id=rule.rule_id,
            trigger_type=rule.trigger_type.value,
            threshold=rule.threshold,
            points=rule.points,
            is_active=rule.is_active,
        )

    @staticmethod
    def _new_id() -> str:
        return str(uuid.uuid4())
