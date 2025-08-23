from __future__ import annotations

from textual.screen import Screen
from textual.widgets import Static, Input, Button, RadioSet, RadioButton, Log
from textual.app import ComposeResult

from ..agents.pydantic_bridge import generate_ideas
from ..utils.error_handler import classify_exception, format_error_summary


class PromptGenerationScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Prompt Generation")
        yield RadioSet(
            RadioButton("simple", value=True, id="mode-simple"),
            RadioButton("viral", id="mode-viral"),
            RadioButton("variations", id="mode-variations"),
            id="modes",
        )
        yield Static("Topic / Seed")
        yield Input(placeholder="e.g., Latest trends in technology", id="topic")
        yield Static("Count (optional)")
        yield Input(placeholder="10", id="count")
        yield Button("Generate", id="run")
        yield Log(highlight=True, id="log")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "run":
            return
        modes = self.query_one("#modes", RadioSet)
        selected = "simple"
        for rb in modes.children:  # type: ignore[attr-defined]
            if isinstance(rb, RadioButton) and rb.value:
                selected = rb.label.plain  # type: ignore[attr-defined]
                break
        topic = self.query_one("#topic", Input).value or None
        count_text = self.query_one("#count", Input).value or ""
        n = int(count_text) if count_text.isdigit() else None
        log = self.query_one("#log", Log)
        log.clear()
        try:
            ideas = generate_ideas(selected, topic, n)
            for i, item in enumerate(ideas.ideas, start=1):
                log.write_line(f"{i}. {item.title}: {item.description}")
        except Exception as e:
            info = classify_exception(e)
            log.write_line(format_error_summary(info, e))


