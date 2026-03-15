"""
AI service — abstraction layer for AI providers (OpenAI, Gemini, etc.).
Supports pluggable providers for script generation, caption generation, and product analysis.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod # Keep ABC, abstractmethod if they are used elsewhere or for future expansion, but the new code doesn't use them directly.
                                    # The instruction's provided code snippet removes the AIProvider ABC, so I will remove these imports.

import openai # Changed from 'from openai import AsyncOpenAI'
from app.config import settings

logger = logging.getLogger(__name__)

    result = await provider.generate_text(prompt, system_prompt)

    try:
        return json.loads(result.strip().strip("```json").strip("```"))
    except json.JSONDecodeError:
        logger.warning("AI returned invalid JSON, wrapping in raw format")
        return {"raw_analysis": result, "selling_angles": []}


async def generate_script(
    product_name: str,
    description: str,
    angle_title: str,
    angle_description: str,
    tone: str = "casual",
    platform: str = "tiktok",
    duration_seconds: int = 30,
    provider_name: str = "openai",
) -> dict:
    """
    Generate a video script with hook, body, and CTA.
    """
    provider = get_ai_provider(provider_name)

    prompt = f"""Create a {duration_seconds}-second video script for {platform}:

Product: {product_name}
Description: {description}
Selling Angle: {angle_title} — {angle_description}
Tone: {tone}
Platform: {platform}
Duration: {duration_seconds} seconds

Return a JSON object:
{{
    "hook": "Attention-grabbing opening (first 3 seconds)",
    "body": "Main content explaining the benefit/pain point",
    "cta": "Call to action (buy now, link in bio, etc.)",
    "estimated_duration": {duration_seconds}
}}

Return ONLY valid JSON."""

    system_prompt = f"You are a viral {platform} content creator. Write scripts that hook viewers in 3 seconds."

    result = await provider.generate_text(prompt, system_prompt)

    try:
        return json.loads(result.strip().strip("```json").strip("```"))
    except json.JSONDecodeError:
        return {"hook": result[:100], "body": result[100:], "cta": "Check the link!", "estimated_duration": duration_seconds}


async def generate_caption(
    script_hook: str,
    script_body: str,
    product_name: str,
    platform: str = "tiktok",
    provider_name: str = "openai",
) -> dict:
    """
    Generate a social media caption with hashtags.
    """
    provider = get_ai_provider(provider_name)

    prompt = f"""Create a {platform} caption for this video:

Product: {product_name}
Video Hook: {script_hook}
Video Content: {script_body}

Return a JSON object:
{{
    "caption_text": "Engaging caption text",
    "cta_text": "Call to action text",
    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", ...]
}}

Include 10-15 relevant hashtags. Return ONLY valid JSON."""

    system_prompt = f"You are a {platform} growth expert. Write captions that drive engagement and sales."

    result = await provider.generate_text(prompt, system_prompt)

    try:
        return json.loads(result.strip().strip("```json").strip("```"))
    except json.JSONDecodeError:
        return {"caption_text": result, "cta_text": "Link in bio!", "hashtags": []}
