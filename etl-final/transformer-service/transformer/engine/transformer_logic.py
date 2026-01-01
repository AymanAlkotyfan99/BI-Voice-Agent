"""
Enhanced Transformer Logic for ETL Pipeline
Business transformations with validation and error handling
"""
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TransformerLogic:
    """
    Enhanced business transformation logic with validation.
    
    Features:
    - Type-safe transformations
    - Business rule application
    - Data normalization
    - Error handling
    - Transformation metadata
    """
    
    def __init__(self):
        """Initialize transformer with default rules."""
        self.transformation_count = 0
        self.error_count = 0
    
    def transform_row(self, row: Dict[str, Any], schema: Optional[Dict[str, str]] = None) -> Tuple[Dict[str, Any], List[str]]:
        """
        Apply business transformations to a row.
        
        Args:
            row: Input row dictionary
            schema: Optional schema dict for type hints
            
        Returns:
            Tuple of (transformed_row, list_of_warnings)
        """
        warnings = []
        transformed = {}
        
        if not row:
            return {}, ["Empty row received"]
        
        try:
            for field, value in row.items():
                try:
                    # Apply transformations based on field name patterns or schema
                    transformed_value = self._apply_field_transformations(field, value, schema)
                    transformed[field] = transformed_value
                except Exception as e:
                    logger.warning(f"[Transformer] Error transforming field {field}: {e}")
                    warnings.append(f"Field {field}: {str(e)}")
                    transformed[field] = value  # Keep original value on error
            
            self.transformation_count += 1
            return transformed, warnings
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"Transformation error: {str(e)}"
            logger.error(error_msg)
            return row, [error_msg]  # Return original row on error
    
    def _apply_field_transformations(self, field: str, value: Any, schema: Optional[Dict[str, str]] = None) -> Any:
        """
        Apply specific transformations to a field value.
        
        Args:
            field: Field name
            value: Field value
            schema: Optional schema for type hints
            
        Returns:
            Transformed value
        """
        if value is None:
            return None
        
        # Use schema type if available
        if schema and field in schema:
            target_type = schema[field].lower()
            return self._coerce_to_type(value, target_type)
        
        # Apply general transformations
        return self._apply_general_transformations(value)
    
    def _coerce_to_type(self, value: Any, target_type: str) -> Any:
        """Coerce value to target type."""
        if target_type in ['int', 'integer', 'bigint']:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str) and value.strip():
                try:
                    return int(float(value.strip()))
                except ValueError:
                    return value
            return None
        
        elif target_type in ['float', 'double', 'decimal', 'numeric']:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str) and value.strip():
                try:
                    return float(value.strip())
                except ValueError:
                    return value
            return None
        
        elif target_type in ['bool', 'boolean']:
            return self._coerce_boolean(value)
        
        elif target_type in ['string', 'text', 'varchar']:
            return str(value) if value is not None else None
        
        return value
    
    def _apply_general_transformations(self, value: Any) -> Any:
        """Apply general transformations to value."""
        # Already handled by cleaning rules, but can add business-specific logic here
        return value
    
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
        return bool(value) if value is not None else False
