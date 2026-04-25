"""Collaboration middleware for Workbench ticket enforcement."""

from .restricted_auth import RestrictedAuthError, validate_push_attempt

__all__ = ["RestrictedAuthError", "validate_push_attempt"]
