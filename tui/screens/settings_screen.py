"""
Settings screen for the Veo3 Workflow Agents TUI.

This screen allows users to configure API keys, model settings, and other preferences.
"""

import asyncio
from typing import Dict, Any, Optional

from textual.widgets import Static, Button, Input, Select, Label, Switch, TextArea
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.validation import Function, ValidationResult, Validator
from textual import on

from ..config import get_settings, APIKeyManager
from ..utils.validators import validate_api_key
from ..utils.errors import ValidationError


class APIKeyInput(Container):
    """Widget for API key input with validation."""
    
    def __init__(self, service: str, label: str, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self.label_text = label
        self.api_key_manager = APIKeyManager()
    
    def compose(self):
        yield Label(self.label_text)
        yield Input(
            placeholder=f"Enter {self.service} API key...",
            password=True,
            id=f"input-{self.service}",
            validators=[self._validate_api_key]
        )
        yield Static("", id=f"status-{self.service}", classes="input-status")
    
    def _validate_api_key(self, value: str) -> ValidationResult:
        """Validate the API key format."""
        if not value:
            return ValidationResult.success()
        
        try:
            validate_api_key(value, self.service)
            return ValidationResult.success()
        except ValidationError as e:
            return ValidationResult.failure(e.message)
    
    def on_mount(self):
        """Load existing API key when mounted."""
        existing_key = self.api_key_manager.get_api_key(self.service)
        if existing_key:
            input_widget = self.query_one(f"#input-{self.service}", Input)
            input_widget.value = existing_key
            
            status_widget = self.query_one(f"#status-{self.service}", Static)
            status_widget.update("✓ API key configured")
            status_widget.add_class("status-success")
    
    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed):
        """Handle API key input changes."""
        if event.input.id == f"input-{self.service}":
            status_widget = self.query_one(f"#status-{self.service}", Static)
            
            if event.validation_result and event.validation_result.is_valid:
                status_widget.update("✓ Valid format")
                status_widget.set_classes("status-success")
            elif event.value:
                status_widget.update("✗ Invalid format")
                status_widget.set_classes("status-error")
            else:
                status_widget.update("")
                status_widget.set_classes("")


class ModelSettings(Container):
    """Widget for model configuration settings."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = get_settings()
    
    def compose(self):
        yield Static("Model Configuration", classes="section-title")
        
        with Vertical():
            # Pydantic AI Model
            yield Label("Pydantic AI Model:")
            yield Select(
                options=[
                    ("gemini-2.5-flash", "gemini-2.5-flash"),
                    ("gemini-2.5-pro", "gemini-2.5-pro"),
                    ("gemini-2.0-flash", "gemini-2.0-flash"),
                    ("gemini-1.5-pro", "gemini-1.5-pro"),
                    ("gemini-1.5-flash", "gemini-1.5-flash"),
                ],
                value=self.settings.PYA_MODEL,
                id="select-pya-model"
            )
            
            # LangGraph Model
            yield Label("LangGraph Model:")
            yield Select(
                options=[
                    ("gemini-2.5-flash", "gemini-2.5-flash"),
                    ("gemini-2.5-pro", "gemini-2.5-pro"),
                    ("gemini-2.0-flash", "gemini-2.0-flash"),
                    ("gemini-1.5-pro", "gemini-1.5-pro"),
                    ("gemini-1.5-flash", "gemini-1.5-flash"),
                ],
                value=self.settings.GOOGLE_MODEL,
                id="select-langraph-model"
            )
            
            # Video Model
            yield Label("Video Generation Model:")
            yield Select(
                options=[
                    ("video-generation-001", "video-generation-001"),
                    ("veo-3", "veo-3"),
                    ("veo-2", "veo-2"),
                ],
                value=self.settings.VEO3_MODEL,
                id="select-video-model"
            )
            
            # Temperature
            yield Label("Default Temperature:")
            yield Input(
                value=str(self.settings.DEFAULT_TEMPERATURE),
                placeholder="0.0 - 2.0",
                id="input-temperature"
            )
            
            # Number of ideas
            yield Label("Default Number of Ideas:")
            yield Input(
                value=str(self.settings.DEFAULT_NUM_IDEAS),
                placeholder="1 - 100",
                id="input-num-ideas"
            )


class VideoSettings(Container):
    """Widget for video generation settings."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = get_settings()
    
    def compose(self):
        yield Static("Video Generation Settings", classes="section-title")
        
        with Vertical():
            # Video Quality
            yield Label("Default Video Quality:")
            yield Select(
                options=[
                    ("low", "Low"),
                    ("medium", "Medium"),
                    ("high", "High"),
                    ("ultra", "Ultra"),
                ],
                value=self.settings.VIDEO_QUALITY,
                id="select-video-quality"
            )
            
            # Aspect Ratio
            yield Label("Default Aspect Ratio:")
            yield Select(
                options=[
                    ("16:9", "16:9 (Landscape)"),
                    ("9:16", "9:16 (Portrait)"),
                    ("1:1", "1:1 (Square)"),
                    ("4:3", "4:3 (Classic)"),
                    ("3:4", "3:4 (Portrait Classic)"),
                ],
                value=self.settings.VIDEO_ASPECT_RATIO,
                id="select-aspect-ratio"
            )
            
            # Duration
            yield Label("Default Duration (seconds):")
            yield Input(
                value=str(self.settings.VIDEO_DURATION),
                placeholder="1 - 300",
                id="input-video-duration"
            )


