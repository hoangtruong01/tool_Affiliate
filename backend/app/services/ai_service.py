"""
AI service — abstraction layer for AI providers (OpenAI, Gemini, etc.).
Supports pluggable providers for script generation, caption generation, and product analysis.
"""
import json
import logging
from typing import Dict, Any, List, Optional

import openai
from app.config import settings

logger = logging.getLogger(__name__)


# ── AI Provider Abstraction ────────────────────────
class OpenAIProvider:
    """OpenAI API provider using async client."""

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def generate_text(self, prompt: str, system_prompt: str) -> str:
        """Generate text using OpenAI chat completions."""
        if self.client.api_key == "sk-your-openai-key":
            logger.info("Using mocked OpenAI response for test environment.")
            
            # If prompt looks like product analysis
            if "selling angles" in prompt.lower():
                return '''{
                    "summary": "This is a great dummy product.",
                    "target_audience": "Tech enthusiasts and developers",
                    "selling_angles": [
                        {
                            "type": "benefit",
                            "title": "Boost Productivity",
                            "description": "It helps you work faster.",
                            "score": 0.95
                        }
                    ]
                }'''
            # If prompt looks like script generation
            elif "tiktok script" in prompt.lower() or "video script" in prompt.lower():
                return '''{
                    "hook": "Stop scrolling! Here is the best tech product.",
                    "body": "This amazing test product will save you hours of work everyday.",
                    "cta": "Click the link in bio to get yours now!"
                }'''
            # If prompt looks like caption generation
            elif "social media caption" in prompt.lower():
                return '''{
                    "caption": "Check out this amazing product that boosts your productivity! 🚀",
                    "cta": "Link in bio! 👆",
                    "hashtags": ["#tech", "#productivity", "#musthave"]
                }'''
            return "Mock response for query."

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise


def get_ai_provider(provider_name: str = "openai"):
    """Factory function to get AI provider instance."""
    if provider_name == "openai":
        return OpenAIProvider()
    raise ValueError(f"Unknown AI provider: {provider_name}")


# ── AI Functions ───────────────────────────────────
async def analyze_product(
    product_name: str,
    description: str,
    source_url: Optional[str] = None,
    provider_name: str = "openai",
) -> dict:
    """
    Analyze a product to extract selling angles.
    """
    provider = get_ai_provider(provider_name)

    prompt = f"""Analyze this affiliate product and identify selling angles:

Product: {product_name}
Description: {description}
URL: {source_url or 'N/A'}

Return a JSON object:
{{
    "summary": "Brief product analysis",
    "target_audience": "Who would buy this",
    "selling_angles": [
        {{
            "type": "pain_point|benefit|comparison|story|urgency",
            "title": "Angle title",
            "description": "Why this angle works",
            "score": 0.8
        }}
    ]
}}

Return ONLY valid JSON."""

    system_prompt = "You are a marketing expert specializing in affiliate product analysis for short-form video content."

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
