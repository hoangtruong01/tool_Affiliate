"""
FFmpeg command builder utility for video rendering.
"""
import subprocess
import os
import logging
from typing import List, Optional
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)


def escape_drawtext(text: str) -> str:
    """Escape special characters for FFmpeg drawtext filter."""
    # FFmpeg drawtext requires escaping: \ ' : !
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace(":", "\\:")
    text = text.replace("!", "\\!")
    return text



@dataclass
class RenderConfig:
    """Configuration for an FFmpeg render job."""
    output_path: str
    width: int = 1080
    height: int = 1920  # 9:16 portrait for TikTok/Shorts
    fps: int = 30
    duration: int = 30
    background_color: str = "black"
    font_path: Optional[str] = None
    font_size: int = 48
    font_color: str = "white"


def build_slideshow_command(
    image_paths: List[str],
    audio_path: Optional[str],
    text_overlay: Optional[str],
    config: RenderConfig,
) -> List[str]:
    """
    Build an FFmpeg command for creating a slideshow video from images.

    Args:
        image_paths: List of image file paths to use as slides
        audio_path: Optional background audio track
        text_overlay: Optional text to overlay on the video
        config: Render configuration (resolution, fps, etc.)

    Returns:
        FFmpeg command as a list of arguments
    """
    cmd = [settings.FFMPEG_PATH, "-y"]  # -y = overwrite output

    # Calculate duration per image
    duration_per_image = max(config.duration // len(image_paths), 2) if image_paths else config.duration

    # Input images as concat
    if image_paths:
        for img in image_paths:
            cmd.extend(["-loop", "1", "-t", str(duration_per_image), "-i", img])
    else:
        # Blank color background
        cmd.extend([
            "-f", "lavfi",
            "-i", f"color=c={config.background_color}:s={config.width}x{config.height}:d={config.duration}",
        ])

    # Audio input
    if audio_path:
        cmd.extend(["-i", audio_path])

    # Filter complex for concatenating images
    if image_paths and len(image_paths) > 1:
        filter_parts = []
        for i in range(len(image_paths)):
            filter_parts.append(
                f"[{i}:v]scale={config.width}:{config.height}:force_original_aspect_ratio=decrease,"
                f"pad={config.width}:{config.height}:(ow-iw)/2:(oh-ih)/2:color={config.background_color},"
                f"setsar=1[v{i}]"
            )
        concat_inputs = "".join(f"[v{i}]" for i in range(len(image_paths)))
        filter_parts.append(f"{concat_inputs}concat=n={len(image_paths)}:v=1:a=0[outv]")

        # Text overlay
        if text_overlay:
            filter_parts.append(
                f"[outv]drawtext=text='{escape_drawtext(text_overlay)}':"
                f"fontsize={config.font_size}:fontcolor={config.font_color}:"
                f"x=(w-text_w)/2:y=h-100:enable='between(t,0,5)'[final]"
            )
            map_label = "[final]"
        else:
            map_label = "[outv]"

        cmd.extend(["-filter_complex", ";".join(filter_parts)])
        cmd.extend(["-map", map_label])
    elif image_paths:
        # Single image
        filter_str = f"scale={config.width}:{config.height}:force_original_aspect_ratio=decrease,pad={config.width}:{config.height}:(ow-iw)/2:(oh-ih)/2"
        if text_overlay:
            filter_str += (
                f",drawtext=text='{escape_drawtext(text_overlay)}':"
                f"fontsize={config.font_size}:fontcolor={config.font_color}:"
                f"x=(w-text_w)/2:y=h-100"
            )
        cmd.extend(["-vf", filter_str])

    # Audio mapping
    if audio_path:
        audio_idx = len(image_paths) if image_paths else 1
        cmd.extend(["-map", f"{audio_idx}:a", "-shortest"])

    # Output settings
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-r", str(config.fps),
        "-t", str(config.duration),
        config.output_path,
    ])

    return cmd


def run_ffmpeg(cmd: List[str]) -> tuple[bool, str]:
    """
    Execute an FFmpeg command.

    Returns:
        Tuple of (success: bool, output/error message: str)
    """
    logger.info(f"Running FFmpeg: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 min max
        )
        if result.returncode == 0:
            logger.info("FFmpeg render completed successfully")
            return True, result.stdout
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg render timed out after 600s")
        return False, "Render timed out after 600 seconds"
    except Exception as e:
        logger.error(f"FFmpeg exception: {str(e)}")
        return False, str(e)
