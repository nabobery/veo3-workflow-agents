from __future__ import annotations

import time
from textual.screen import Screen
from textual.widgets import Static, Input, Button, Log
from textual.app import ComposeResult

from ..utils.video_runner import generate_video_with_progress
from ..utils.error_handler import classify_exception, format_error_summary


class VideoGenerationScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Veo3 Video Generation")
        yield Input(placeholder="Enter the final prompt to generate a video", id="prompt")
        yield Button("Generate Video", id="run")
        yield Log(highlight=True, id="log")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "run":
            return
        prompt = self.query_one("#prompt", Input).value or ""
        log = self.query_one("#log", Log)
        log.clear()

        def progress(msg: str) -> None:
            log.write_line(msg)

        try:
            start = time.time()
            result = generate_video_with_progress(prompt, progress)
            if result["success"]:
                elapsed = time.time() - start
                log.write_line(f"Success in {elapsed:.1f}s. Saved file: {result.get('filename','<temp>')}")
            else:
                info = classify_exception(result.get("error", ""))
                log.write_line(format_error_summary(info, result.get("error", "Unknown error")))
        except Exception as e:
            info = classify_exception(e)
            log.write_line(format_error_summary(info, e))


