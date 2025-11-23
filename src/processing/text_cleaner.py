"""Text cleaning utilities for document preprocessing."""
import re


class TextCleaner:
    """Clean and normalize text content."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing noise and normalizing."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def anonymize_text(text: str, patterns: list = None) -> str:
        """Anonymize sensitive information in text."""
        if patterns is None:
            # Default patterns for common sensitive data
            patterns = [
                (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
                (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]'),  # Credit card
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
            ]
        
        anonymized = text
        for pattern, replacement in patterns:
            anonymized = re.sub(pattern, replacement, anonymized)
        
        return anonymized

