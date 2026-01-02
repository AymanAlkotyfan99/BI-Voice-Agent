"""
Small Whisper Client

Calls the existing Small Whisper service as a black box.
Sends audio → Receives transcription + intent + SQL
"""

import requests
import logging
import os
from typing import Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class SmallWhisperClient:
    """
    Client for calling Small Whisper service.
    Treats it as a black box API - does NOT rebuild any logic.
    """
    
    def __init__(self):
        """Initialize client with Small Whisper endpoint."""
        # Use settings.SMALL_WHISPER_URL (127.0.0.1 instead of localhost)
        self.base_url = getattr(settings, 'SMALL_WHISPER_URL', 'http://127.0.0.1:8001')
        # Small Whisper URL structure: /api/transcribe/ (NOT /whisper/transcribe/)
        self.transcribe_endpoint = f'{self.base_url}/api/transcribe/'
        self.health_endpoint = f'{self.base_url}/admin/'  # Django admin as health check
        
        # Log configuration at startup
        logger.info(f"Small Whisper Client initialized: {self.base_url}")
        logger.info(f"Transcribe endpoint: {self.transcribe_endpoint}")
    
    def check_health(self) -> bool:
        """
        Check if Small Whisper service is reachable.
        
        Returns:
            bool: True if service is reachable, False otherwise
        """
        try:
            logger.debug(f"Health check: Testing connection to {self.base_url}")
            response = requests.get(self.health_endpoint, timeout=3)
            is_healthy = response.status_code in [200, 301, 302, 404]  # Any response means it's alive
            
            if is_healthy:
                logger.debug(f"Health check PASSED: Small Whisper is reachable (status {response.status_code})")
            else:
                logger.warning(f"Health check FAILED: Unexpected status {response.status_code}")
            
            return is_healthy
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Health check FAILED: Cannot connect to {self.base_url} - {str(e)}")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"Health check FAILED: Timeout connecting to {self.base_url}")
            return False
        except Exception as e:
            logger.error(f"Health check FAILED: Unexpected error - {str(e)}")
            return False
    
    def process_audio(self, audio_file) -> Dict:
        """
        Send audio to Small Whisper and get back transcription + SQL.
        
        Args:
            audio_file: Audio file (Django UploadedFile or file path)
        
        Returns:
            dict: {
                'success': bool,
                'text': transcription text,
                'intent': intent object,
                'sql': generated SQL query,
                'reasoning': reasoning result (if available),
                'error': error message (if failed)
            }
        """
        # Pre-flight health check
        logger.info("=== Starting Small Whisper Request ===")
        logger.info(f"Target URL: {self.transcribe_endpoint}")
        
        if not self.check_health():
            error_msg = f"Small Whisper service is not reachable at {self.base_url}. Please ensure it is running on port 8001."
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        
        try:
            # Prepare file for upload
            file_to_close = None
            if hasattr(audio_file, 'read'):
                # Django UploadedFile
                logger.debug(f"Using Django UploadedFile: {getattr(audio_file, 'name', 'unknown')}")
                # Reset file pointer to beginning
                audio_file.seek(0)
                files = {'audio': (getattr(audio_file, 'name', 'audio.wav'), audio_file, 'audio/wav')}
            else:
                # File path
                logger.debug(f"Opening file from path: {audio_file}")
                file_handle = open(audio_file, 'rb')
                file_to_close = file_handle
                files = {'audio': (os.path.basename(audio_file), file_handle, 'audio/wav')}
            
            logger.info(f"📤 Sending audio to Small Whisper: {self.transcribe_endpoint}")
            
            # Call Small Whisper endpoint with explicit timeout
            response = requests.post(
                self.transcribe_endpoint,
                files=files,
                timeout=90  # Increased timeout for Whisper processing
            )
            
            # Close file if we opened it
            if file_to_close:
                file_to_close.close()
            
            logger.info(f"📥 Received response from Small Whisper: Status {response.status_code}")
            
            if response.status_code != 200:
                error_detail = response.text[:500]  # First 500 chars
                logger.error(f"❌ Small Whisper error: {response.status_code}")
                logger.error(f"Response body: {error_detail}")
                return {
                    'success': False,
                    'error': f"Small Whisper returned {response.status_code}: {error_detail}"
                }
            
            # Parse response
            try:
                result = response.json()
            except ValueError as e:
                logger.error(f"❌ Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response.text[:500]}")
                return {
                    'success': False,
                    'error': 'Small Whisper returned invalid JSON response'
                }
            
            logger.info("✅ Small Whisper processing successful")
            logger.debug(f"Response keys: {list(result.keys())}")
            
            # Extract data from Small Whisper response
            # Small Whisper returns: {text, reasoning, llm}
            # llm contains: {intent, sql}
            
            text = result.get('text', '')
            sql = result.get('llm', {}).get('sql', '')
            
            logger.info(f"📝 Transcription: {text[:100]}...")
            logger.info(f"🔍 SQL Generated: {sql[:100]}...")
            
            return {
                'success': True,
                'text': text,
                'reasoning': result.get('reasoning'),
                'intent': result.get('llm', {}).get('intent'),
                'sql': sql,
                'raw_response': result
            }
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Cannot connect to Small Whisper at {self.transcribe_endpoint}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"ConnectionError details: {str(e)}")
            return {
                'success': False,
                'error': f'Small Whisper service is not reachable at {self.base_url}. Verify it is running on port 8001.'
            }
        
        except requests.exceptions.Timeout:
            error_msg = f"Request to Small Whisper timed out after 90 seconds"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'error': 'Small Whisper processing timed out. The audio file may be too long or the service is overloaded.'
            }
        
        except Exception as e:
            logger.error(f"❌ Unexpected error calling Small Whisper: {type(e).__name__}", exc_info=True)
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
        finally:
            logger.info("=== Small Whisper Request Complete ===\n")


# Singleton instance
_small_whisper_client = None

def get_small_whisper_client() -> SmallWhisperClient:
    """Get or create Small Whisper client singleton."""
    global _small_whisper_client
    if _small_whisper_client is None:
        _small_whisper_client = SmallWhisperClient()
    return _small_whisper_client

