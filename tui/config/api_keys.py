"""
API Key management with secure storage capabilities.

This module provides functionality to manage API keys similar to how the Gemini CLI
handles credentials, with options for environment variables or secure file storage.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, SecretStr

try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    Fernet = None

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    keyring = None

from .settings import get_settings


class APIKeyStore(BaseModel):
    """Secure storage for API keys."""
    
    google_api_key: Optional[SecretStr] = None
    tavily_api_key: Optional[SecretStr] = None
    exa_api_key: Optional[SecretStr] = None
    linkup_api_key: Optional[SecretStr] = None
    
    class Config:
        arbitrary_types_allowed = True


class APIKeyManager:
    """
    Manages API keys with multiple storage backends.
    
    Supports:
    1. Environment variables (highest priority)
    2. System keyring (secure, cross-platform)
    3. Encrypted file storage (fallback)
    4. Plain file storage (development only)
    """
    
    SERVICE_NAME = "veo3-workflow-tui"
    KEY_FILE_NAME = "api_keys.json"
    ENCRYPTED_KEY_FILE_NAME = "api_keys.enc"
    
    def __init__(self):
        self.settings = get_settings()
        self.config_dir = self.settings.CONFIG_DIR
        self.key_file_path = self.config_dir / self.KEY_FILE_NAME
        self.encrypted_key_file_path = self.config_dir / self.ENCRYPTED_KEY_FILE_NAME
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get an API key for a service.
        
        Checks in order:
        1. Environment variable
        2. System keyring
        3. Encrypted file
        4. Plain file
        """
        # 1. Check environment variables first
        env_key = self._get_env_key(service)
        if env_key:
            return env_key
        
        # 2. Check system keyring
        keyring_key = self._get_keyring_key(service)
        if keyring_key:
            return keyring_key
        
        # 3. Check encrypted file
        encrypted_key = self._get_encrypted_file_key(service)
        if encrypted_key:
            return encrypted_key
        
        # 4. Check plain file (development only)
        file_key = self._get_file_key(service)
        return file_key
    
    def set_api_key(self, service: str, api_key: str, storage_method: str = "keyring") -> bool:
        """
        Set an API key for a service.
        
        Args:
            service: Service name (e.g., 'google', 'tavily')
            api_key: The API key to store
            storage_method: 'keyring', 'encrypted_file', or 'file'
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if storage_method == "keyring":
                return self._set_keyring_key(service, api_key)
            elif storage_method == "encrypted_file":
                return self._set_encrypted_file_key(service, api_key)
            elif storage_method == "file":
                return self._set_file_key(service, api_key)
            else:
                raise ValueError(f"Unknown storage method: {storage_method}")
        except Exception as e:
            print(f"Failed to set API key for {service}: {e}")
            return False
    
    def delete_api_key(self, service: str) -> bool:
        """Delete an API key for a service from all storage methods."""
        success = True
        
        # Delete from keyring
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(self.SERVICE_NAME, service)
            except Exception:
                # PasswordDeleteError or other keyring errors
                pass
        
        # Delete from files
        try:
            self._delete_file_key(service)
        except Exception:
            success = False
        
        return success
    
    def list_stored_keys(self) -> Dict[str, bool]:
        """List which API keys are currently stored."""
        services = ["google", "tavily", "exa", "linkup"]
        stored = {}
        
        for service in services:
            stored[service] = self.get_api_key(service) is not None
        
        return stored
    
    def _get_env_key(self, service: str) -> Optional[str]:
        """Get API key from environment variables."""
        env_var_map = {
            "google": "GOOGLE_API_KEY",
            "tavily": "TAVILY_API_KEY", 
            "exa": "EXA_API_KEY",
            "linkup": "LINKUP_API_KEY"
        }
        
        env_var = env_var_map.get(service)
        if env_var:
            # Check both with and without VEO3_ prefix
            return os.getenv(env_var) or os.getenv(f"VEO3_{env_var}")
        return None
    
    def _get_keyring_key(self, service: str) -> Optional[str]:
        """Get API key from system keyring."""
        if not KEYRING_AVAILABLE:
            return None
        try:
            return keyring.get_password(self.SERVICE_NAME, service)
        except Exception:
            return None
    
    def _set_keyring_key(self, service: str, api_key: str) -> bool:
        """Set API key in system keyring."""
        if not KEYRING_AVAILABLE:
            return False
        try:
            keyring.set_password(self.SERVICE_NAME, service, api_key)
            return True
        except Exception:
            return False
    
    def _get_encrypted_file_key(self, service: str) -> Optional[str]:
        """Get API key from encrypted file."""
        if not CRYPTOGRAPHY_AVAILABLE or not self.encrypted_key_file_path.exists():
            return None
        
        try:
            # Use a key derived from the user's system
            key = self._get_encryption_key()
            fernet = Fernet(key)
            
            with open(self.encrypted_key_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
            
            return data.get(service)
        except Exception:
            return None
    
    def _set_encrypted_file_key(self, service: str, api_key: str) -> bool:
        """Set API key in encrypted file."""
        if not CRYPTOGRAPHY_AVAILABLE:
            return False
        try:
            # Load existing data or create new
            data = {}
            if self.encrypted_key_file_path.exists():
                existing_key = self._get_encrypted_file_key("dummy")  # Load existing data
                if existing_key is not None:
                    # File exists and is readable, load all data
                    key = self._get_encryption_key()
                    fernet = Fernet(key)
                    with open(self.encrypted_key_file_path, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = fernet.decrypt(encrypted_data)
                    data = json.loads(decrypted_data.decode())
            
            # Update with new key
            data[service] = api_key
            
            # Encrypt and save
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(json.dumps(data).encode())
            
            with open(self.encrypted_key_file_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception:
            return False
    
    def _get_file_key(self, service: str) -> Optional[str]:
        """Get API key from plain text file (development only)."""
        if not self.key_file_path.exists():
            return None
        
        try:
            with open(self.key_file_path, 'r') as f:
                data = json.load(f)
            return data.get(service)
        except Exception:
            return None
    
    def _set_file_key(self, service: str, api_key: str) -> bool:
        """Set API key in plain text file (development only)."""
        try:
            # Load existing data or create new
            data = {}
            if self.key_file_path.exists():
                with open(self.key_file_path, 'r') as f:
                    data = json.load(f)
            
            # Update with new key
            data[service] = api_key
            
            # Save
            with open(self.key_file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def _delete_file_key(self, service: str) -> bool:
        """Delete API key from file storage."""
        success = True
        
        # Delete from plain file
        if self.key_file_path.exists():
            try:
                with open(self.key_file_path, 'r') as f:
                    data = json.load(f)
                
                if service in data:
                    del data[service]
                    
                    if data:  # If there are still keys, save the file
                        with open(self.key_file_path, 'w') as f:
                            json.dump(data, f, indent=2)
                    else:  # If no keys left, delete the file
                        self.key_file_path.unlink()
            except Exception:
                success = False
        
        # Delete from encrypted file
        if self.encrypted_key_file_path.exists():
            try:
                key = self._get_encryption_key()
                fernet = Fernet(key)
                
                with open(self.encrypted_key_file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = fernet.decrypt(encrypted_data)
                data = json.loads(decrypted_data.decode())
                
                if service in data:
                    del data[service]
                    
                    if data:  # If there are still keys, save the file
                        encrypted_data = fernet.encrypt(json.dumps(data).encode())
                        with open(self.encrypted_key_file_path, 'wb') as f:
                            f.write(encrypted_data)
                    else:  # If no keys left, delete the file
                        self.encrypted_key_file_path.unlink()
            except Exception:
                success = False
        
        return success
    
    def _get_encryption_key(self) -> bytes:
        """Get or create an encryption key for the current user."""
        if not CRYPTOGRAPHY_AVAILABLE:
            return b""
        
        key_file = self.config_dir / ".encryption_key"
        
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception:
                pass
        
        # Generate new key
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            # Make file readable only by owner
            key_file.chmod(0o600)
        except Exception:
            pass
        
        return key
