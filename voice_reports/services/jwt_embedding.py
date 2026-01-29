"""
JWT Embedding Service (Metabase Self-Hosted)

Generates JWT tokens for Metabase embedded dashboards/questions.
Uses the same secret as configured in Metabase Admin > Settings > Embedding.
Optional: only needed if you use embedded iframes; API uses Session Auth only.
"""

import jwt
import time
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class JWTEmbeddingService:
    """
    JWT token generation for Metabase self-hosted embedding.
    Requires METABASE_SECRET_KEY to match Metabase Admin embedding secret.
    """
    
    def __init__(self):
        """Initialize from environment (METABASE_SECRET_KEY optional)."""
        self.secret_key = os.getenv("METABASE_SECRET_KEY")
        self.issuer = os.getenv("JWT_ISSUER", "bi-voice-agent")
        self.audience = os.getenv("JWT_AUDIENCE", "metabase")
        self.metabase_url = (os.getenv("METABASE_URL") or "http://localhost:3000").rstrip("/")
        
        if not self.secret_key:
            logger.debug("METABASE_SECRET_KEY not set - embedding URLs will not be signed")
    
    def _ensure_secret(self) -> None:
        if not self.secret_key:
            raise ValueError(
                "METABASE_SECRET_KEY is not set. Set it in .env to match "
                "Metabase Admin > Settings > Embedding secret for JWT embedding."
            )

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
            ValueError: If resource is invalid or METABASE_SECRET_KEY not set
        """
        self._ensure_secret()
        if not isinstance(resource, dict):
            raise ValueError("Resource must be a dictionary")
        if "type" not in resource or "id" not in resource:
            raise ValueError("Resource must have 'type' and 'id'")
        if resource["type"] not in ("dashboard", "question"):
            raise ValueError("Resource type must be 'dashboard' or 'question'")

        current_time = int(time.time())
        payload = {
            "resource": resource,
            "params": params or {},
            "iat": current_time,
            "exp": current_time + (exp_minutes * 60),
            "iss": self.issuer,
            "aud": self.audience,
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        logger.info("Generated JWT token for %s %s", resource["type"], resource["id"])
        return token
    
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
        Get full embed URL with JWT token (requires METABASE_SECRET_KEY).
        """
        resource = {"type": resource_type, "id": resource_id}
        token = self.generate_embed_token(resource, params)
        embed_url = f"{self.metabase_url}/embed/{resource_type}/{token}"
        if params and "theme" in params:
            embed_url += f"#theme={params['theme']}"
        logger.info("Generated embed URL for %s %s", resource_type, resource_id)
        return embed_url
    
    def get_dashboard_embed_url(self, dashboard_id: int,
                                workspace_id: Optional[int] = None) -> str:
        """
        Dashboard URL: JWT embed if METABASE_SECRET_KEY set, else direct Metabase URL.
        """
        params = {}
        if workspace_id:
            params["workspace_id"] = workspace_id
        try:
            return self.get_embed_url("dashboard", dashboard_id, params)
        except ValueError:
            return f"{self.metabase_url}/dashboard/{dashboard_id}"

    def get_question_embed_url(self, question_id: int,
                              workspace_id: Optional[int] = None) -> str:
        """
        Question URL: JWT embed if METABASE_SECRET_KEY set, else direct Metabase URL.
        """
        params = {}
        if workspace_id:
            params["workspace_id"] = workspace_id
        try:
            return self.get_embed_url("question", question_id, params)
        except ValueError:
            return f"{self.metabase_url}/question/{question_id}"
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token; returns None if secret not set or invalid."""
        if not self.secret_key:
            return None
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            logger.error("JWT verification error: %s", e)
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

