from textual.screen import Screen
from textual.widgets import Static, Button
from textual.app import ComposeResult


class HomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Welcome to Veo3 Workflow TUI", id="title")
        yield Static("Use the function keys or buttons below to navigate.")
        yield Button("Settings", id="go-settings")
        yield Button("Generate Prompts", id="go-generate")
        yield Button("Enhance Prompt", id="go-enhance")
        yield Button("Generate Video", id="go-video")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping = {
            "go-settings": "settings",
            "go-generate": "generate",
            "go-enhance": "enhance",
            "go-video": "video",
        }
        dest = mapping.get(event.button.id or "")
        if dest:
            self.app.push_screen(dest)


