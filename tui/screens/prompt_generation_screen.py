"""
Prompt generation screen using Pydantic AI agents.

This screen provides interfaces for generating video prompt ideas using
various Pydantic AI agents and search capabilities.
"""

from textual.widgets import Static, Button, Input, Select, TextArea, DataTable
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual import on

class PromptGenerationScreen(ScrollableContainer):
    """Screen for generating video prompt ideas."""
    
    def compose(self):
        yield Static("Prompt Generation", classes="screen-title")
        yield Static("Generate creative video prompt ideas using AI-powered agents", classes="screen-subtitle")
        
        # Generation controls
        with Container(classes="generation-controls"):
            yield Static("Generation Type", classes="section-title")
            yield Select(
                options=[
                    ("simple", "Simple Search"),
                    ("viral", "Viral Topics"),
                    ("variations", "Topic Variations"),
                ],
                value="simple",
                id="select-generation-type"
            )
            
            yield Static("Topic/Query", classes="input-label")
            yield TextArea(
                placeholder="Enter your topic, theme, or search query...",
                id="input-topic"
            )
            
            with Horizontal(classes="generation-options"):
                yield Static("Number of Ideas:")
                yield Input(value="10", placeholder="1-100", id="input-num-ideas")
                yield Button("Generate Ideas", id="btn-generate", variant="primary")
        
        # Results area
        yield Static("Generated Ideas", classes="section-title")
        yield DataTable(id="results-table")
    
    def on_mount(self):
        """Initialize the table."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Title", "Description", "Sources", "Trend Score")
    
    @on(Button.Pressed, "#btn-generate")
    async def on_generate_pressed(self):
        """Handle generate button press."""
        # This would integrate with the Pydantic AI manager
        pass
    
    async def refresh(self):
        """Refresh the screen."""
        pass
