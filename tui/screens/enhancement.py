from __future__ import annotations

from textual.screen import Screen
from textual.widgets import Static, Input, Button, Log
from textual.app import ComposeResult

from ..agents.langraph_bridge import enhance_prompt
from ..utils.error_handler import classify_exception, format_error_summary


class EnhancementScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Prompt Enhancement")
        yield Input(placeholder="Enter a base prompt to enhance", id="prompt")
        yield Button("Enhance", id="run")
        yield Log(highlight=True, id="log")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "run":
            return
        prompt = self.query_one("#prompt", Input).value or ""
        log = self.query_one("#log", Log)
        log.clear()
        try:
            result = enhance_prompt(prompt)
            saved = result.get("saved_dir") or ""
            if saved:
                log.write_line(f"Saved enhanced outputs to: {saved}")
            else:
                log.write_line("Enhancement completed; no save directory reported.")
        except Exception as e:
            info = classify_exception(e)
            log.write_line(format_error_summary(info, e))


