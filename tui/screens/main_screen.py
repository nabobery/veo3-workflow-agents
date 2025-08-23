"""
Main dashboard screen for the Veo3 Workflow Agents TUI.

This screen provides an overview of the application status, recent activities,
and quick access to main features.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List

from textual.widgets import Static, Button, DataTable, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import var
from textual import on

from ..utils.helpers import format_duration, relative_time
from ..utils.errors import TUIError


class StatusCard(Container):
    """A card widget showing status information."""
    
    def __init__(self, title: str, status: str, details: str = "", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.status = status
        self.details = details
    
    def compose(self):
        yield Static(self.title, classes="card-title")
        yield Static(self.status, classes="card-status")
        if self.details:
            yield Static(self.details, classes="card-details")


class QuickActions(Container):
    """Quick action buttons for common tasks."""
    
    def compose(self):
        yield Static("Quick Actions", classes="section-title")
        with Horizontal(classes="quick-actions"):
            yield Button("Generate Ideas", id="btn-generate", variant="primary")
            yield Button("Enhance Prompt", id="btn-enhance", variant="default") 
            yield Button("Create Video", id="btn-video", variant="success")
            yield Button("Settings", id="btn-settings", variant="default")


class RecentActivity(Container):
    """Display recent activity and logs."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.activity_log = []
    
    def compose(self):
        yield Static("Recent Activity", classes="section-title")
        yield RichLog(id="activity-log", max_lines=10)
    
    def add_activity(self, message: str, level: str = "info"):
        """Add an activity message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log = self.query_one("#activity-log", RichLog)
        
        if level == "error":
            log.write(f"[red]{timestamp}[/red] [bold red]ERROR:[/bold red] {message}")
        elif level == "warning":
            log.write(f"[yellow]{timestamp}[/yellow] [bold yellow]WARNING:[/bold yellow] {message}")
        elif level == "success":
            log.write(f"[green]{timestamp}[/green] [bold green]SUCCESS:[/bold green] {message}")
        else:
            log.write(f"[blue]{timestamp}[/blue] {message}")


class SystemOverview(Container):
    """System status overview with cards."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pydantic_status = "Unknown"
        self.langraph_status = "Unknown"
        self.video_status = "Unknown"
        self.api_status = "Unknown"
    
    def compose(self):
        yield Static("System Status", classes="section-title")
        with Horizontal(classes="status-cards"):
            yield StatusCard(
                "Pydantic AI",
                self.pydantic_status,
                "Prompt generation",
                id="pydantic-card"
            )
            yield StatusCard(
                "LangGraph",
                self.langraph_status,
                "Prompt enhancement", 
                id="langraph-card"
            )
            yield StatusCard(
                "Video Generation",
                self.video_status,
                "Veo3 integration",
                id="video-card"
            )
            yield StatusCard(
                "API Status",
                self.api_status,
                "Service connectivity",
                id="api-card"
            )
    
    def update_status(self, service: str, status: str, details: str = ""):
        """Update the status of a specific service."""
        card_id = f"{service}-card"
        try:
            card = self.query_one(f"#{card_id}", StatusCard)
            card.status = status
            card.details = details
            
            # Update the status display
            status_widget = card.query_one(".card-status", Static)
            status_widget.update(status)
            
            if details:
                details_widget = card.query_one(".card-details", Static)
                details_widget.update(details)
                
        except Exception:
            pass  # Card not found or not ready yet


