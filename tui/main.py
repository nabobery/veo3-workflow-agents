"""
Main TUI application for Veo3 Workflow Agents.

This module implements the main Textual application with a tabbed interface
for prompt generation, enhancement, and video creation.
"""

import asyncio
import logging
from typing import Any, Optional
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Static
from textual.containers import Container
from textual.binding import Binding
from textual.reactive import var
from textual import on

from .config import get_settings, APIKeyManager
from .screens import (
    MainScreen,
    SettingsScreen,
    PromptGenerationScreen,
    PromptEnhancementScreen,
    VideoGenerationScreen,
)
from .agents import PydanticAIManager, LangGraphManager, VideoGenerator
from .utils.errors import TUIError, ConfigurationError, APIKeyError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Veo3WorkflowApp(App[None]):
    """
    Main TUI application for Veo3 Workflow Agents.
    
    This application provides a comprehensive interface for:
    - Prompt generation using Pydantic AI agents
    - Prompt enhancement using LangGraph workflows
    - Video generation using Veo3 models
    - Configuration and API key management
    """
    
    TITLE = "Veo3 Workflow Agents"
    SUB_TITLE = "AI-Powered Video Content Creation"
    
    CSS_PATH = "styles/main.tcss"
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("F1", "help", "Help"),
        Binding("F10", "settings", "Settings"),
        Binding("ctrl+r", "refresh", "Refresh"),
    ]
    
    # Reactive variables
    current_tab = var("main")
    status_message = var("Ready")
    api_status = var("Unknown")
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Initialize components
        self.settings = get_settings()
        self.api_key_manager = APIKeyManager()
        
        # Initialize managers (will be created lazily)
        self._pydantic_manager = None
        self._langraph_manager = None
        self._video_generator = None
        
        # Application state
        self.initialization_complete = False
    
    def compose(self) -> ComposeResult:
        """Compose the main UI layout."""
        yield Header(show_clock=True)
        
        with TabbedContent(initial="main"):
            with TabPane("Dashboard", id="main"):
                yield MainScreen(id="main-screen")
            
            with TabPane("Generate", id="generate"):
                yield PromptGenerationScreen(id="generation-screen")
            
            with TabPane("Enhance", id="enhance"):
                yield PromptEnhancementScreen(id="enhancement-screen")
            
            with TabPane("Create Video", id="video"):
                yield VideoGenerationScreen(id="video-screen")
            
            with TabPane("Settings", id="settings"):
                yield SettingsScreen(id="settings-screen")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.title = self.TITLE
        self.sub_title = self.SUB_TITLE
        
        # Start initialization
        asyncio.create_task(self._initialize_async())
    
    async def _initialize_async(self) -> None:
        """Initialize the application asynchronously."""
        try:
            self.status_message = "Initializing..."
            
            # Check API keys
            await self._check_api_status()
            
            # Initialize managers
            await self._initialize_managers()
            
            self.status_message = "Ready"
            self.initialization_complete = True
            
            logger.info("Application initialization complete")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            self.status_message = f"Initialization failed: {str(e)}"
            
            # Show settings screen if API keys are missing
            if isinstance(e, (APIKeyError, ConfigurationError)):
                await self.action_settings()
    
    async def _check_api_status(self) -> None:
        """Check the status of API keys and services."""
        try:
            # Check required API keys
            missing_keys = self.settings.get_missing_keys()
            
            if missing_keys:
                self.api_status = f"Missing: {', '.join(missing_keys)}"
                return
            
            # If all keys are present, check if services are accessible
            self.api_status = "Checking services..."
            
            # This would be replaced with actual service checks
            # For now, just check if keys are present
            self.api_status = "Ready"
            
        except Exception as e:
            logger.error(f"API status check failed: {e}")
            self.api_status = f"Error: {str(e)}"
    
    async def _initialize_managers(self) -> None:
        """Initialize the AI managers."""
        try:
            # Initialize Pydantic AI manager
            self._pydantic_manager = PydanticAIManager()
            
            # Initialize LangGraph manager
            self._langraph_manager = LangGraphManager()
            
            # Initialize Video Generator
            self._video_generator = VideoGenerator()
            
            logger.info("All managers initialized successfully")
            
        except Exception as e:
            logger.error(f"Manager initialization failed: {e}")
            # Continue with limited functionality
    
    @property
    def pydantic_manager(self) -> Optional[PydanticAIManager]:
        """Get the Pydantic AI manager."""
        return self._pydantic_manager
    
    @property
    def langraph_manager(self) -> Optional[LangGraphManager]:
        """Get the LangGraph manager."""
        return self._langraph_manager
    
    @property
    def video_generator(self) -> Optional[VideoGenerator]:
        """Get the Video Generator."""
        return self._video_generator
    
    @on(TabbedContent.TabActivated)
    def on_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab activation."""
        self.current_tab = event.tab.id
        logger.debug(f"Activated tab: {event.tab.id}")
        
        # Update screen-specific state if needed
        screen = self.query_one(f"#{event.tab.id}-screen", expect_type=Container)
        if hasattr(screen, 'on_tab_activated'):
            asyncio.create_task(screen.on_tab_activated())
    
    def action_quit(self) -> None:
        """Quit the application."""
        logger.info("Application quit requested")
        self.exit()
    
    async def action_settings(self) -> None:
        """Show the settings screen."""
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = "settings"
    
    async def action_refresh(self) -> None:
        """Refresh the application state."""
        self.status_message = "Refreshing..."
        
        try:
            # Reload settings
            from .config.settings import reload_settings
            self.settings = reload_settings()
            
            # Re-check API status
            await self._check_api_status()
            
            # Re-initialize managers if needed
            if self.settings.has_required_keys():
                await self._initialize_managers()
            
            self.status_message = "Refreshed"
            
            # Notify all screens to refresh
            screens = [
                self.query_one("#main-screen"),
                self.query_one("#generation-screen"),
                self.query_one("#enhancement-screen"),
                self.query_one("#video-screen"),
                self.query_one("#settings-screen"),
            ]
            
            for screen in screens:
                if hasattr(screen, 'refresh'):
                    asyncio.create_task(screen.refresh())
            
        except Exception as e:
            logger.error(f"Refresh failed: {e}")
            self.status_message = f"Refresh failed: {str(e)}"
    
    async def action_help(self) -> None:
        """Show help information."""
        help_text = """
