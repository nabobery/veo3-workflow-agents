"""
Video generation integration using Google's Veo3 model.

This module provides video generation capabilities using Google AI's video generation API.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

try:
    import google.genai as genai
    from google.genai.types import Content, Part
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    logging.warning("google-genai package not available")
    GOOGLE_GENAI_AVAILABLE = False

from tui.config import get_settings
from tui.utils.errors import (
    APIKeyError, 
    ModelError, 
    ValidationError, 
    VideoGenerationError,
    APILimitError,
    TimeoutError
)
from tui.utils.validators import validate_prompt, validate_video_params


logger = logging.getLogger(__name__)


class VideoGenerator:
    """
    Video generation manager using Google's Veo3 model.
    
    This class handles video generation requests, parameter validation,
    and result processing for the Veo3 video generation model.
    """
    
    def __init__(self):
        """Initialize the video generator."""
        self.settings = get_settings()
        self.client = None
        self._validate_setup()
    
    def _validate_setup(self) -> None:
        """Validate that the setup is correct for video generation."""
        if not GOOGLE_GENAI_AVAILABLE:
            raise ImportError("google-genai package is not available")
        
        if not self.settings.get_google_api_key():
            raise APIKeyError("google", "Google API key is required for video generation")
    
    def _get_client(self):
        """Get or create the Google GenAI client."""
        if self.client is None:
            if not GOOGLE_GENAI_AVAILABLE:
                raise ImportError("google-genai package is not available")
            
            api_key = self.settings.get_google_api_key()
            if not api_key:
                raise APIKeyError("google", "Google API key is not configured")
            
            # Configure the client
            genai.configure(api_key=api_key)
            self.client = genai
        
        return self.client
    
    async def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        quality: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a video from a text prompt.
        
        Args:
            prompt: Text description of the video to generate
            duration: Duration in seconds (default from settings)
            quality: Video quality ("low", "medium", "high")
            aspect_ratio: Video aspect ratio ("16:9", "9:16", "1:1", etc.)
            style: Video style ("cinematic", "photorealistic", etc.)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary containing generation results and metadata
        
        Raises:
            ValidationError: If parameters are invalid
            APIKeyError: If API key is missing or invalid
            VideoGenerationError: If video generation fails
            APILimitError: If API limits are exceeded
            TimeoutError: If generation times out
        """
        # Validate prompt
        prompt = validate_prompt(prompt)
        
        # Prepare parameters
        params = {
            "duration": duration or self.settings.VIDEO_DURATION,
            "quality": quality or self.settings.VIDEO_QUALITY,
            "aspect_ratio": aspect_ratio or self.settings.VIDEO_ASPECT_RATIO,
        }
        
        if style:
            params["style"] = style
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Validate video parameters
        validated_params = validate_video_params(params)
        
        if not GOOGLE_GENAI_AVAILABLE:
            # Return mock data for development
            return self._generate_mock_video(prompt, validated_params)
        
        try:
            client = self._get_client()
            result = await self._generate_with_api(client, prompt, validated_params)
            return result
        
        except Exception as e:
            logger.error(f"Failed to generate video: {e}", exc_info=True)
            self._handle_error(e, prompt)
    
    async def _generate_with_api(
        self, 
        client, 
        prompt: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate video using the actual Google API.
        
        Args:
            client: Google GenAI client
            prompt: Validated prompt
            params: Validated parameters
        
        Returns:
            Generation result dictionary
        """
        try:
            # For now, this is a placeholder since the actual Veo3 API
            # may not be publicly available yet. This would be replaced
            # with the actual API calls when available.
            
            # Example of what the API call might look like:
            # model = client.GenerativeModel(self.settings.VEO3_MODEL)
            # 
            # generation_config = {
            #     "duration": params["duration"],
            #     "quality": params["quality"],
            #     "aspect_ratio": params["aspect_ratio"],
            #     **{k: v for k, v in params.items() if k not in ["duration", "quality", "aspect_ratio"]}
            # }
            # 
            # response = await model.generate_video_async(
            #     prompt=prompt,
            #     generation_config=generation_config
            # )
            
            # For now, return a mock response
            return self._generate_mock_video(prompt, params)
            
        except Exception as e:
            logger.error(f"API call failed: {e}", exc_info=True)
            raise VideoGenerationError(str(e), prompt)
    
    def _generate_mock_video(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock video data for development and testing.
        
        Args:
            prompt: The video prompt
            params: Video parameters
        
        Returns:
            Mock generation result
        """
        return {
            "status": "completed",
            "video_id": f"mock_video_{hash(prompt) % 10000}",
            "prompt": prompt,
            "parameters": params,
            "duration": params.get("duration", 30),
            "quality": params.get("quality", "high"),
            "aspect_ratio": params.get("aspect_ratio", "16:9"),
            "file_size_mb": params.get("duration", 30) * 2,  # Mock: 2MB per second
            "download_url": "https://mock.example.com/video.mp4",
            "thumbnail_url": "https://mock.example.com/thumbnail.jpg",
            "created_at": "2024-01-01T12:00:00Z",
            "processing_time_seconds": 45,
            "credits_used": 10,
            "metadata": {
                "model": self.settings.VEO3_MODEL,
                "api_version": "v1",
                "resolution": self._get_resolution_for_aspect_ratio(params.get("aspect_ratio", "16:9")),
                "fps": 24,
                "format": "mp4",
                "codec": "h264"
            }
        }
    
    def _get_resolution_for_aspect_ratio(self, aspect_ratio: str) -> str:
        """Get appropriate resolution for aspect ratio."""
        resolution_map = {
            "16:9": "1920x1080",
            "9:16": "1080x1920", 
            "1:1": "1080x1080",
            "4:3": "1440x1080",
            "3:4": "1080x1440"
        }
        return resolution_map.get(aspect_ratio, "1920x1080")
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a video generation request.
        
        Args:
            video_id: ID of the video generation request
        
        Returns:
            Status information dictionary
        
        Raises:
            ValidationError: If video_id is invalid
            APIKeyError: If API key is missing
            VideoGenerationError: If status check fails
        """
        if not video_id or not video_id.strip():
            raise ValidationError("video_id", video_id, "Video ID cannot be empty")
        
        if not GOOGLE_GENAI_AVAILABLE:
            # Return mock status for development
            return {
                "video_id": video_id,
                "status": "completed",
                "progress": 100,
                "estimated_completion": None,
                "download_url": "https://mock.example.com/video.mp4"
            }
        
        try:
            client = self._get_client()
            # This would be replaced with actual API call
            # status = await client.get_video_status(video_id)
            
            # Mock response for now
            return {
                "video_id": video_id,
                "status": "completed",
                "progress": 100,
                "estimated_completion": None,
                "download_url": "https://mock.example.com/video.mp4"
            }
            
        except Exception as e:
            logger.error(f"Failed to get video status: {e}", exc_info=True)
            self._handle_error(e)
    
    async def download_video(self, video_id: str, output_path: Optional[Path] = None) -> Path:
        """
        Download a generated video.
        
        Args:
            video_id: ID of the video to download
            output_path: Path to save the video (optional)
        
        Returns:
            Path to the downloaded video file
        
        Raises:
            ValidationError: If video_id is invalid
            VideoGenerationError: If download fails
        """
        if not video_id or not video_id.strip():
            raise ValidationError("video_id", video_id, "Video ID cannot be empty")
        
        if output_path is None:
            output_path = self.settings.OUTPUT_DIR / f"{video_id}.mp4"
        
        if not GOOGLE_GENAI_AVAILABLE:
            # Create a mock file for development
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("Mock video file content")
            return output_path
        
        try:
            # This would be replaced with actual download implementation
            # video_data = await client.download_video(video_id)
            # output_path.write_bytes(video_data)
            
            # Mock implementation for now
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("Mock video file content")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to download video: {e}", exc_info=True)
            raise VideoGenerationError(f"Download failed: {str(e)}", video_id)
    
    def _handle_error(self, error: Exception, prompt: Optional[str] = None) -> None:
        """
        Handle and re-raise errors with appropriate TUI error types.
        
        Args:
            error: The original error to handle
            prompt: Optional prompt that caused the error
        
        Raises:
            Appropriate TUI error type based on the original error
        """
        error_msg = str(error).lower()
        
        # Check for API key errors
        if "api key" in error_msg or "authentication" in error_msg:
            raise APIKeyError("google", str(error))
        
        # Check for rate limiting errors
        if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
            raise APILimitError("google", "rate", str(error))
        
        # Check for timeout errors
        if "timeout" in error_msg or "deadline" in error_msg:
            raise TimeoutError("google", 300.0, str(error))  # Assume 5 minute timeout
        
        # Check for model errors
        if "model" in error_msg or self.settings.VEO3_MODEL in error_msg:
            raise ModelError(self.settings.VEO3_MODEL, str(error))
        
        # Re-raise as generic video generation error
        raise VideoGenerationError(str(error), prompt)
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available video generation models.
        
        Returns:
            List of available model names
        """
        return [
            "video-generation-001",
            "veo-3", 
            "veo-2"
        ]
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get supported video formats and options.
        
        Returns:
            Dictionary of supported options
        """
        return {
            "qualities": ["low", "medium", "high", "ultra"],
            "aspect_ratios": ["16:9", "9:16", "1:1", "4:3", "3:4"],
            "styles": [
                "cinematic", "photorealistic", "animated", "artistic",
                "documentary", "vintage", "modern", "fantasy"
            ],
            "durations": {
                "min": 1,
                "max": 300,
                "recommended": [5, 10, 15, 30, 60]
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of video generation integration.
        
        Returns:
            Dictionary containing status information
        """
        status = {
            "available": GOOGLE_GENAI_AVAILABLE,
            "google_api_key": bool(self.settings.get_google_api_key()),
            "current_model": self.settings.VEO3_MODEL,
            "default_duration": self.settings.VIDEO_DURATION,
            "default_quality": self.settings.VIDEO_QUALITY,
            "default_aspect_ratio": self.settings.VIDEO_ASPECT_RATIO,
            "output_directory": str(self.settings.OUTPUT_DIR),
        }
        
        # Check if minimum requirements are met
        status["ready"] = (
            status["available"] and 
            status["google_api_key"]
        )
        
        return status
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the current configuration and return any issues.
        
        Returns:
            List of validation error messages (empty if no issues)
        """
        issues = []
        
        if not GOOGLE_GENAI_AVAILABLE:
            issues.append("google-genai package is not available")
        
        if not self.settings.get_google_api_key():
            issues.append("Google API key is not configured")
        
        if self.settings.VEO3_MODEL not in self.get_available_models():
            issues.append(f"Model '{self.settings.VEO3_MODEL}' is not in the list of available models")
        
        supported = self.get_supported_formats()
        
        if self.settings.VIDEO_QUALITY not in supported["qualities"]:
            issues.append(f"Video quality '{self.settings.VIDEO_QUALITY}' is not supported")
        
        if self.settings.VIDEO_ASPECT_RATIO not in supported["aspect_ratios"]:
            issues.append(f"Aspect ratio '{self.settings.VIDEO_ASPECT_RATIO}' is not supported")
        
        duration_limits = supported["durations"]
        if (self.settings.VIDEO_DURATION < duration_limits["min"] or 
            self.settings.VIDEO_DURATION > duration_limits["max"]):
            issues.append(f"Video duration should be between {duration_limits['min']} and {duration_limits['max']} seconds")
        
        # Check if output directory is writable
        try:
            test_file = self.settings.OUTPUT_DIR / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
        except Exception:
            issues.append(f"Output directory '{self.settings.OUTPUT_DIR}' is not writable")
        
        return issues
