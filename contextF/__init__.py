"""
contextF - Efficient Context Builder

A library for building relevant context from documents using configurable search patterns
and token-aware context windowing.
"""

from .contextf import ContextBuilder
from .exceptions import ContextFError, ConfigurationError, SearchError, FileProcessingError

__version__ = "1.0.0"
__author__ = "contextF Team"
__description__ = "Efficient context builder for document analysis"

__all__ = [
    "ContextBuilder",
    "ContextFError", 
    "ConfigurationError",
    "SearchError",
    "FileProcessingError"
]
