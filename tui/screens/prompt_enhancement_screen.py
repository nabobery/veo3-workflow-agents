"""
Prompt enhancement screen using LangGraph workflows.

This screen provides interfaces for enhancing video prompts using
LangGraph's sophisticated prompt enhancement workflow.
"""

from textual.widgets import Static, Button, TextArea, TabbedContent, TabPane
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual import on

class PromptEnhancementScreen(ScrollableContainer):
    """Screen for enhancing video prompts."""
    
    def compose(self):
        yield Static("Prompt Enhancement", classes="screen-title")
        yield Static("Enhance your prompts using advanced AI workflows", classes="screen-subtitle")
        
        # Input section
        with Container(classes="enhancement-input"):
            yield Static("Original Prompt", classes="section-title")
            yield TextArea(
                placeholder="Enter your video prompt to enhance...",
                id="input-prompt"
            )
            
            with Horizontal(classes="enhancement-controls"):
                yield Button("Enhance Prompt", id="btn-enhance", variant="primary")
                yield Button("Clear", id="btn-clear", variant="default")
        
        # Results section
        yield Static("Enhanced Results", classes="section-title")
        
        with TabbedContent(id="results-tabs"):
            with TabPane("JSON Format", id="json-tab"):
                yield TextArea(id="json-output", read_only=True)
            
            with TabPane("XML Format", id="xml-tab"):
                yield TextArea(id="xml-output", read_only=True)
            
            with TabPane("Natural Language", id="natural-tab"):
                yield TextArea(id="natural-output", read_only=True)
            
            with TabPane("Enhancement Notes", id="notes-tab"):
                yield TextArea(id="notes-output", read_only=True)
    
    @on(Button.Pressed, "#btn-enhance")
    async def on_enhance_pressed(self):
        """Handle enhance button press."""
        # This would integrate with the LangGraph manager
        pass
    
    @on(Button.Pressed, "#btn-clear")
    async def on_clear_pressed(self):
        """Handle clear button press."""
        input_area = self.query_one("#input-prompt", TextArea)
        input_area.clear()
        
        # Clear all output areas
        for output_id in ["json-output", "xml-output", "natural-output", "notes-output"]:
            output_area = self.query_one(f"#{output_id}", TextArea)
            output_area.clear()
    
    async def refresh(self):
        """Refresh the screen."""
        pass
