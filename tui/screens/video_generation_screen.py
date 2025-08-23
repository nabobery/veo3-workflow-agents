"""
Video generation screen using Veo3 models.

This screen provides interfaces for generating videos from prompts
using Google's Veo3 video generation models.
"""

from textual.widgets import Static, Button, Input, Select, TextArea, ProgressBar, DataTable
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual import on

class VideoGenerationScreen(ScrollableContainer):
    """Screen for video generation."""
    
    def compose(self):
        yield Static("Video Generation", classes="screen-title")
        yield Static("Create videos from prompts using Veo3 AI models", classes="screen-subtitle")
        
        # Generation controls
        with Container(classes="video-controls"):
            yield Static("Video Prompt", classes="section-title")
            yield TextArea(
                placeholder="Enter your video description...",
                id="input-video-prompt"
            )
            
            with Horizontal(classes="video-options"):
                with Vertical():
                    yield Static("Duration (seconds):")
                    yield Input(value="30", placeholder="1-300", id="input-duration")
                
                with Vertical():
                    yield Static("Quality:")
                    yield Select(
                        options=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("ultra", "Ultra"),
                        ],
                        value="high",
                        id="select-quality"
                    )
                
                with Vertical():
                    yield Static("Aspect Ratio:")
                    yield Select(
                        options=[
                            ("16:9", "16:9 (Landscape)"),
                            ("9:16", "9:16 (Portrait)"),
                            ("1:1", "1:1 (Square)"),
                        ],
                        value="16:9",
                        id="select-aspect-ratio"
                    )
                
                with Vertical():
                    yield Static("Style:")
                    yield Select(
                        options=[
                            ("cinematic", "Cinematic"),
                            ("photorealistic", "Photorealistic"),
                            ("animated", "Animated"),
                            ("artistic", "Artistic"),
                        ],
                        value="cinematic",
                        id="select-style"
                    )
            
            with Horizontal(classes="generation-actions"):
                yield Button("Generate Video", id="btn-generate-video", variant="primary")
                yield Button("Clear Form", id="btn-clear-form", variant="default")
        
        # Progress section
        with Container(classes="progress-section", id="progress-container"):
            yield Static("Generation Progress", classes="section-title")
            yield ProgressBar(id="generation-progress")
            yield Static("Ready", id="progress-status")
        
        # Results section
        yield Static("Generated Videos", classes="section-title")
        yield DataTable(id="videos-table")
    
    def on_mount(self):
        """Initialize the table."""
        table = self.query_one("#videos-table", DataTable)
        table.add_columns("Video ID", "Status", "Duration", "Quality", "Created", "Actions")
        
        # Hide progress section initially
        progress_container = self.query_one("#progress-container")
        progress_container.display = False
    
    @on(Button.Pressed, "#btn-generate-video")
    async def on_generate_video_pressed(self):
        """Handle generate video button press."""
        # This would integrate with the Video Generator
        pass
    
    @on(Button.Pressed, "#btn-clear-form")
    async def on_clear_form_pressed(self):
        """Handle clear form button press."""
        prompt_area = self.query_one("#input-video-prompt", TextArea)
        prompt_area.clear()
        
        # Reset form to defaults
        duration_input = self.query_one("#input-duration", Input)
        duration_input.value = "30"
        
        quality_select = self.query_one("#select-quality", Select)
        quality_select.value = "high"
        
        aspect_select = self.query_one("#select-aspect-ratio", Select)
        aspect_select.value = "16:9"
        
        style_select = self.query_one("#select-style", Select)
        style_select.value = "cinematic"
    
    async def refresh(self):
        """Refresh the screen."""
        pass
