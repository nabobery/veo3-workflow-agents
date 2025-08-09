"""
Core Nodes for Video Prompt Enhancement

This module implements the core processing nodes for the video prompt enhancer agent.
Each node performs a specific enhancement task using Google Gemini models.
"""

from defusedxml import ElementTree as SafeET
import xml.etree.ElementTree as XET
from typing import Dict, Any, Optional
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging
from functools import lru_cache
from xml.sax.saxutils import escape as xml_escape

from prompt_enhancer_state import VideoPromptState, ConfigSettings
from prompts import (
    CONCEPT_SYSTEM_PROMPT,
    CONCEPT_HUMAN_PROMPT,
    DETAILS_SYSTEM_PROMPT,
    DETAILS_HUMAN_PROMPT,
    JSON_SYSTEM_PROMPT,
    JSON_HUMAN_PROMPT,
    JSON_SYSTEM_PROMPT_STRICT,
    JSON_HUMAN_PROMPT_STRICT,
    XML_SYSTEM_PROMPT,
    XML_HUMAN_PROMPT,
    NATURAL_SYSTEM_PROMPT,
    NATURAL_HUMAN_PROMPT,
)
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedConcept(BaseModel):
    """Structured output for concept enhancement"""
    enhanced_prompt: str
    negative_prompt: str
    enhancement_notes: list[str] = Field(default_factory=list)
    quality_score: float = 0.0


class JSONPromptOutput(BaseModel):
    """Structured output for JSON prompt generation"""
    prompt: str
    negative_prompt: str
    config: Dict[str, Any]


def initialize_llm(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    """Initialize the Google Gemini LLM with optimal settings with error handling."""
    try:
        settings = get_settings()
        return ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GOOGLE_MODEL,
            temperature=temperature,
            max_tokens=2048,
            top_p=0.9,
        )
    except Exception as err:
        logger.exception("Failed to initialize LLM", exc_info=True)
        raise RuntimeError(f"LLM initialization error: {err}") from err


