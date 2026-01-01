"""
Unified Metadata Schema for ETL Pipeline
Defines consistent metadata structures across all pipeline stages
"""
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple


class MetadataSchema:
    """
    Unified metadata model for ETL pipeline tracking.
    Ensures consistent metadata structure across all stages.
    """
    
    @staticmethod
    def create_connection_metadata(
        source_type: str,
        source_id: str,
        connection_info: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create metadata for connection stage.
        
        Args:
            source_type: "file" or "database"
            source_id: Unique identifier for the source
            connection_info: Connection details (path, db config, etc.)
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Standardized connection metadata dict
        """
        return {
            "metadata_type": "connection",
            "source_type": source_type,
            "source_id": source_id,
            "connection_info": connection_info,
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
            "pipeline_stage": "connection",
            "status": "success"
        }
    
    @staticmethod
    def create_schema_metadata(
        source_id: str,
        schema: Dict[str, Any],
        row_count: int,
        validation_results: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create metadata for schema extraction stage.
        
        Args:
            source_id: Unique identifier for the source
            schema: Schema information (columns, types, etc.)
            row_count: Number of rows extracted
            validation_results: Optional schema validation results
            timestamp: Optional timestamp
            
        Returns:
            Standardized schema metadata dict
        """
        return {
            "metadata_type": "schema",
            "source_id": source_id,
            "schema": schema,
            "row_count": row_count,
            "validation_results": validation_results or {},
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
            "pipeline_stage": "extract",
            "status": "success"
        }
    
    @staticmethod
    def create_extraction_metadata(
        source_id: str,
        rows_processed: int,
        rows_successful: int,
        rows_failed: int,
        errors: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create metadata for row extraction stage.
        
        Args:
            source_id: Unique identifier for the source
            rows_processed: Total rows processed
            rows_successful: Successfully extracted rows
            rows_failed: Failed extractions
            errors: List of error messages
            timestamp: Optional timestamp
            
        Returns:
            Standardized extraction metadata dict
        """
        return {
            "metadata_type": "extraction",
            "source_id": source_id,
            "rows_processed": rows_processed,
            "rows_successful": rows_successful,
            "rows_failed": rows_failed,
            "errors": errors or [],
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
            "pipeline_stage": "extract",
            "status": "success" if rows_failed == 0 else "partial"
        }
    
    @staticmethod
    def create_cleaning_metadata(
        source_id: str,
        rows_processed: int,
        rows_cleaned: int,
        rows_failed: int,
        cleaning_rules_applied: List[str],
        validation_warnings: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create metadata for cleaning/transformation stage.
        
        Args:
            source_id: Unique identifier for the source
            rows_processed: Total rows processed
            rows_cleaned: Successfully cleaned rows
            rows_failed: Failed cleanings
            cleaning_rules_applied: List of cleaning rules used
            validation_warnings: Optional validation warnings
            timestamp: Optional timestamp
            
        Returns:
            Standardized cleaning metadata dict
        """
        return {
            "metadata_type": "cleaning",
            "source_id": source_id,
            "rows_processed": rows_processed,
            "rows_cleaned": rows_cleaned,
            "rows_failed": rows_failed,
            "cleaning_rules_applied": cleaning_rules_applied,
            "validation_warnings": validation_warnings or [],
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
            "pipeline_stage": "transform",
            "status": "success" if rows_failed == 0 else "partial"
        }
    
    @staticmethod
    def create_loading_metadata(
        source_id: str,
        table_name: str,
        rows_loaded: int,
        rows_failed: int,
        load_duration_ms: Optional[int] = None,
        errors: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Create metadata for loading stage.
        
        Args:
            source_id: Unique identifier for the source
            table_name: Target table name in ClickHouse
            rows_loaded: Successfully loaded rows
            rows_failed: Failed loads
            load_duration_ms: Optional load duration in milliseconds
            errors: List of error messages
            timestamp: Optional timestamp
            
        Returns:
            Standardized loading metadata dict
        """
        return {
            "metadata_type": "loading",
            "source_id": source_id,
            "table_name": table_name,
            "rows_loaded": rows_loaded,
            "rows_failed": rows_failed,
            "load_duration_ms": load_duration_ms,
            "errors": errors or [],
            "timestamp": timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
            "pipeline_stage": "load",
            "status": "success" if rows_failed == 0 else "partial"
        }
    
    @staticmethod
    def validate_metadata(metadata: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate metadata structure.
        
        Args:
            metadata: Metadata dict to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["metadata_type", "source_id", "timestamp", "pipeline_stage", "status"]
        
        for field in required_fields:
            if field not in metadata:
                return False, f"Missing required field: {field}"
        
        valid_types = ["connection", "schema", "extraction", "cleaning", "loading"]
        if metadata["metadata_type"] not in valid_types:
            return False, f"Invalid metadata_type: {metadata['metadata_type']}"
        
        valid_stages = ["connection", "extract", "transform", "load"]
        if metadata["pipeline_stage"] not in valid_stages:
            return False, f"Invalid pipeline_stage: {metadata['pipeline_stage']}"
        
        return True, None

