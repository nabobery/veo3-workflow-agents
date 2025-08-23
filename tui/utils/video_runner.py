from __future__ import annotations

from typing import Callable, Dict, Any
import time

from notebook_demo import generate_video as nb_generate_video


def generate_video_with_progress(prompt: str, progress_callback: Callable[[str], None]) -> Dict[str, Any]:
    if not prompt or not prompt.strip():
        return {"success": False, "error": "Prompt is required"}
    progress_callback("Validating configuration...")
    try:
        start = time.time()
        result = nb_generate_video(prompt, save_video=True)
        if result.get("success"):
            progress_callback("Video generation complete.")
        else:
            progress_callback("Video generation failed.")
        result["generation_time"] = time.time() - start
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