@lru_cache(maxsize=4)
def _get_cached_llm(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    """Return a cached LLM instance to avoid repeated initialization cost."""
    return initialize_llm(temperature=temperature)


def generate_concept(state: VideoPromptState) -> dict:
    """
    First node: Generate an enhanced concept from the original prompt.
    
    This node takes the basic user prompt and creates a conceptually enhanced
    version with better scene description, visual details, and narrative structure.
    
    Args:
        state: Current VideoPromptState
        
    Returns:
        Updated VideoPromptState with enhanced_concept populated
    """
    logger.info("Starting concept generation...")
    
    llm = _get_cached_llm()
    parser = PydanticOutputParser(pydantic_object=EnhancedConcept)
    
    system_prompt = CONCEPT_SYSTEM_PROMPT
    human_prompt = CONCEPT_HUMAN_PROMPT
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    try:
        # Primary attempt(s) with exponential backoff
        last_err: Optional[Exception] = None
        for attempt in range(3):
            try:
                chain = prompt_template | llm | parser
                result = chain.invoke({
                    "original_prompt": state.original_prompt,
                    "format_instructions": parser.get_format_instructions(),
                })
                logger.info("Concept generation completed successfully")
                return {
                    "enhanced_concept": result.enhanced_prompt,
                    "negative_prompt": result.negative_prompt,
                    "enhancement_notes": (state.enhancement_notes + result.enhancement_notes),
                    "enhancement_quality_score": result.quality_score,
                    "current_step": "concept_generated",
                }
            except Exception as inner_err:
                last_err = inner_err
                logger.warning(
                    f"Concept attempt {attempt + 1} failed: {inner_err}",
                    exc_info=True,
                )
                time.sleep(0.5 * (2 ** attempt))

        # Strict retry with lower temperature
        strict_system = (
            system_prompt
            + "\nReturn a JSON object ONLY with keys: enhanced_prompt (string), negative_prompt (string), enhancement_notes (array of strings), quality_score (float between 0 and 1). No prose."
        )
        strict_template = ChatPromptTemplate.from_messages([
            ("system", strict_system),
            ("human", human_prompt + "\nRespond ONLY as JSON."),
        ])
        retry_llm = _get_cached_llm(temperature=0.2)
        retry_chain = strict_template | retry_llm | parser
        result = retry_chain.invoke({
            "original_prompt": state.original_prompt,
            "format_instructions": parser.get_format_instructions(),
        })
        return {
            "enhanced_concept": result.enhanced_prompt,
            "negative_prompt": result.negative_prompt,
            "enhancement_notes": (state.enhancement_notes + result.enhancement_notes),
            "enhancement_quality_score": result.quality_score,
            "current_step": "concept_generated",
        }

    except Exception as e:
        logger.error("Error in concept generation", exc_info=True)
        # Fallback behavior
        return {
            "enhanced_concept": state.original_prompt,
            "negative_prompt": "blurry, low quality, distorted, poor lighting",
            "enhancement_notes": (
                state.enhancement_notes
                + [f"Concept generation failed, using fallback: {str(e)}"]
            ),
            "enhancement_quality_score": 0.5,
            "current_step": "concept_generated_fallback",
        }


def enhance_with_details(state: VideoPromptState) -> dict:
    """
    Second node: Add technical and stylistic details to the enhanced concept.
    
    This node takes the enhanced concept and adds specific technical details,
    camera settings, timing information, and other production-level specifications.
    
    Args:
        state: Current VideoPromptState with enhanced_concept
        
    Returns:
        Updated VideoPromptState with refined enhanced_concept and updated config
    """
    logger.info("Starting detail enhancement...")
    
    llm = _get_cached_llm()
    
    system_prompt = DETAILS_SYSTEM_PROMPT
    human_prompt = DETAILS_HUMAN_PROMPT
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    try:
        # Create the chain
        chain = prompt_template | llm | StrOutputParser()

        # Execute the chain
        detailed_concept = chain.invoke({
            "enhanced_concept": state.enhanced_concept
        })

        # Update configuration with intelligent defaults based on the concept
        new_config = _extract_config_from_concept(detailed_concept, state.config)

        logger.info("Detail enhancement completed successfully")
        return {
            "enhanced_concept": detailed_concept,
            "config": new_config,
            "enhancement_notes": (state.enhancement_notes + ["Added technical and stylistic details"]),
            "current_step": "details_enhanced",
        }

    except Exception as e:
        logger.error("Error in detail enhancement", exc_info=True)
        return {
            "enhancement_notes": (state.enhancement_notes + [f"Detail enhancement failed: {str(e)}"]),
            "current_step": "details_enhanced_fallback",
        }


def generate_json_format(state: VideoPromptState) -> dict:
    """
    Generate JSON-formatted prompt output.
    
    Args:
        state: Current VideoPromptState
        
    Returns:
        Updated VideoPromptState with json_prompt populated
    """
    logger.info("Generating JSON format...")
    
    llm = _get_cached_llm()
    parser = PydanticOutputParser(pydantic_object=JSONPromptOutput)
    
    system_prompt = JSON_SYSTEM_PROMPT
    human_prompt = JSON_HUMAN_PROMPT
    
    try:
        chain = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ]) | llm | parser

        result = chain.invoke({
            "enhanced_concept": state.enhanced_concept,
            "negative_prompt": state.negative_prompt,
            "current_config": state.config.model_dump() if state.config else {},
            "format_instructions": parser.get_format_instructions()
        })

        json_output = {
            "prompt": result.prompt,
            "negative_prompt": result.negative_prompt,
            "config": result.config,
        }

        logger.info("JSON generation completed successfully")
        return {
            "json_prompt": json_output,
        }

    except Exception:
        logger.error("Error in JSON generation", exc_info=True)

        # Retry with stricter instructions and lower temperature
        try:
            strict_template = ChatPromptTemplate.from_messages([
                ("system", JSON_SYSTEM_PROMPT_STRICT),
                ("human", JSON_HUMAN_PROMPT_STRICT),
            ])
            retry_llm = initialize_llm(temperature=0.2)
            retry_chain = strict_template | retry_llm | parser

            last_err: Optional[Exception] = None
            for attempt in range(2):
                try:
                    result = retry_chain.invoke({
                        "enhanced_concept": state.enhanced_concept,
                        "negative_prompt": state.negative_prompt,
                        "current_config": state.config.model_dump() if state.config else {},
                        "format_instructions": parser.get_format_instructions(),
                    })
                    json_output = {
                        "prompt": result.prompt,
                        "negative_prompt": result.negative_prompt,
                        "config": result.config,
                    }
                    return {"json_prompt": json_output}
                except Exception as inner_err:
                    last_err = inner_err
                    logger.warning(
                        f"Strict JSON attempt {attempt + 1} failed: {inner_err}",
                        exc_info=True,
                    )
                    time.sleep(0.5 * (2 ** attempt))

            # Fallback JSON creation
            return {
                "json_prompt": _create_fallback_json(state),
            }
        except Exception:
            logger.error("Retry failed in JSON generation", exc_info=True)
            return {"json_prompt": _create_fallback_json(state)}


