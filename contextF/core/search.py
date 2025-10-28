import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from ..exceptions import SearchError, FileProcessingError

class SearchEngine:
    """Handles file searching and pattern matching"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize search engine
        
        Args:
            config: Search configuration dictionary
        """
        self.config = config
        self.case_sensitive = config.get('case_sensitive', False)
        self.max_matches_per_file = config.get('max_matches_per_file', 3)
    
    def search_files(self, patterns: List[str], docs_path: str, 
                    file_patterns: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for patterns across multiple files
        
        Args:
            patterns: List of search patterns/keywords
            docs_path: Path to documents directory
            file_patterns: List of file patterns to match (e.g., ['*.md', '*.txt'])
        
        Returns:
            Dictionary mapping filenames to list of matches
        """
        if not patterns:
            raise SearchError("No search patterns provided")
        
        path_obj = Path(docs_path)
        if not path_obj.exists():
            raise SearchError(f"Documents path does not exist: {docs_path}")
        
        all_file_matches = {}
        
        try:
            # Get all matching files
            files_to_search = []
            for pattern in file_patterns:
                files_to_search.extend(path_obj.rglob(pattern))
            
            if not files_to_search:
                raise SearchError(f"No files found matching patterns {file_patterns} in {docs_path}")
            
            # Search each file for all patterns
            for file_path in files_to_search:
                if file_path.is_file():
                    file_matches = self._search_file(patterns, str(file_path))
                    if file_matches:
                        all_file_matches[str(file_path)] = file_matches
            
            return all_file_matches
            
        except Exception as e:
            if isinstance(e, SearchError):
                raise
            raise SearchError(f"Error during file search: {e}")
    
    def _search_file(self, patterns: List[str], filename: str) -> List[Dict[str, Any]]:
        """
        Search for patterns within a specific file
        
        Args:
            patterns: List of search patterns
            filename: Path to file to search
        
        Returns:
            List of match dictionaries with line_num, text, and pattern
        """
        matches = []
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in patterns:
                        if self._pattern_matches(pattern, line):
                            matches.append({
                                'line_num': line_num,
                                'text': line.rstrip(),
                                'pattern': pattern
                            })
                            
                            # Limit matches per file
                            if len(matches) >= self.max_matches_per_file:
                                return matches
            
            return matches
            
        except Exception as e:
            raise FileProcessingError(f"Error reading file {filename}: {e}")
    
    def _pattern_matches(self, pattern: str, text: str) -> bool:
        """
        Check if pattern matches text
        
        Args:
            pattern: Search pattern
            text: Text to search in
        
        Returns:
            True if pattern matches, False otherwise
        """
        try:
            flags = 0 if self.case_sensitive else re.IGNORECASE
            return bool(re.search(re.escape(pattern), text, flags))
        except re.error:
            # If regex fails, fall back to simple string matching
            if self.case_sensitive:
                return pattern in text
            else:
                return pattern.lower() in text.lower()
    
    def filter_unique_matches(self, matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out duplicate matches based on text content
        
        Args:
            matches: List of match dictionaries
        
        Returns:
            List of unique matches, limited by max_matches_per_file
        """
        seen_texts = set()
        unique_matches = []
        
        for match in matches:
            text_key = match['text'].strip().lower()
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_matches.append(match)
                
                if len(unique_matches) >= self.max_matches_per_file:
                    break
        
        return unique_matches
