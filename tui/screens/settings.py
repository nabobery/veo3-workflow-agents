from __future__ import annotations

from textual.screen import Screen
from textual.widgets import Static, Input, Button
from textual.app import ComposeResult

from ..utils.key_store import KeyStore


class SettingsScreen(Screen):
    def compose(self) -> ComposeResult:
        store = KeyStore.load()
        yield Static("Settings — API Keys")
        yield Static("Google API Key")
        yield Input(store.google_api_key_preview(), password=True, id="google")
        yield Static("Tavily API Key (optional)")
        yield Input(store.tavily_api_key_preview(), password=True, id="tavily")
        yield Button("Save", id="save")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            google_val = self.query_one("#google", Input).value or ""
            tavily_val = self.query_one("#tavily", Input).value or ""
            KeyStore.save_masked(google_val, tavily_val)
            self.app.push_screen("home")


