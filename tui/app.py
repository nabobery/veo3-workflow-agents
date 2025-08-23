from __future__ import annotations

from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static
from textual.screen import Screen

from .screens.home import HomeScreen
from .screens.settings import SettingsScreen
from .screens.prompt_generation import PromptGenerationScreen
from .screens.enhancement import EnhancementScreen
from .screens.video import VideoGenerationScreen
from .config import ensure_environment_from_store


class RootApp(App):
    CSS_PATH = None
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "push_screen('home')", "Home"),
        Binding("f2", "push_screen('settings')", "Settings"),
        Binding("f3", "push_screen('generate')", "Generate"),
        Binding("f4", "push_screen('enhance')", "Enhance"),
        Binding("f5", "push_screen('video')", "Video"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Veo3 Workflow TUI — F1 Home • F2 Settings • F3 Generate • F4 Enhance • F5 Video", id="banner")
        yield Footer()

    def on_mount(self) -> None:
        # Register screens
        self.install_screen(HomeScreen(id="home"), name="home")
        self.install_screen(SettingsScreen(id="settings"), name="settings")
        self.install_screen(PromptGenerationScreen(id="generate"), name="generate")
        self.install_screen(EnhancementScreen(id="enhance"), name="enhance")
        self.install_screen(VideoGenerationScreen(id="video"), name="video")
        self.push_screen("home")


def main(argv: Optional[list[str]] = None) -> int:
    # Ensure environment variables are populated from saved key store if needed
    ensure_environment_from_store()
    app = RootApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