# Veo3 Workflow Agents Help

## Overview
This application helps you create video content using AI-powered tools:

## Tabs:
- **Dashboard**: Overview and status
- **Generate**: Create prompt ideas using Pydantic AI
- **Enhance**: Improve prompts using LangGraph workflows  
- **Create Video**: Generate videos using Veo3 models
- **Settings**: Configure API keys and preferences

## Key Bindings:
- `q` or `Ctrl+C`: Quit application
- `F1`: Show this help
- `F10`: Go to settings
- `Ctrl+R`: Refresh application state

## Getting Started:
1. Go to Settings (F10) to configure your API keys
2. Use Generate tab to create prompt ideas
3. Use Enhance tab to improve prompts
4. Use Create Video tab to generate videos

## Support:
Check the logs for detailed error information.
"""
        
        # Create a modal with help text
        from textual.widgets import Markdown
        from textual.screen import ModalScreen
        
        class HelpModal(ModalScreen[None]):
            def compose(self) -> ComposeResult:
                with Container(id="help-modal"):
                    yield Markdown(help_text)
        
        await self.push_screen(HelpModal())
    
    def watch_status_message(self, status: str) -> None:
        """React to status message changes."""
        logger.debug(f"Status updated: {status}")
        
        # Update footer if it exists
        try:
            footer = self.query_one(Footer)
            # This would update a custom status bar if implemented
        except Exception:
            pass
    
    def watch_api_status(self, status: str) -> None:
        """React to API status changes."""
        logger.debug(f"API status updated: {status}")
    
    async def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle errors and show appropriate feedback to the user.
        
        Args:
            error: The error that occurred
            context: Additional context about where the error occurred
        """
        logger.error(f"Error in {context}: {error}", exc_info=True)
        
        if isinstance(error, APIKeyError):
            self.status_message = f"API key error: {error.service}"
            # Optionally show settings screen
            if error.service == "google":
                await self.action_settings()
        
        elif isinstance(error, ConfigurationError):
            self.status_message = f"Configuration error: {str(error)}"
            await self.action_settings()
        
        else:
            self.status_message = f"Error: {str(error)}"
        
        # Show error in a modal for critical errors
        if isinstance(error, (APIKeyError, ConfigurationError)):
            await self._show_error_modal(error, context)
    
    async def _show_error_modal(self, error: Exception, context: str) -> None:
        """Show an error modal dialog."""
        from textual.widgets import Static
        from textual.screen import ModalScreen
        from textual.containers import Vertical
        
        class ErrorModal(ModalScreen[None]):
            def compose(self) -> ComposeResult:
                with Vertical(id="error-modal"):
                    yield Static(f"Error in {context}")
                    yield Static(str(error))
                    yield Static("Press Escape to close")
        
        await self.push_screen(ErrorModal())


def main() -> None:
    """Main entry point for the TUI application."""
    try:
        app = Veo3WorkflowApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        print(f"Failed to start application: {e}")


if __name__ == "__main__":
    main()
