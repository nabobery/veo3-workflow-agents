#!/usr/bin/env python3
"""
Demo script showcasing Veo3 integration with AI-enhanced prompts.

This script demonstrates the complete workflow:
1. Generate creative prompt variations using pydantic_ai_agents
2. Enhance prompts with technical details using langraph_agents  
3. Generate videos using Veo3 Fast API

Usage:
    python notebook_demo.py "A cat playing with a ball of yarn"
    python notebook_demo.py "Sunset over mountains" --duration 6 --aspect-ratio "9:16"
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
# Guard against duplicate insertions
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
logger = logging.getLogger(__name__)


def generate_and_enhance_prompts(user_prompt: str, num_ideas: int = 3) -> List[Dict[str, Any]]:
    """
    Generate multiple prompt variations for a user prompt and enhance each with technical details.
    
    Given a user-provided prompt, this function uses an agent pipeline to:
    - produce up to `num_ideas` initial prompt variations, and
    - enhance each variation into a production-ready prompt with structured technical details and a quality score.
    
    Returns a list of dictionaries (one per idea) with the following keys:
    - index (int): 1-based position in the returned list.
    - title (str): short title for the idea.
    - original (str): the original generated idea description.
    - enhanced (str): the enhanced natural-language prompt (falls back to `original` on enhancement failure).
    - technical_details (dict): structured technical data for video generation (may be empty on failure).
    - quality_score (float): numeric quality score produced by the enhancer (defaults to 0.5 on enhancement failure).
    - saved_dir (str): any path returned by the enhancer for auxiliary files (may be empty).
    
    Behavior notes:
    - If no initial ideas are generated or an unexpected error occurs during the overall process, the function returns an empty list.
    - Enhancement failures for individual ideas are handled per-item by falling back to the original description and a default quality_score of 0.5.
    """
    logger.info("🎭 Generating %s enhanced prompts for: '%s'", num_ideas, user_prompt)
    
    try:
        # Import and use pydantic agents
        from pydantic_ai_agents import agents as pydantic_agents
        logger.info("📝 Generating initial prompt variations...")
        
        result = pydantic_agents.generate_variations_for_topic(
            topic=user_prompt,
            num_ideas=num_ideas
        )
        
        if not result.ideas:
            logger.warning("❌ No ideas generated")
            return []
        
        logger.info("✅ Generated %s initial ideas", len(result.ideas))
        
        # Import and use langraph enhancement
        from langraph_agents.prompt_enhancer_graph import enhance_video_prompt
        
        enhanced_prompts = []
        for i, idea in enumerate(result.ideas, 1):
            logger.info("⚡ Enhancing idea %s/%s: %s", i, len(result.ideas), idea.title)
            
            try:
                enhancement_result = enhance_video_prompt(idea.description)
                
                enhanced_prompt = {
                    "title": idea.title,
                    "original": idea.description,
                    "enhanced": enhancement_result.get("natural_language_prompt", idea.description),
                    "technical_details": enhancement_result.get("json_prompt", {}),
                    "quality_score": enhancement_result.get("quality_score", 0.0),
                    "saved_dir": enhancement_result.get("saved_dir", ""),
                    "index": i
                }
                
                enhanced_prompts.append(enhanced_prompt)
                logger.info("   ✅ Enhanced (quality: %.2f)", enhanced_prompt['quality_score'])
                
            except Exception as e:
                logger.warning("   ❌ Enhancement failed: %s", e, exc_info=True)
                # Fallback to original
                enhanced_prompts.append({
                    "title": idea.title,
                    "original": idea.description,
                    "enhanced": idea.description,
                    "technical_details": {},
                    "quality_score": 0.5,
                    "saved_dir": "",
                    "index": i
                })
        
        return enhanced_prompts
        
    except Exception as e:
        logger.error("❌ Prompt generation failed: %s", e, exc_info=True)
        return []


def select_best_prompt(enhanced_prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Select the highest-quality enhanced prompt from a list.
    
    If `enhanced_prompts` is empty returns None. Otherwise, picks the prompt with the highest
    `quality_score`, prints a brief summary (title, quality score, preview of the enhanced text,
    and saved directory if present) to stdout, and returns the selected prompt dictionary.
    
    Returns:
        The prompt dictionary with the highest `quality_score`, or `None` if no prompts were provided.
    """
    if not enhanced_prompts:
        return None
    
    # Sort by quality score, descending
    sorted_prompts = sorted(enhanced_prompts, key=lambda x: x["quality_score"], reverse=True)
    best_prompt = sorted_prompts[0]
    
    logger.info("\n" + "="*60)
    logger.info("🏆 SELECTED BEST PROMPT")
    logger.info("="*60)
    logger.info("Title: %s", best_prompt['title'])
    logger.info("Quality Score: %.2f", best_prompt['quality_score'])
    logger.info("Enhanced Prompt: %s...", best_prompt['enhanced'][:200])
    if best_prompt["saved_dir"]:
        logger.info("Details saved to: %s", best_prompt['saved_dir'])
    logger.info("="*60)
    
    return best_prompt


