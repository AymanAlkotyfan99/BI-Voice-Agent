"""
Metabase Integration Service

Integrates with Metabase API for:
- Creating questions (visualizations)
- Creating dashboards
- Managing dashboard cards
- Getting embed URLs
"""

import requests
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MetabaseService:
    """
    Metabase API integration service.
    Handles question and dashboard creation programmatically.
    """
    
    def __init__(self):
        """Initialize Metabase service with environment configuration."""
        self.base_url = os.getenv('METABASE_URL', 'http://localhost:3000')
        self.secret_key = os.getenv('METABASE_SECRET_KEY')
        self.database_id = int(os.getenv('METABASE_DATABASE_ID', '1'))
        self.session_token = None
        
        if not self.secret_key:
            logger.warning("METABASE_SECRET_KEY not set - embedding will not work")
    
    def authenticate(self, username=None, password=None) -> bool:
        """
        Authenticate with Metabase and get session token.
        
        Args:
            username: Metabase admin username (from env if not provided)
            password: Metabase admin password (from env if not provided)
        
        Returns:
            bool: Success status
        """
        try:
            username = username or os.getenv('METABASE_USERNAME')
            password = password or os.getenv('METABASE_PASSWORD')
            
            if not username or not password:
                logger.error("Metabase credentials not provided")
                return False
            
            url = f"{self.base_url}/api/session"
            response = requests.post(url, json={
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                self.session_token = response.json()['id']
                logger.info("Metabase authentication successful")
                return True
            else:
                logger.error(f"Metabase authentication failed: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Metabase authentication error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with session token."""
        if not self.session_token:
            self.authenticate()
        
        return {
            'X-Metabase-Session': self.session_token,
            'Content-Type': 'application/json'
        }
    
    def create_question(self, name: str, sql: str, description: str = "", 
                       visualization_settings: Optional[Dict] = None) -> Optional[int]:
        """
        Create a Metabase question (saved query).
        
        Args:
            name: Question name
            sql: SQL query (native query)
            description: Question description
            visualization_settings: Chart configuration
        
        Returns:
            int: Question ID or None if failed
        """
        try:
            url = f"{self.base_url}/api/card"
            
            # Default visualization settings
            if visualization_settings is None:
                visualization_settings = {}
            
            data = {
                'name': name,
                'description': description,
                'dataset_query': {
                    'type': 'native',
                    'native': {
                        'query': sql
                    },
                    'database': self.database_id
                },
                'display': visualization_settings.get('display', 'table'),
                'visualization_settings': visualization_settings
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            if response.status_code in [200, 201]:
                question_id = response.json()['id']
                logger.info(f"Created Metabase question: {question_id}")
                return question_id
            else:
                logger.error(f"Failed to create question: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating Metabase question: {e}")
            return None
    
    def create_dashboard(self, name: str, description: str = "") -> Optional[int]:
        """
        Create a Metabase dashboard.
        
        Args:
            name: Dashboard name
            description: Dashboard description
        
        Returns:
            int: Dashboard ID or None if failed
        """
        try:
            url = f"{self.base_url}/api/dashboard"
            
            data = {
                'name': name,
                'description': description
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            if response.status_code in [200, 201]:
                dashboard_id = response.json()['id']
                logger.info(f"Created Metabase dashboard: {dashboard_id}")
                return dashboard_id
            else:
                logger.error(f"Failed to create dashboard: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating Metabase dashboard: {e}")
            return None
    
    def add_question_to_dashboard(self, question_id: int, dashboard_id: int,
                                  row: int = 0, col: int = 0, 
                                  size_x: int = 6, size_y: int = 4) -> bool:
        """
        Add a question to a dashboard.
        
        Args:
            question_id: Question ID
            dashboard_id: Dashboard ID
            row: Row position
            col: Column position
            size_x: Width (in grid units)
            size_y: Height (in grid units)
        
        Returns:
            bool: Success status
        """
        try:
            url = f"{self.base_url}/api/dashboard/{dashboard_id}/cards"
            
            data = {
                'cardId': question_id,
                'row': row,
                'col': col,
                'sizeX': size_x,
                'sizeY': size_y
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Added question {question_id} to dashboard {dashboard_id}")
                return True
            else:
                logger.error(f"Failed to add question to dashboard: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error adding question to dashboard: {e}")
            return False
    
    def get_dashboard(self, dashboard_id: int) -> Optional[Dict]:
        """
        Get dashboard details.
        
        Args:
            dashboard_id: Dashboard ID
        
        Returns:
            dict: Dashboard data or None
        """
        try:
            url = f"{self.base_url}/api/dashboard/{dashboard_id}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get dashboard: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
            return None
    
    def delete_question(self, question_id: int) -> bool:
        """
        Delete a question.
        
        Args:
            question_id: Question ID
        
        Returns:
            bool: Success status
        """
        try:
            url = f"{self.base_url}/api/card/{question_id}"
            response = requests.delete(url, headers=self._get_headers())
            
            if response.status_code == 204:
                logger.info(f"Deleted question {question_id}")
                return True
            else:
                logger.error(f"Failed to delete question: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error deleting question: {e}")
            return False
    
    def enable_dashboard_embedding(self, dashboard_id: int) -> bool:
        """
        Enable embedding for a dashboard.
        
        Args:
            dashboard_id: Dashboard ID
        
        Returns:
            bool: Success status
        """
        try:
            url = f"{self.base_url}/api/dashboard/{dashboard_id}"
            data = {'enable_embedding': True}
            
            response = requests.put(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                logger.info(f"Enabled embedding for dashboard {dashboard_id}")
                return True
            else:
                logger.error(f"Failed to enable embedding: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error enabling embedding: {e}")
            return False
    
    def enable_question_embedding(self, question_id: int) -> bool:
        """
        Enable embedding for a question.
        
        Args:
            question_id: Question ID
        
        Returns:
            bool: Success status
        """
        try:
            url = f"{self.base_url}/api/card/{question_id}"
            data = {'enable_embedding': True}
            
            response = requests.put(
                url,
                json=data,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                logger.info(f"Enabled embedding for question {question_id}")
                return True
            else:
                logger.error(f"Failed to enable embedding: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error enabling embedding: {e}")
            return False


# Singleton instance
_metabase_service = None

def get_metabase_service() -> MetabaseService:
    """Get or create Metabase service singleton."""
    global _metabase_service
    if _metabase_service is None:
        _metabase_service = MetabaseService()
    return _metabase_service

