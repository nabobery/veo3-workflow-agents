from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, AnyUrl


class VideoPromptIdea(BaseModel):
    """Structured representation of a single video prompt idea."""

    title: str = Field(..., min_length=3, max_length=200, description="Short, catchy title for the idea")
    description: str = Field(..., min_length=30, max_length=2000, description="2-4 sentence description of the video prompt")
    sources: list[AnyUrl] = Field(default_factory=list, description="Evidence or inspiration links (URLs as strings)")
    trend_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Estimated virality/trend score (0-1). Only set in viral mode.",
    )


class IdeaList(BaseModel):
    """Container for multiple video prompt ideas."""

    ideas: list[VideoPromptIdea]


