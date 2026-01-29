"""
Metabase Self-Hosted Integration Service

Integrates with a local Metabase instance (e.g. Docker) using Session Authentication only.
No API keys, no Cloud endpoints, no Bearer tokens.

- Authenticates via POST /api/session (username/password from env)
- Uses X-Metabase-Session header for all API calls
- Caches session in memory and re-authenticates on 401

Environment: METABASE_URL, METABASE_USERNAME, METABASE_PASSWORD, METABASE_DATABASE_ID
"""

import os
import logging
import requests
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# In-memory session cache (singleton service holds its own token)
_session_token: Optional[str] = None


def get_metabase_session(force_refresh: bool = False) -> Optional[str]:
    """
    Authenticate with Metabase Self-Hosted and return session ID.
    Uses POST {METABASE_URL}/api/session with username/password from env.
    Result is cached in memory; pass force_refresh=True to re-login.

    Returns:
        Session ID string, or None if credentials missing or login failed.
    """
    global _session_token
    if _session_token and not force_refresh:
        return _session_token

    base_url = os.getenv("METABASE_URL")
    username = os.getenv("METABASE_USERNAME")
    password = os.getenv("METABASE_PASSWORD")

    if not base_url or not username or not password:
        logger.error("METABASE_URL, METABASE_USERNAME, METABASE_PASSWORD must be set")
        return None

    url = f"{base_url.rstrip('/')}/api/session"
    try:
        response = requests.post(
            url,
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            _session_token = data.get("id")
            if _session_token:
                logger.info("Metabase session obtained successfully")
                return _session_token
        logger.error(
            "Metabase login failed: status=%s body=%s",
            response.status_code,
            response.text[:200],
        )
    except Exception as e:
        logger.error("Metabase session error: %s", e)
    _session_token = None
    return None


def clear_metabase_session() -> None:
    """Clear cached session (e.g. after 401)."""
    global _session_token
    _session_token = None


def get_metabase_headers() -> Dict[str, str]:
    """
    Headers for Metabase API: X-Metabase-Session + Content-Type.
    Call get_metabase_session() first; if None, API calls will fail.
    """
    session_id = get_metabase_session()
    headers = {"Content-Type": "application/json"}
    if session_id:
        headers["X-Metabase-Session"] = session_id
    return headers


class MetabaseService:
    """
    Metabase Self-Hosted API client.
    All calls use Session Authentication only (X-Metabase-Session).
    """

    def __init__(self) -> None:
        self.base_url = (os.getenv("METABASE_URL") or "http://localhost:3000").rstrip("/")
        self.database_id = int(os.getenv("METABASE_DATABASE_ID", "1"))

    def _headers(self) -> Dict[str, str]:
        return get_metabase_headers()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        retry_on_401: bool = True,
    ) -> Optional[requests.Response]:
        """
        Send request to Metabase API. On 401, clear session, re-auth, retry once.
        path is relative to base_url (e.g. /api/card).
        """
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        headers = self._headers()
        if not headers.get("X-Metabase-Session"):
            if not get_metabase_session():
                return None
            headers = self._headers()

        try:
            kwargs = {"headers": headers, "timeout": 30}
            if json is not None and method.upper() != "GET":
                kwargs["json"] = json
            response = requests.request(method, url, **kwargs)
            if response.status_code == 401 and retry_on_401:
                clear_metabase_session()
                if get_metabase_session(force_refresh=True):
                    headers = self._headers()
                    kwargs["headers"] = headers
                    response = requests.request(method, url, **kwargs)
            return response
        except Exception as e:
            logger.error("Metabase request error %s %s: %s", method, path, e)
            return None

    def authenticate(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Ensure we have a valid session (optional username/password override).
        For self-hosted, env METABASE_USERNAME / METABASE_PASSWORD are used if not passed.
        """
        if username and password:
            # Temporarily override env for this process is not ideal; prefer env.
            # So we only use env here.
            pass
        return get_metabase_session(force_refresh=True) is not None

    def create_question(
        self,
        name: str,
        sql: str,
        description: str = "",
        visualization_settings: Optional[Dict] = None,
    ) -> Optional[int]:
        """
        Create a Metabase card (native SQL question).
        Use the same SQL that was executed successfully in ClickHouse.
        """
        if visualization_settings is None:
            visualization_settings = {}
        data = {
            "name": name,
            "description": description,
            "dataset_query": {
                "type": "native",
                "native": {"query": sql},
                "database": self.database_id,
            },
            "display": visualization_settings.get("display", "table"),
            "visualization_settings": visualization_settings,
        }
        response = self._request("POST", "/api/card", json=data)
        if response and response.status_code in (200, 201):
            question_id = response.json().get("id")
            logger.info("Created Metabase question id=%s", question_id)
            return question_id
        if response:
            logger.error("Create question failed: %s %s", response.status_code, response.text[:200])
        return None

    def update_question(
        self,
        card_id: int,
        name: str,
        sql: str,
        description: str = "",
        visualization_settings: Optional[Dict] = None,
    ) -> bool:
        """
        Update an existing Metabase card with new name/SQL/settings.
        Use this to bind updated ClickHouse SQL to an existing visualization.
        """
        if visualization_settings is None:
            visualization_settings = {}
        data = {
            "name": name,
            "description": description,
            "dataset_query": {
                "type": "native",
                "native": {"query": sql},
                "database": self.database_id,
            },
            "display": visualization_settings.get("display", "table"),
            "visualization_settings": visualization_settings,
        }
        response = self._request("PUT", f"/api/card/{card_id}", json=data)
        if response and response.status_code == 200:
            logger.info("Updated Metabase question id=%s", card_id)
            return True
        if response:
            logger.error("Update question failed: %s %s", response.status_code, response.text[:200])
        return False

    def create_dashboard(self, name: str, description: str = "") -> Optional[int]:
        """Create a Metabase dashboard."""
        response = self._request(
            "POST", "/api/dashboard", json={"name": name, "description": description}
        )
        if response and response.status_code in (200, 201):
            dashboard_id = response.json().get("id")
            logger.info("Created Metabase dashboard id=%s", dashboard_id)
            return dashboard_id
        if response:
            logger.error("Create dashboard failed: %s %s", response.status_code, response.text[:200])
        return None

    def update_dashboard(self, dashboard_id: int, name: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update dashboard name/description."""
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if not payload:
            return True
        response = self._request("PUT", f"/api/dashboard/{dashboard_id}", json=payload)
        if response and response.status_code == 200:
            return True
        return False

    def add_question_to_dashboard(
        self,
        question_id: int,
        dashboard_id: int,
        row: int = 0,
        col: int = 0,
        size_x: int = 6,
        size_y: int = 4,
    ) -> bool:
        """Add a question (card) to a dashboard."""
        response = self._request(
            "POST",
            f"/api/dashboard/{dashboard_id}/cards",
            json={
                "cardId": question_id,
                "row": row,
                "col": col,
                "sizeX": size_x,
                "sizeY": size_y,
            },
        )
        if response and response.status_code in (200, 201):
            logger.info("Added question %s to dashboard %s", question_id, dashboard_id)
            return True
        if response:
            logger.error("Add to dashboard failed: %s %s", response.status_code, response.text[:200])
        return False

    def get_dashboard(self, dashboard_id: int) -> Optional[Dict]:
        """Get dashboard details."""
        response = self._request("GET", f"/api/dashboard/{dashboard_id}")
        if response and response.status_code == 200:
            return response.json()
        return None

    def get_card(self, card_id: int) -> Optional[Dict]:
        """Get card (question) details."""
        response = self._request("GET", f"/api/card/{card_id}")
        if response and response.status_code == 200:
            return response.json()
        return None

    def delete_question(self, question_id: int) -> bool:
        """Delete a question (card)."""
        response = self._request("DELETE", f"/api/card/{question_id}")
        if response and response.status_code == 204:
            logger.info("Deleted question id=%s", question_id)
            return True
        return False

    def enable_dashboard_embedding(self, dashboard_id: int) -> bool:
        """Enable embedding for a dashboard (self-hosted embedding)."""
        response = self._request(
            "PUT", f"/api/dashboard/{dashboard_id}", json={"enable_embedding": True}
        )
        if response and response.status_code == 200:
            logger.info("Enabled embedding for dashboard %s", dashboard_id)
            return True
        return False

    def enable_question_embedding(self, question_id: int) -> bool:
        """Enable embedding for a question (self-hosted embedding)."""
        response = self._request(
            "PUT", f"/api/card/{question_id}", json={"enable_embedding": True}
        )
        if response and response.status_code == 200:
            logger.info("Enabled embedding for question %s", question_id)
            return True
        return False


_metabase_service: Optional[MetabaseService] = None


def get_metabase_service() -> MetabaseService:
    """Get or create Metabase service singleton (self-hosted, session auth only)."""
    global _metabase_service
    if _metabase_service is None:
        _metabase_service = MetabaseService()
    return _metabase_service
