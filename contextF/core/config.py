import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from ..exceptions import ConfigurationError

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: Optional[str] = None, **overrides):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to JSON configuration file
            **overrides: Configuration overrides as keyword arguments
        """
        self.config = self._load_default_config()
        
        if config_path:
            self._load_config_file(config_path)
        
        if overrides:
            self._apply_overrides(overrides)
        
        self._validate_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        default_config_path = Path(__file__).parent.parent / "default_config.json"
        try:
            with open(default_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load default configuration: {e}")
    
    def _load_config_file(self, config_path: str):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            self._deep_update(self.config, user_config)
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {e}")
    
    def _apply_overrides(self, overrides: Dict[str, Any]):
        """Apply configuration overrides"""
        # Handle direct parameter overrides
        for key, value in overrides.items():
            if key in ['docs_path', 'file_patterns', 'max_patterns_per_query', 'max_matches_per_file', 'case_sensitive']:
                self.config['search'][key] = value
            elif key in ['context_window_tokens', 'max_context_tokens', 'max_file_tokens', 'encoding']:
                self.config['tokens'][key] = value
            elif key in ['chunk_size', 'chunk_overlap', 'merge_overlapping_windows']:
                self.config['text_processing'][key] = value
            elif key in ['enabled', 'model', 'temperature', 'pattern_generation_prompt']:
                self.config['llm'][key] = value
            else:
                # For nested overrides, use dot notation
                if '.' in key:
                    self._set_nested_value(self.config, key, value)
                else:
                    # Try to find the right section for unknown keys
                    found = False
                    for section in self.config.values():
                        if isinstance(section, dict) and key in section:
                            section[key] = value
                            found = True
                            break
                    if not found:
                        # Create new key in search section as default
                        self.config['search'][key] = value
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _set_nested_value(self, d: Dict, key: str, value: Any):
        """Set value in nested dictionary using dot notation"""
        keys = key.split('.')
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
    
    def _validate_config(self):
        """Validate configuration values"""
        try:
            # Validate token limits
            tokens = self.config['tokens']
            if tokens['context_window_tokens'] <= 0:
                raise ValueError("context_window_tokens must be positive")
            if tokens['max_context_tokens'] <= 0:
                raise ValueError("max_context_tokens must be positive")
            if tokens['max_file_tokens'] <= 0:
                raise ValueError("max_file_tokens must be positive")
            
            # Validate search parameters
            search = self.config['search']
            if search['max_patterns_per_query'] <= 0:
                raise ValueError("max_patterns_per_query must be positive")
            if search['max_matches_per_file'] <= 0:
                raise ValueError("max_matches_per_file must be positive")
            
            # Validate file patterns
            if not search['file_patterns']:
                raise ValueError("file_patterns cannot be empty")
            
            # Validate docs path
            if not search['docs_path']:
                raise ValueError("docs_path cannot be empty")
                
        except KeyError as e:
            raise ConfigurationError(f"Missing required configuration key: {e}")
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration value: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search configuration"""
        return self.config['search']
    
    def get_token_config(self) -> Dict[str, Any]:
        """Get token configuration"""
        return self.config['tokens']
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.config['llm']
    
    def get_text_processing_config(self) -> Dict[str, Any]:
        """Get text processing configuration"""
        return self.config['text_processing']
