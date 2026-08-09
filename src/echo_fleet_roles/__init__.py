"""ECHO fleet role selection and context runtime."""

from .registry import Registry, Role, load_registry
from .runtime import RoleRuntime

__all__ = ["Registry", "Role", "RoleRuntime", "load_registry"]
__version__ = "1.0.0"
