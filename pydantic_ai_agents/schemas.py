from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class VideoPromptIdea(BaseModel):
    """Structured representation of a single video prompt idea."""

    title: str = Field(..., description="Short, catchy title for the idea")
    description: str = Field(..., description="2-4 sentence description of the video prompt")
    sources: List[str] = Field(default_factory=list, description="Evidence or inspiration links (URLs as strings)")
    trend_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Estimated virality/trend score (0-1). Only set in viral mode.",
    )


class IdeaList(BaseModel):
    """Container for multiple video prompt ideas."""

    ideas: List[VideoPromptIdea]