def generate_xml_format(state: VideoPromptState) -> dict:
    """
    Generate XML-formatted prompt output deterministically from the current state.

    This avoids relying on LLM output for XML, ensuring well-formed documents.
    """
    logger.info("Generating XML format...")

    try:
        config = state.config or ConfigSettings()

        root = XET.Element("prompt")

        description_el = XET.SubElement(root, "description")
        description_el.text = (state.enhanced_concept or state.original_prompt or "").strip()

        negative_el = XET.SubElement(root, "negative")
        negative_el.text = (state.negative_prompt or "blurry, low quality, distorted").strip()

        camera_attrs = {
            "movement": config.camera.movement,
            "angle": config.camera.angle,
            "lens": config.camera.lens,
        }
        camera_el = XET.SubElement(root, "camera", camera_attrs)
        camera_el.text = "Standard camera setup with natural framing"

        style_attrs = {
            "aesthetic": config.style.aesthetic,
            "rendering": config.style.rendering,
        }
        style_el = XET.SubElement(root, "style", style_attrs)
        style_el.text = "Clean, professional visual style with natural lighting"

        xml_body = XET.tostring(root, encoding="unicode")
        final_xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n{xml_body}"

        # Validate with defusedxml to ensure well-formedness
        SafeET.fromstring(final_xml)

        logger.info("XML generation completed successfully")
        return {"xml_prompt": final_xml}

    except Exception:
        logger.error("Error in XML generation", exc_info=True)
        return {"xml_prompt": _create_fallback_xml(state)}


def generate_natural_language_format(state: VideoPromptState) -> dict:
    """
    Generate enhanced natural language prompt output.
    
    Args:
        state: Current VideoPromptState
        
    Returns:
        Updated VideoPromptState with natural_language_prompt populated
    """
    logger.info("Generating natural language format...")
    
    llm = initialize_llm()
    
    system_prompt = NATURAL_SYSTEM_PROMPT
    human_prompt = NATURAL_HUMAN_PROMPT
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    try:
        chain = prompt_template | llm | StrOutputParser()

        natural_language_output = chain.invoke({
            "enhanced_concept": state.enhanced_concept
        })

        logger.info("Natural language generation completed successfully")
        return {
            "natural_language_prompt": natural_language_output,
        }

    except Exception:
        logger.error("Error in natural language generation", exc_info=True)
        # Fallback to enhanced concept
        return {
            "natural_language_prompt": state.enhanced_concept,
        }


