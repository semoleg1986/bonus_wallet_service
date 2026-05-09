"""Domain-level errors for bonus_wallet_service."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain-layer errors."""


class ValidationError(DomainError):
    """Raised when input violates domain validation rules."""


class NotFoundError(DomainError):
    """Raised when an aggregate or entity cannot be found."""


class AccessDeniedError(DomainError):
    """Raised when an actor is not allowed to perform an operation."""


class InvariantViolationError(DomainError):
    """Raised when a domain invariant would be violated."""
