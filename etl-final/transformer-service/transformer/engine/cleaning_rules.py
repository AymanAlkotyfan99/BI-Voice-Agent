"""
Enhanced Cleaning Rules for ETL Pipeline
Comprehensive data cleaning with validation and edge-case handling
"""
from typing import Dict, Any, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class CleaningRules:
    """
    Comprehensive data cleaning rules with validation and error handling.
    
    Features:
    - Null/empty value handling
    - String normalization
    - Type coercion
    - Invalid data detection
    - Edge case handling
    - Validation metadata
    """
    
    def __init__(self):
        """Initialize cleaning rules with default configurations."""
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def remove_null_fields(self, row: Dict[str, Any], keep_empty_strings: bool = False) -> Dict[str, Any]:
        """
        Remove fields with NULL/None values.
        
        Args:
            row: Input row dictionary
            keep_empty_strings: Whether to keep empty strings (default: False)
            
        Returns:
            Cleaned row dictionary
        """
        cleaned = {}
        for k, v in row.items():
            if v is None:
                continue  # Skip None values
            if not keep_empty_strings and v == "":
                continue  # Skip empty strings
            cleaned[k] = v
        return cleaned
    
    def trim_strings(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trim whitespace from string fields, including newlines and tabs.
        
        Args:
            row: Input row dictionary
            
        Returns:
            Row with trimmed strings
        """
        cleaned = {}
        for k, v in row.items():
            if isinstance(v, str):
                # Remove leading/trailing whitespace, newlines, tabs
                cleaned[k] = v.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            else:
                cleaned[k] = v
        return cleaned
    
    def normalize_whitespace(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize multiple spaces to single space in string fields.
        
        Args:
            row: Input row dictionary
            
        Returns:
            Row with normalized whitespace
        """
        cleaned = {}
        for k, v in row.items():
            if isinstance(v, str):
                # Replace multiple spaces with single space
                cleaned[k] = re.sub(r'\s+', ' ', v).strip()
            else:
                cleaned[k] = v
        return cleaned
    
    def handle_empty_strings(self, row: Dict[str, Any], convert_to_none: bool = True) -> Dict[str, Any]:
        """
        Handle empty strings (convert to None or keep).
        
        Args:
            row: Input row dictionary
            convert_to_none: Convert empty strings to None (default: True)
            
        Returns:
            Row with handled empty strings
        """
        cleaned = {}
        for k, v in row.items():
            if isinstance(v, str) and v.strip() == "":
                cleaned[k] = None if convert_to_none else ""
            else:
                cleaned[k] = v
        return cleaned
    
    def coerce_types(self, row: Dict[str, Any], schema: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Coerce values to appropriate types based on schema or inference.
        
        Args:
            row: Input row dictionary
            schema: Optional schema dict with column:type mappings
            
        Returns:
            Row with coerced types
        """
        cleaned = {}
        for k, v in row.items():
            if v is None:
                cleaned[k] = None
                continue
            
            # Use schema if provided
            if schema and k in schema:
                target_type = schema[k].lower()
                try:
                    if target_type in ['int', 'integer', 'bigint']:
                        cleaned[k] = int(float(str(v))) if str(v).strip() else None
                    elif target_type in ['float', 'double', 'decimal', 'numeric']:
                        cleaned[k] = float(str(v)) if str(v).strip() else None
                    elif target_type in ['bool', 'boolean']:
                        cleaned[k] = self._coerce_boolean(v)
                    else:
                        cleaned[k] = str(v)
                except (ValueError, TypeError) as e:
                    logger.warning(f"[Cleaning] Type coercion failed for {k}: {e}")
                    cleaned[k] = v  # Keep original value
            else:
                # Infer type
                cleaned[k] = self._infer_type(v)
        
        return cleaned
    
    def _coerce_boolean(self, value: Any) -> bool:
        """Coerce value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.lower().strip()
            if normalized in ['true', 'yes', '1', 'y', 'on']:
                return True
            if normalized in ['false', 'no', '0', 'n', 'off', '']:
                return False
        return bool(value)
    
    def _infer_type(self, value: Any) -> Any:
        """Infer and convert type for a value."""
        if isinstance(value, (int, float, bool)):
            return value
        
        if not isinstance(value, str):
            return value
        
        value_str = value.strip()
        
        # Try integer
        if value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
            try:
                return int(value_str)
            except ValueError:
                pass
        
        # Try float
        try:
            return float(value_str)
        except ValueError:
            pass
        
        # Try boolean
        normalized = value_str.lower()
        if normalized in ['true', 'yes', '1']:
            return True
        if normalized in ['false', 'no', '0', '']:
            return False
        
        # Return as string
        return value_str
    
    def validate_row(self, row: Dict[str, Any], required_fields: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
        """
        Validate row structure and content.
        
        Args:
            row: Row dictionary to validate
            required_fields: Optional list of required field names
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check required fields
        if required_fields:
            for field in required_fields:
                if field not in row or row[field] is None:
                    warnings.append(f"Missing required field: {field}")
        
        # Check for completely empty row
        if not row or all(v is None or v == "" for v in row.values()):
            warnings.append("Row is completely empty")
        
        return len(warnings) == 0, warnings
    
    def apply_all(self, row: Dict[str, Any], schema: Optional[Dict[str, str]] = None, 
                  required_fields: Optional[List[str]] = None) -> Tuple[Dict[str, Any], List[str]]:
        """
        Apply all cleaning rules in sequence.
        
        Args:
            row: Input row dictionary
            schema: Optional schema for type coercion
            required_fields: Optional list of required fields
            
        Returns:
            Tuple of (cleaned_row, list_of_warnings)
        """
        self.warnings = []
        self.errors = []
        
        if not row:
            self.errors.append("Empty row received")
            return {}, self.errors
        
        try:
            # Step 1: Handle nulls and empty strings
            cleaned = self.remove_null_fields(row, keep_empty_strings=False)
            
            # Step 2: Trim strings
            cleaned = self.trim_strings(cleaned)
            
            # Step 3: Normalize whitespace
            cleaned = self.normalize_whitespace(cleaned)
            
            # Step 4: Handle empty strings
            cleaned = self.handle_empty_strings(cleaned, convert_to_none=True)
            
            # Step 5: Coerce types
            cleaned = self.coerce_types(cleaned, schema)
            
            # Step 6: Validate
            is_valid, validation_warnings = self.validate_row(cleaned, required_fields)
            self.warnings.extend(validation_warnings)
            
            if not is_valid:
                self.warnings.append("Row validation failed")
            
            return cleaned, self.warnings
            
        except Exception as e:
            error_msg = f"Cleaning error: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return row, self.errors  # Return original row on error
