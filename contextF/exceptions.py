class ContextFError(Exception):
    """Base exception for contextF library"""
    pass

class ConfigurationError(ContextFError):
    """Raised when there's an error in configuration"""
    pass

class SearchError(ContextFError):
    """Raised when there's an error during search operations"""
    pass

class FileProcessingError(ContextFError):
    """Raised when there's an error processing files"""
    pass

class TokenLimitError(ContextFError):
    """Raised when token limits are exceeded"""
    pass
