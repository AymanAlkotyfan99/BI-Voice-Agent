"""
JWT Embedding Service

Generates secure JWT tokens for Metabase embedding.
CRITICAL SECURITY: Tokens are short-lived and signed server-side only.
"""

import jwt
import time
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class JWTEmbeddingService:
    """
    JWT token generation for secure Metabase embedding.
    
    Security Features:
    - HS256 algorithm
    - Short-lived tokens (10 minutes)
    - Server-side signing only
    - Workspace-scoped parameters
    """
    
    def __init__(self):
        """Initialize JWT service with secret key from environment."""
        self.secret_key = os.getenv('b1abade2a5822ad12387ccc097c63cafcbdcaa2844dc76a4bdbfec15d06592f8')
        self.issuer = os.getenv('JWT_ISSUER', 'bi-voice-agent')
        self.audience = os.getenv('JWT_AUDIENCE', 'metabase')
        self.metabase_url = os.getenv('METABASE_URL', 'http://localhost:3000')
        
        if not self.secret_key:
            logger.error("METABASE_SECRET_KEY not set - JWT signing will fail")
            raise ValueError("METABASE_SECRET_KEY environment variable is required")
    
    def generate_embed_token(self, resource: Dict, params: Optional[Dict] = None,
                            exp_minutes: int = 10) -> str:
        """
        Generate JWT token for embedding.
        
        Args:
            resource: {'type': 'dashboard'|'question', 'id': int}
            params: Optional parameters (filters, workspace_id, etc.)
            exp_minutes: Token expiration in minutes (default: 10)
        
        Returns:
            str: JWT token
        
        Raises:
            ValueError: If resource is invalid
        """
        try:
            # Validate resource
            if not isinstance(resource, dict):
                raise ValueError("Resource must be a dictionary")
            
            if 'type' not in resource or 'id' not in resource:
                raise ValueError("Resource must have 'type' and 'id'")
            
            if resource['type'] not in ['dashboard', 'question']:
                raise ValueError("Resource type must be 'dashboard' or 'question'")
            
            # Build JWT payload
            current_time = int(time.time())
            
            payload = {
                'resource': resource,
                'params': params or {},
                'iat': current_time,  # Issued at
                'exp': current_time + (exp_minutes * 60),  # Expiration
                'iss': self.issuer,  # Issuer
                'aud': self.audience  # Audience
            }
            
            # Sign token
            token = jwt.encode(
                payload,
                self.secret_key,
                algorithm='HS256'
            )
            
            logger.info(f"Generated JWT token for {resource['type']} {resource['id']}")
            
            # Handle both string and bytes return from jwt.encode
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            
            return token
        
        except Exception as e:
            logger.error(f"Failed to generate JWT token: {e}")
            raise
    
    def generate_dashboard_token(self, dashboard_id: int, params: Optional[Dict] = None) -> str:
        """
        Generate token specifically for dashboard embedding.
        
        Args:
            dashboard_id: Metabase dashboard ID
            params: Optional dashboard parameters
        
        Returns:
            str: JWT token
        """
        resource = {'type': 'dashboard', 'id': dashboard_id}
        return self.generate_embed_token(resource, params)
    
    def generate_question_token(self, question_id: int, params: Optional[Dict] = None) -> str:
        """
        Generate token specifically for question embedding.
        
        Args:
            question_id: Metabase question ID
            params: Optional question parameters
        
        Returns:
            str: JWT token
        """
        resource = {'type': 'question', 'id': question_id}
        return self.generate_embed_token(resource, params)
    
    def get_embed_url(self, resource_type: str, resource_id: int, 
                     params: Optional[Dict] = None) -> str:
        """
        Get full embed URL with JWT token.
        
        Args:
            resource_type: 'dashboard' or 'question'
            resource_id: Resource ID
            params: Optional parameters
        
        Returns:
            str: Full embed URL with JWT token
        """
        try:
            # Generate token
            resource = {'type': resource_type, 'id': resource_id}
            token = self.generate_embed_token(resource, params)
            
            # Build embed URL
            embed_url = f"{self.metabase_url}/embed/{resource_type}/{token}"
            
            # Add theme parameter if needed
            if params and 'theme' in params:
                embed_url += f"#theme={params['theme']}"
            
            logger.info(f"Generated embed URL for {resource_type} {resource_id}")
            
            return embed_url
        
        except Exception as e:
            logger.error(f"Failed to generate embed URL: {e}")
            raise
    
    def get_dashboard_embed_url(self, dashboard_id: int, 
                               workspace_id: Optional[int] = None) -> str:
        """
        Get dashboard embed URL with workspace filtering.
        
        Args:
            dashboard_id: Metabase dashboard ID
            workspace_id: Optional workspace ID for filtering
        
        Returns:
            str: Dashboard embed URL
        """
        params = {}
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        return self.get_embed_url('dashboard', dashboard_id, params)
    
    def get_question_embed_url(self, question_id: int,
                              workspace_id: Optional[int] = None) -> str:
        """
        Get question embed URL with workspace filtering.
        
        Args:
            question_id: Metabase question ID
            workspace_id: Optional workspace ID for filtering
        
        Returns:
            str: Question embed URL
        """
        params = {}
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        return self.get_embed_url('question', question_id, params)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            dict: Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256'],
                audience=self.audience,
                issuer=self.issuer
            )
            
            logger.info("JWT token verified successfully")
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        
        except Exception as e:
            logger.error(f"JWT verification error: {e}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired.
        
        Args:
            token: JWT token string
        
        Returns:
            bool: True if expired or invalid
        """
        payload = self.verify_token(token)
        return payload is None


# Singleton instance
_jwt_service = None

def get_jwt_service() -> JWTEmbeddingService:
    """Get or create JWT service singleton."""
    global _jwt_service
    if _jwt_service is None:
        _jwt_service = JWTEmbeddingService()
    return _jwt_service