class MainScreen(Container):
    """Main dashboard screen showing system overview and quick actions."""
    
    # Reactive variables
    last_updated = var(datetime.now())
    total_generations = var(0)
    total_enhancements = var(0) 
    total_videos = var(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = None
    
    def compose(self):
        with Vertical():
            # Welcome section
            yield Static("Welcome to Veo3 Workflow Agents", classes="welcome-title")
            yield Static(
                "Create amazing video content with AI-powered prompt generation, enhancement, and video creation.",
                classes="welcome-subtitle"
            )
            
            # System overview
            yield SystemOverview(id="system-overview")
            
            # Quick actions
            yield QuickActions(id="quick-actions")
            
            # Statistics
            yield self._create_stats_section()
            
            # Recent activity
            yield RecentActivity(id="recent-activity")
    
    def _create_stats_section(self) -> Container:
        """Create the statistics section."""
        stats = Container(id="stats-section")
        
        with stats:
            Static("Usage Statistics", classes="section-title")
            
            with Horizontal(classes="stats-row"):
                with Vertical(classes="stat-card"):
                    Static("0", id="stat-generations", classes="stat-number")
                    Static("Ideas Generated", classes="stat-label")
                
                with Vertical(classes="stat-card"):
                    Static("0", id="stat-enhancements", classes="stat-number")
                    Static("Prompts Enhanced", classes="stat-label")
                
                with Vertical(classes="stat-card"):
                    Static("0", id="stat-videos", classes="stat-number")
                    Static("Videos Created", classes="stat-label")
                
                with Vertical(classes="stat-card"):
                    Static("Never", id="stat-last-updated", classes="stat-number")
                    Static("Last Activity", classes="stat-label")
        
        return stats
    
    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Get reference to the main app
        self.app_ref = self.app
        
        # Start periodic updates
        self.set_interval(5.0, self._update_status)
        
        # Initial status update
        asyncio.create_task(self._initial_update())
    
    async def _initial_update(self) -> None:
        """Perform initial status update."""
        await self._update_status()
        
        # Add welcome message to activity log
        activity = self.query_one("#recent-activity", RecentActivity)
        activity.add_activity("Application started", "success")
    
    async def _update_status(self) -> None:
        """Update the system status periodically."""
        try:
            overview = self.query_one("#system-overview", SystemOverview)
            
            # Update Pydantic AI status
            if hasattr(self.app_ref, 'pydantic_manager') and self.app_ref.pydantic_manager:
                try:
                    status = self.app_ref.pydantic_manager.get_status()
                    if status["ready"]:
                        overview.update_status("pydantic", "Ready", "All systems operational")
                    else:
                        overview.update_status("pydantic", "Not Ready", "Check API keys")
                except Exception as e:
                    overview.update_status("pydantic", "Error", str(e))
            else:
                overview.update_status("pydantic", "Not Available", "Manager not initialized")
            
            # Update LangGraph status
            if hasattr(self.app_ref, 'langraph_manager') and self.app_ref.langraph_manager:
                try:
                    status = self.app_ref.langraph_manager.get_status()
                    if status["ready"]:
                        overview.update_status("langraph", "Ready", "Workflow available")
                    else:
                        overview.update_status("langraph", "Not Ready", "Check configuration")
                except Exception as e:
                    overview.update_status("langraph", "Error", str(e))
            else:
                overview.update_status("langraph", "Not Available", "Manager not initialized")
            
            # Update Video Generation status
            if hasattr(self.app_ref, 'video_generator') and self.app_ref.video_generator:
                try:
                    status = self.app_ref.video_generator.get_status()
                    if status["ready"]:
                        overview.update_status("video", "Ready", "Veo3 available")
                    else:
                        overview.update_status("video", "Not Ready", "Check API keys")
                except Exception as e:
                    overview.update_status("video", "Error", str(e))
            else:
                overview.update_status("video", "Not Available", "Generator not initialized")
            
            # Update API status
            if hasattr(self.app_ref, 'api_status'):
                overview.update_status("api", self.app_ref.api_status, "Service connectivity")
            
            # Update last updated time
            self.last_updated = datetime.now()
            last_updated_widget = self.query_one("#stat-last-updated", Static)
            last_updated_widget.update(relative_time(self.last_updated))
            
        except Exception as e:
            # Log error but don't crash
            if hasattr(self, 'query_one'):
                try:
                    activity = self.query_one("#recent-activity", RecentActivity)
                    activity.add_activity(f"Status update failed: {str(e)}", "error")
                except:
                    pass
    
    @on(Button.Pressed, "#btn-generate")
    async def on_generate_pressed(self) -> None:
        """Handle generate button press."""
        if hasattr(self.app_ref, 'query_one'):
            try:
                from textual.widgets import TabbedContent
                tabbed = self.app_ref.query_one(TabbedContent)
                tabbed.active = "generate"
                
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity("Switched to Generate tab", "info")
            except Exception as e:
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity(f"Navigation failed: {str(e)}", "error")
    
    @on(Button.Pressed, "#btn-enhance")
    async def on_enhance_pressed(self) -> None:
        """Handle enhance button press."""
        if hasattr(self.app_ref, 'query_one'):
            try:
                from textual.widgets import TabbedContent
                tabbed = self.app_ref.query_one(TabbedContent)
                tabbed.active = "enhance"
                
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity("Switched to Enhance tab", "info")
            except Exception as e:
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity(f"Navigation failed: {str(e)}", "error")
    
    @on(Button.Pressed, "#btn-video")
    async def on_video_pressed(self) -> None:
        """Handle video button press."""
        if hasattr(self.app_ref, 'query_one'):
            try:
                from textual.widgets import TabbedContent
                tabbed = self.app_ref.query_one(TabbedContent)
                tabbed.active = "video"
                
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity("Switched to Video tab", "info")
            except Exception as e:
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity(f"Navigation failed: {str(e)}", "error")
    
    @on(Button.Pressed, "#btn-settings")
    async def on_settings_pressed(self) -> None:
        """Handle settings button press."""
        if hasattr(self.app_ref, 'query_one'):
            try:
                from textual.widgets import TabbedContent
                tabbed = self.app_ref.query_one(TabbedContent)
                tabbed.active = "settings"
                
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity("Switched to Settings tab", "info")
            except Exception as e:
                activity = self.query_one("#recent-activity", RecentActivity)
                activity.add_activity(f"Navigation failed: {str(e)}", "error")
    
    async def on_tab_activated(self) -> None:
        """Called when this tab is activated."""
        # Refresh status when tab becomes active
        await self._update_status()
        
        activity = self.query_one("#recent-activity", RecentActivity)
        activity.add_activity("Dashboard refreshed", "info")
    
    async def refresh(self) -> None:
        """Refresh the screen data."""
        await self._update_status()
        
        activity = self.query_one("#recent-activity", RecentActivity)
        activity.add_activity("Manual refresh completed", "info")
    
    def update_stats(self, generations: int = None, enhancements: int = None, videos: int = None):
        """Update the usage statistics."""
        try:
            if generations is not None:
                self.total_generations = generations
                stat_widget = self.query_one("#stat-generations", Static)
                stat_widget.update(str(generations))
            
            if enhancements is not None:
                self.total_enhancements = enhancements
                stat_widget = self.query_one("#stat-enhancements", Static)
                stat_widget.update(str(enhancements))
            
            if videos is not None:
                self.total_videos = videos
                stat_widget = self.query_one("#stat-videos", Static)
                stat_widget.update(str(videos))
            
            # Update last activity time
            self.last_updated = datetime.now()
            last_updated_widget = self.query_one("#stat-last-updated", Static)
            last_updated_widget.update(relative_time(self.last_updated))
            
        except Exception:
            pass  # Widgets might not be ready yet
    
    def add_activity(self, message: str, level: str = "info"):
        """Add an activity message to the log."""
        try:
            activity = self.query_one("#recent-activity", RecentActivity)
            activity.add_activity(message, level)
        except Exception:
            pass  # Widget might not be ready yet