def generate_video(
    prompt: str,
    duration_seconds: int = 8,
    aspect_ratio: str = "16:9",
    resolution: str = "1080p",
    generate_audio: bool = True,
    save_video: bool = True,
) -> Dict[str, Any]:
    """
    Generate a video from a natural-language prompt using the Veo3 API.
    
    Creates a Veo3 client via the module's configuration, starts a generation operation, polls until completion (5‑minute timeout), and attempts to retrieve the produced video bytes. If retrieval succeeds the function returns a result dict describing the generated video and metadata; on any failure it returns a dict with "success": False and an "error" string.
    
    Parameters:
        prompt (str): Natural-language prompt describing the desired video.
        duration_seconds (int): Target video duration in seconds.
        aspect_ratio (str): Aspect ratio string (e.g., "16:9", "9:16").
        resolution (str): Target resolution label (e.g., "1080p").
        generate_audio (bool): Whether to request audio generation when supported by the model (default: True).
        save_video (bool): If True, the final video bytes are written to a timestamped .mp4 file and the filename is included in the returned dict.
    
    Returns:
        dict: On success:
            {
                "success": True,
                "video_bytes": bytes,         # raw MP4 bytes
                "operation_id": str,         # Veo3 operation identifier
                "generation_time": float,    # seconds elapsed during generation
                "config": {                  # echo of generation settings
                    "duration_seconds": int,
                    "aspect_ratio": str,
                    "resolution": str
                },
                "filename": str (optional)   # present when save_video is True
            }
            On failure:
            {
                "success": False,
                "error": str                # human-readable error message
            }
    """
    logger.info("\n🎬 Starting video generation...")
    logger.info("Prompt: %s...", prompt[:100])
    logger.info("Settings: %ss, %s, %s", duration_seconds, aspect_ratio, resolution)
    logger.debug("Note: Depending on model support, duration/resolution may be ignored by the API.")
    
    try:
        # Import streamlined Veo3 configuration
        from veo3_config import get_client_manager
        
        # Get client manager
        client_manager = get_client_manager()
        client = client_manager.get_genai_client()
        
        # Create video generation config
        video_config = client_manager.get_video_generation_config(
            duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            generate_audio=generate_audio,
        )
        
        logger.info("🚀 Calling Veo3 API with model: %s", client_manager.config.VEO3_MODEL)
        logger.info("🔑 Using streamlined configuration (no Vertex AI required)")
        
        # Generate video
        operation = client.models.generate_videos(
            model=client_manager.config.VEO3_MODEL,
            prompt=prompt,
            config=video_config,
        )
        
        logger.info("⏳ Video generation started. Operation ID: %s", operation.name)
        logger.info("⏱️  This typically takes 30-90 seconds...")
        
        # Poll for completion
        start_time = time.time()
        while not operation.done:
            elapsed = time.time() - start_time
            logger.debug("⏳ Generating... %.0f s elapsed", elapsed)
            if elapsed > 300:
                raise TimeoutError("Video generation timed out after 5 minutes")
            time.sleep(10)
            operation = client.operations.get(operation)
        
        # ----- Success path: use operation.result -----
        result_payload = getattr(operation, "result", None)
        if not result_payload or not getattr(result_payload, "generated_videos", None):
            raise RuntimeError("Video generation completed, but result payload is empty or malformed.")

        video_data = result_payload.generated_videos[0]
        generation_time = time.time() - start_time

        # Preferred: download returns raw bytes and populates video.video_bytes
        try:
            video_bytes = client.files.download(file=video_data.video)
        except Exception as e:
            logger.warning("⚠️ Download failed: %s. Trying inline bytes fallback.", e, exc_info=True)
            video_bytes = getattr(getattr(video_data, "video", object()), "video_bytes", None)

        if not video_bytes:
            raise RuntimeError("Video generation completed, but failed to retrieve video bytes.")

        result = {
            "success": True,
            "video_bytes": video_bytes,
            "operation_id": operation.name,
            "generation_time": generation_time,
            "config": {
                "duration_seconds": duration_seconds,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "generate_audio": generate_audio,
            },
        }

        logger.info("✅ Video generated successfully in %.1f s", generation_time)

        if save_video:
            timestamp = int(time.time())
            filename = f"generated_video_{timestamp}.mp4"
            with open(filename, "wb") as f:
                f.write(video_bytes)
            result["filename"] = filename
            logger.info("💾 Video saved as: %s", filename)

        return result
    
    except Exception as e:
        logger.error("❌ Video generation failed: %s", e, exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """
    Run the CLI demo that generates AI-enhanced prompts and optionally creates a video via Veo3.
    
    Parses command-line arguments (prompt, --duration, --aspect-ratio, --no-audio, --num-ideas, --enhance-only), executes the three-step demo pipeline:
    1. Generate and enhance prompt variations.
    2. Select the best enhanced prompt.
    3. Generate a video from the selected prompt (skipped if --enhance-only).
    
    Returns:
        int: Exit code (0 on success, 1 on failure). Failures include inability to produce enhanced prompts or video-generation errors.
    """
    parser = argparse.ArgumentParser(
        description="Demo Veo3 video generation with AI-enhanced prompts"
    )
    parser.add_argument(
        "prompt", 
        help="Your video prompt (e.g., 'A cat playing with a ball of yarn')"
    )
    parser.add_argument(
        "--duration", 
        type=int, 
        default=8,
        help="Video duration in seconds (4-12, default: 8)"
    )
    parser.add_argument(
        "--aspect-ratio", 
        default="16:9",
        choices=["16:9", "9:16", "1:1"],
        help="Video aspect ratio (default: 16:9)"
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio generation (requires SDK/model support)"
    )
    parser.add_argument(
        "--num-ideas", 
        type=int, 
        default=3,
        help="Number of prompt variations to generate (default: 3)"
    )
    parser.add_argument(
        "--enhance-only", 
        action="store_true",
        help="Only generate and enhance prompts, don't create video"
    )
    
    args = parser.parse_args()
    
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    logger.info("🎬 Veo3 Video Generation Demo")
    logger.info("=" * 50)
    
    # Step 1: Generate and enhance prompts
    enhanced_prompts = generate_and_enhance_prompts(args.prompt, args.num_ideas)
    
    if not enhanced_prompts:
        logger.error("❌ Failed to generate enhanced prompts")
        return 1
    
    # Display all generated prompts
    logger.info("\n📝 All Enhanced Prompts:")
    for prompt_data in enhanced_prompts:
        logger.info("\n%s. %s", prompt_data['index'], prompt_data['title'])
        logger.info("   Quality: %.2f", prompt_data['quality_score'])
        logger.info("   Enhanced: %s...", prompt_data['enhanced'][:150])
    
    # Step 2: Select best prompt
    best_prompt = select_best_prompt(enhanced_prompts)
    if not best_prompt:
        logger.error("❌ No selectable prompt returned")
        return 1
    
    if args.enhance_only:
        logger.info("\n✅ Prompt enhancement complete!")
        logger.info("💡 Run without --enhance-only to generate video")
        return 0
    
    # Step 3: Generate video
    logger.info("\n" + "="*60)
    logger.info("🎬 GENERATING VIDEO")
    logger.info("="*60)
    
    video_result = generate_video(
        prompt=best_prompt["enhanced"],
        duration_seconds=args.duration,
        aspect_ratio=args.aspect_ratio,
        generate_audio=(not args.no_audio),
    )
    
    if video_result["success"]:
        logger.info("\n🎉 SUCCESS! Video generated successfully!")
        logger.info("⏱️  Total time: %.1f s", video_result['generation_time'])
        if "filename" in video_result:
            logger.info("📁 File: %s", video_result['filename'])
        logger.info("\n💡 You can now play the video file or upload it to your platform!")
        return 0
    else:
        logger.error("\n❌ Video generation failed: %s", video_result['error'])
        return 1


if __name__ == "__main__":
    sys.exit(main())