def finalize_results(state: VideoPromptState) -> dict:
    """
    Final node: Validate and finalize all outputs.
    
    Args:
        state: Current VideoPromptState
        
    Returns:
        Final VideoPromptState with validation and completion markers
    """
    logger.info("Finalizing results...")
    
    # Validate that all outputs were generated
    outputs_generated = {
        "json": state.json_prompt is not None,
        "xml": state.xml_prompt is not None,
        "natural_language": state.natural_language_prompt is not None,
    }

    missing_outputs = [k for k, v in outputs_generated.items() if not v]

    notes = list(state.enhancement_notes)
    if outputs_generated["json"]:
        notes.append("Generated JSON format")
    if outputs_generated["xml"]:
        notes.append("Generated XML format")
    if outputs_generated["natural_language"]:
        notes.append("Generated natural language format")
    if missing_outputs:
        notes.append(f"Warning: Missing outputs: {missing_outputs}")

    # Final quality assessment
    final_quality = state.enhancement_quality_score if state.enhancement_quality_score is not None else 0.7
    notes.append("Enhancement process completed")
    notes.append(f"Final quality score: {final_quality}")

    logger.info("Results finalization completed")
    return {
        "enhancement_notes": notes,
        "enhancement_quality_score": final_quality,
        "current_step": "completed",
    }


# Helper functions

def _extract_config_from_concept(concept: str, current_config: ConfigSettings) -> ConfigSettings:
    """Extract configuration hints from the enhanced concept"""
    # Simple keyword-based extraction - could be enhanced with LLM analysis
    config = current_config or ConfigSettings()
    
    concept_lower = concept.lower()
    
    # Extract duration hints
    if "quick" in concept_lower or "brief" in concept_lower:
        config.duration_seconds = 5
    elif "long" in concept_lower or "extended" in concept_lower:
        config.duration_seconds = 12
    
    # Extract camera movement hints
    if "zoom" in concept_lower:
        config.camera.movement = "zoom_in"
    elif "pan" in concept_lower:
        config.camera.movement = "pan"
    elif "static" in concept_lower:
        config.camera.movement = "static"
    
    # Extract style hints
    if "cinematic" in concept_lower:
        config.style.aesthetic = "cinematic"
    elif "documentary" in concept_lower:
        config.style.aesthetic = "documentary"
    elif "commercial" in concept_lower:
        config.style.aesthetic = "commercial"
    
    return config


def _create_fallback_json(state: VideoPromptState) -> Dict[str, Any]:
    """Create a fallback JSON structure"""
    return {
        "prompt": state.enhanced_concept or state.original_prompt,
        "negative_prompt": state.negative_prompt or "blurry, low quality, distorted",
        "config": {
            "duration_seconds": 8,
            "aspect_ratio": "16:9",
            "generate_audio": True,
            "camera": {
                "movement": "static",
                "angle": "medium_shot",
                "lens": "50mm_equivalent"
            },
            "style": {
                "aesthetic": "photorealistic",
                "rendering": "high_quality"
            }
        }
    }


def _create_fallback_xml(state: VideoPromptState) -> str:
    """Create a fallback XML structure with escaped content"""
    desc = xml_escape(state.enhanced_concept or state.original_prompt)
    neg = xml_escape(state.negative_prompt or "blurry, low quality, distorted")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<prompt>
    <description>
        {desc}
    </description>
    
    <negative>
        {neg}
    </negative>
    
    <camera movement="static" angle="medium_shot" lens="50mm">
        Standard camera setup with natural framing
    </camera>
    
    <style aesthetic="photorealistic" rendering="high_quality">
        Clean, professional visual style with natural lighting
    </style>
</prompt>"""


def _clean_xml_output(xml_string: str) -> str:
    """Clean and fix common XML issues"""
    # Remove any text before <?xml declaration
    if "<?xml" in xml_string:
        xml_start = xml_string.find("<?xml")
        xml_string = xml_string[xml_start:]
    
    # Basic cleanup
    xml_string = xml_string.replace("&", "&amp;")
    
    return xml_string