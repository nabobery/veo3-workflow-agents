"""
Streamlined Veo3 configuration using only Google API key.

This module provides a clean, professional configuration system that follows
the Get_started_Veo.ipynb pattern without Vertex AI dependencies.
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from google import genai
from google.genai import types

# Add project root to Python path for local imports
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class Veo3Config(BaseSettings):
    """
    Streamlined configuration for Veo3 video generation workflow.
    
    Following the pattern established in Get_started_Veo.ipynb, this configuration
    provides secure API key management and proper client initialization using
    only the Google API key.
    
    Environment Variables:
    - GOOGLE_API_KEY: Google API key for Gemini and Veo3 access (required)
    - TAVILY_API_KEY: For enhanced search capabilities (optional)
    - VEO3_MODEL: Veo3 model variant (optional)
    - GEMINI_MODEL: Gemini model for prompt enhancement (optional)
    """
    
    # Core Google API Configuration
    GOOGLE_API_KEY: SecretStr = Field(
        ..., 
        description="Google API key for accessing Gemini and Veo3 APIs"
    )
    
    # Model Configuration
    VEO3_MODEL: str = Field(
        default="veo-3.0-fast-generate-preview",
        # default="veo-2.0-generate-001",
        description="Veo3 model variant for video generation"
    )
    
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model for prompt enhancement and processing"
    )
    
    # Video Generation Defaults
    DEFAULT_DURATION_SECONDS: int = Field(
        default=8,
        ge=4,
        le=12,
        description="Default video duration in seconds"
    )
    
    DEFAULT_ASPECT_RATIO: str = Field(
        default="16:9",
        description="Default video aspect ratio"
    )

    DEFAULT_RESOLUTION: str = Field(
        default="1080p",
        description="Default video resolution (720p or 1080p)"
    )
    
    # Agent Configuration
    DEFAULT_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default temperature for AI models"
    )
    
    DEFAULT_NUM_IDEAS: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Default number of prompt ideas to generate"
    )
    
    # Optional API Keys
    TAVILY_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Optional Tavily API key for enhanced search"
    )
    
    # Safety and Performance Settings
    ENABLE_ADULT_GENERATION: bool = Field(
        default=True,
        description="Allow generation of content with adults"
    )
    
    ENABLE_PROMPT_ENHANCEMENT: bool = Field(
        default=True,
        description="Enable automatic prompt enhancement"
    )
    
    MAX_RETRIES: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for API calls"
    )
    
    RETRY_BACKOFF_SECONDS: float = Field(
        default=1.0,
        ge=0.0,
        le=30.0,
        description="Backoff time between retries"
    )
    
    # Development Settings
    DEBUG: bool = Field(
        default=False,
        description="Enable debug logging"
    )
    
    SAVE_INTERMEDIATE_OUTPUTS: bool = Field(
        default=True,
        description="Save intermediate processing outputs"
    )
    
    @field_validator("VEO3_MODEL")
    def validate_veo3_model(cls, v):
        """
        Validate that the VEO3 model identifier is one of the supported model names.
        
        Raises a ValueError if the provided value is not one of:
        ["veo-3.0-generate-preview", "veo-3.0-fast-generate-preview", "veo-2.0-generate-001"].
        """
        valid_models = [
            "veo-3.0-generate-preview",
            "veo-3.0-fast-generate-preview", 
            "veo-2.0-generate-001"
        ]
        if v not in valid_models:
            raise ValueError(f"VEO3_MODEL must be one of: {valid_models}")
        return v
    
    @field_validator("GEMINI_MODEL")
    def validate_gemini_model(cls, v):
        """
        Validate that a Gemini model identifier starts with the required prefix.
        
        Checks that the provided model string begins with "gemini-". Returns the original
        value if valid; raises ValueError if the prefix is missing.
        """
        if not v.startswith("gemini-"):
            raise ValueError("GEMINI_MODEL must start with 'gemini-'")
        return v
    
    @field_validator("DEFAULT_ASPECT_RATIO")
    def validate_aspect_ratio(cls, v):
        """
        Validate that DEFAULT_ASPECT_RATIO is one of the supported aspect ratios.
        
        This validator enforces that the provided value is one of: "16:9", "9:16", or "1:1".
        
        Parameters:
            v (str): Aspect ratio string to validate.
        
        Returns:
            str: The validated aspect ratio (same as input) if valid.
        
        Raises:
            ValueError: If `v` is not one of the allowed aspect ratios.
        """
        valid_ratios = ["16:9", "9:16", "1:1"]
        if v not in valid_ratios:
            raise ValueError(f"DEFAULT_ASPECT_RATIO must be one of: {valid_ratios}")
        return v

    @field_validator("DEFAULT_RESOLUTION")
    def validate_resolution(cls, v):
        """
        Validate that the resolution value is one of the supported options.
        
        Parameters:
            v (str): Resolution string to validate (e.g., "720p", "1080p").
        
        Returns:
            str: The validated resolution string.
        
        Raises:
            ValueError: If `v` is not one of the supported resolutions: ["720p", "1080p"].
        """
        valid_resolutions = ["720p", "1080p"]
        if v not in valid_resolutions:
            raise ValueError(f"DEFAULT_RESOLUTION must be one of: {valid_resolutions}")
        return v

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_assignment=True,
    )


class Veo3ClientManager:
    """
    Streamlined client manager following the Get_started_Veo.ipynb pattern.
    
    This class handles the initialization and management of Google AI clients
    using only the Google API key, without any Vertex AI dependencies.
    """
    
    def __init__(self, config: Veo3Config):
        """
        Initialize the Veo3ClientManager with a Veo3Config.
        
        Parameters:
            config (Veo3Config): Configuration instance providing API keys, model defaults, and runtime options used by the client manager.
        """
        self.config = config
        self._genai_client: Optional[genai.Client] = None
        
    def get_genai_client(self) -> genai.Client:
        """
        Return a lazily initialized Google GenAI client configured with the API key from the Veo3Config.
        
        This method initializes and caches a genai.Client on first call using the secret value from
        self.config.GOOGLE_API_KEY. Subsequent calls return the same client instance.
        
        Returns:
            genai.Client: An authenticated GenAI client ready for use.
        """
        if self._genai_client is None:
            # Configure the library (following Get_started_Veo.ipynb pattern)
            api_key = self.config.GOOGLE_API_KEY.get_secret_value()
            
            # Initialize client (exact pattern from notebook)
            self._genai_client = genai.Client(api_key=api_key)
            
            if self.config.DEBUG:
                print(f"✅ Google GenAI client initialized")
                print(f"🎬 Veo3 Model: {self.config.VEO3_MODEL}")
                print(f"🧠 Gemini Model: {self.config.GEMINI_MODEL}")
        
        return self._genai_client
    
    def get_video_generation_config(
        self,
        duration_seconds: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        enhance_prompt: Optional[bool] = None,
        person_generation: Optional[str] = None
    ) -> types.GenerateVideosConfig:
        """
        Build a GenerateVideosConfig using Veo3Config defaults.
        
        Returns a types.GenerateVideosConfig configured with:
        - aspect_ratio: provided value or config.DEFAULT_ASPECT_RATIO
        - number_of_videos: always 1 (Veo3 usage)
        
        Parameters:
            duration_seconds (Optional[int]): Desired video length in seconds (config enforces valid range). Present for future use but not currently applied to the returned config.
            aspect_ratio (Optional[str]): Aspect ratio override (e.g., "16:9", "9:16", "1:1").
            resolution (Optional[str]): Resolution override (e.g., "720p", "1080p"). Present for future use but not currently applied.
            enhance_prompt (Optional[bool]): Whether to enable prompt enhancement. Present for future use but not currently applied.
            person_generation (Optional[str]): Person-generation policy (e.g., "allow_adult", "allow_none"). Present for future use but not currently applied.
        
        Returns:
            types.GenerateVideosConfig: Video generation configuration object ready to pass to the Veo3 generation call. Note that several optional parameters are accepted by this helper for future compatibility but are intentionally not included in the returned config because the current target model does not support them.
        """
        # Commenting it because was getting bad request as these parameters are not supported by the model yet
        return types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio or self.config.DEFAULT_ASPECT_RATIO,
            number_of_videos=1,  # Always 1 for Veo3 as per documentation
            # duration_seconds=duration_seconds or self.config.DEFAULT_DURATION_SECONDS,
            # resolution=resolution or self.config.DEFAULT_RESOLUTION,
            # person_generation=person_generation or ("allow_adult" if self.config.ENABLE_ADULT_GENERATION else "allow_none"),
            # enhance_prompt=enhance_prompt if enhance_prompt is not None else self.config.ENABLE_PROMPT_ENHANCEMENT,
        )
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate that the module is correctly configured and that the GenAI client can be initialized.
        
        Performs a basic runtime check: attempts to create/obtain the GenAI client and reports overall validity, readiness, and any errors or warnings.
        
        Returns:
            Dict[str, Any]: A dictionary with the following keys:
                - config_valid (bool): True if preliminary checks passed; set to False on exception.
                - genai_client_ready (bool): True if the GenAI client was successfully initialized.
                - errors (List[str]): Error messages encountered during validation.
                - warnings (List[str]): Non-fatal warnings discovered during validation.
                - notes (List[str], optional): Informational notes about the validation (e.g., that Vertex AI is not used).
        """
        validation_results = {
            "config_valid": True,
            "genai_client_ready": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Test GenAI client initialization
            client = self.get_genai_client()
            validation_results["genai_client_ready"] = True
            
            # Note that we no longer use Vertex AI
            validation_results["notes"] = [
                "Using streamlined configuration without Vertex AI dependencies"
            ]
            
        except Exception as e:
            validation_results["config_valid"] = False
            validation_results["errors"].append(str(e))
        
        return validation_results


# Global configuration instance
_config: Optional[Veo3Config] = None
_client_manager: Optional[Veo3ClientManager] = None


def get_veo3_config() -> Veo3Config:
    """
    Return a singleton Veo3Config instance.
    
    Creates and caches a Veo3Config on first call (loads settings from environment and the module's configured .env file). Subsequent calls return the same instance.
     
    Returns:
        Veo3Config: The global, lazily-initialized configuration object.
    """
    global _config
    if _config is None:
        _config = Veo3Config()
    return _config


def get_client_manager() -> Veo3ClientManager:
    """Get global client manager instance"""
    global _client_manager
    if _client_manager is None:
        config = get_veo3_config()
        _client_manager = Veo3ClientManager(config)
    return _client_manager


def get_genai_client() -> genai.Client:
    """Get configured GenAI client (convenience function)"""
    return get_client_manager().get_genai_client()


def validate_veo3_setup() -> Dict[str, Any]:
    """
    Convenience wrapper that validates the global Veo3 configuration and GenAI client.
    
    Calls the singleton Veo3ClientManager.validate_setup() and returns its result.
    
    Returns:
        dict: Validation result with keys:
            - config_valid (bool): True if configuration appears valid.
            - genai_client_ready (bool): True if the GenAI client was initialized successfully.
            - errors (list[str]): List of error messages encountered.
            - warnings (list[str]): List of non-fatal warnings.
            - notes (list[str], optional): Additional informational notes about the setup.
    """
    return get_client_manager().validate_setup()


# Export key classes and functions
__all__ = [
    "Veo3Config",
    "Veo3ClientManager", 
    "get_veo3_config",
    "get_client_manager",
    "get_genai_client",
    "validate_veo3_setup"
]