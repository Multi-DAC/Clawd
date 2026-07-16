"""Vision tools — image analysis via Claude Code's native multimodal support."""
import logging
from pathlib import Path

import config

logger = logging.getLogger("clawd.tools.vision")

# Supported image extensions
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}

TOOL_DEFINITIONS = [
    {
        "name": "analyze_image",
        "description": (
            "Analyze an image file. Returns the image path for Claude Code to view "
            "natively with its Read tool. Use this for photos, screenshots, diagrams, "
            "charts, or any visual content. The image must be a file on disk "
            "(use screenshot tool first if needed)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Path to the image file. Can be absolute or relative to CLAWD_HOME. "
                        "Supports: jpg, png, gif, bmp, webp, tiff."
                    ),
                },
                "prompt": {
                    "type": "string",
                    "description": (
                        "What to analyze or ask about the image. "
                        "Default: 'Describe this image in detail.'"
                    ),
                },
            },
            "required": ["path"],
        },
    },
]


async def _analyze_image(input_data: dict) -> str:
    """Resolve image path and return instruction for Claude Code to view it natively."""
    raw_path = input_data["path"]
    prompt = input_data.get("prompt", "Describe this image in detail.")

    # Resolve path — try as-is, then relative to CLAWD_HOME
    image_path = Path(raw_path)
    if not image_path.is_absolute():
        image_path = config.CLAWD_HOME / raw_path
    if not image_path.exists():
        # Also try common locations
        for candidate_dir in [
            config.CLAWD_HOME / "incoming",
            config.CLAWD_HOME / "output",
            config.CLAWD_HOME / "Desktop",
            Path.home() / "Desktop",
        ]:
            candidate = candidate_dir / raw_path
            if candidate.exists():
                image_path = candidate
                break

    if not image_path.exists():
        return f"[Error: Image file not found: {raw_path}]"

    suffix = image_path.suffix.lower()
    if suffix not in _IMAGE_EXTENSIONS:
        return f"[Error: Unsupported image format '{suffix}'. Supported: {', '.join(sorted(_IMAGE_EXTENSIONS))}]"

    file_size_mb = image_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 20:
        return f"[Error: Image too large ({file_size_mb:.1f} MB). Maximum ~20 MB.]"

    logger.info(f"Image analysis requested: {image_path.name} ({file_size_mb:.2f} MB)")

    return (
        f"Image located at: {image_path}\n"
        f"Size: {file_size_mb:.2f} MB\n"
        f"Prompt: {prompt}\n\n"
        f"Use the Read tool to view this image file — Claude Code has native multimodal support."
    )


TOOL_HANDLERS = {
    "analyze_image": _analyze_image,
}