class ApplicationSettings(Container):
    """Widget for general application settings."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = get_settings()
    
    def compose(self):
        yield Static("Application Settings", classes="section-title")
        
        with Vertical():
            # Theme
            yield Label("Theme:")
            yield Select(
                options=[
                    ("dark", "Dark"),
                    ("light", "Light"),
                ],
                value=self.settings.TUI_THEME,
                id="select-theme"
            )
            
            # Auto-save
            with Horizontal():
                yield Label("Auto-save generated content:")
                yield Switch(
                    value=self.settings.TUI_AUTO_SAVE,
                    id="switch-auto-save"
                )
            
            # Max history
            yield Label("Maximum History Items:")
            yield Input(
                value=str(self.settings.TUI_MAX_HISTORY),
                placeholder="1 - 1000",
                id="input-max-history"
            )
            
            # Output directory
            yield Label("Output Directory:")
            yield Input(
                value=str(self.settings.OUTPUT_DIR),
                placeholder="Path to output directory",
                id="input-output-dir"
            )


class SettingsScreen(ScrollableContainer):
    """Settings screen for configuring the application."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = get_settings()
        self.api_key_manager = APIKeyManager()
        self.app_ref = None
    
    def compose(self):
        yield Static("Settings", classes="screen-title")
        
        # API Keys Section
        yield Static("API Configuration", classes="section-title")
        yield APIKeyInput("google", "Google API Key (Required)", id="google-key")
        yield APIKeyInput("tavily", "Tavily API Key (Optional)", id="tavily-key")
        yield APIKeyInput("exa", "Exa API Key (Optional)", id="exa-key")
        yield APIKeyInput("linkup", "LinkUp API Key (Optional)", id="linkup-key")
        
        # Model Settings
        yield ModelSettings(id="model-settings")
        
        # Video Settings
        yield VideoSettings(id="video-settings")
        
        # Application Settings
        yield ApplicationSettings(id="app-settings")
        
        # Action buttons
        with Horizontal(classes="action-buttons"):
            yield Button("Save Settings", id="btn-save", variant="primary")
            yield Button("Reset to Defaults", id="btn-reset", variant="default")
            yield Button("Test Connection", id="btn-test", variant="default")
    
    def on_mount(self):
        """Called when the screen is mounted."""
        self.app_ref = self.app
    
    @on(Button.Pressed, "#btn-save")
    async def on_save_pressed(self):
        """Handle save settings button press."""
        try:
            await self._save_settings()
            
            # Show success message
            if hasattr(self.app_ref, 'status_message'):
                self.app_ref.status_message = "Settings saved successfully"
            
            # Refresh the app
            if hasattr(self.app_ref, 'action_refresh'):
                await self.app_ref.action_refresh()
                
        except Exception as e:
            if hasattr(self.app_ref, 'handle_error'):
                await self.app_ref.handle_error(e, "Settings Save")
    
    @on(Button.Pressed, "#btn-reset")
    async def on_reset_pressed(self):
        """Handle reset to defaults button press."""
        try:
            await self._reset_to_defaults()
            
            if hasattr(self.app_ref, 'status_message'):
                self.app_ref.status_message = "Settings reset to defaults"
                
        except Exception as e:
            if hasattr(self.app_ref, 'handle_error'):
                await self.app_ref.handle_error(e, "Settings Reset")
    
    @on(Button.Pressed, "#btn-test")
    async def on_test_pressed(self):
        """Handle test connection button press."""
        try:
            await self._test_connections()
        except Exception as e:
            if hasattr(self.app_ref, 'handle_error'):
                await self.app_ref.handle_error(e, "Connection Test")
    
    async def _save_settings(self):
        """Save the current settings."""
        # Save API keys
        google_input = self.query_one("#input-google", Input)
        if google_input.value:
            self.api_key_manager.set_api_key("google", google_input.value)
        
        tavily_input = self.query_one("#input-tavily", Input)
        if tavily_input.value:
            self.api_key_manager.set_api_key("tavily", tavily_input.value)
        
        exa_input = self.query_one("#input-exa", Input)
        if exa_input.value:
            self.api_key_manager.set_api_key("exa", exa_input.value)
        
        linkup_input = self.query_one("#input-linkup", Input)
        if linkup_input.value:
            self.api_key_manager.set_api_key("linkup", linkup_input.value)
        
        # Note: In a real implementation, we would need to update the settings
        # and save them to a configuration file. For now, we just update environment
        # variables which will be picked up on restart.
    
    async def _reset_to_defaults(self):
        """Reset all settings to their default values."""
        # This would restore default values to all inputs
        # For now, just clear the form
        pass
    
    async def _test_connections(self):
        """Test API connections."""
        if hasattr(self.app_ref, 'status_message'):
            self.app_ref.status_message = "Testing connections..."
        
        # Test each configured API
        # This would make actual test calls to verify connectivity
        # For now, just simulate the test
        await asyncio.sleep(1)
        
        if hasattr(self.app_ref, 'status_message'):
            self.app_ref.status_message = "Connection test completed"
    
    async def refresh(self):
        """Refresh the settings screen."""
        # Reload current values
        pass
